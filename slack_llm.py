import warnings
import re
import datetime as dt
import os
import pandas as pd
import numpy as np
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from llm_prompt import *

# Suppress warnings
warnings.filterwarnings("ignore")

# Grab Slack tokens from local environment
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

# Initialize app
app = App(token=SLACK_BOT_TOKEN)
current_response = None


@app.command("/new")
async def parse_new(ack, say):
    """
    This Slack slash command will reset the LLM's session. All previous
    conversation and context will be removed.
    """
    await ack()  # Acknowledge the command
    response = reset_conversation()
    await say(response)


@app.command("/add-queue")
async def push_to_queue(ack, say):
    """
    This Slack slash command will add a response from the LLM after the
    request message has been parsed. If the file that stores the requests
    in a queue is empty, it will create the file. Otherwise it will just
    append new completed parsed request entries to the queue file.

    The queue file will be ingested by the platform to create new tickets based
    on the entries in the queue file. The ingestion logic, and subsequent
    ticket creation logic will be taken care in the platform.

    This function will display the contents of the request queue file at the
    end of this workflow.
    """
    # Acknowledge the command
    await ack()

    # Check if clean queue batch file exists, if not create a blank one
    if not os.path.exists("clean_queue.csv"):
        with open("clean_queue.csv", "w", encoding="utf-8") as file:
            headers = [
                "date_added_to_queue",
                "project_name",
                "sqft",
                "supervisor",
                "supervisor_contact",
                "project_start",
                "cleans",
                "touchups",
                "project_requirements"
                ]
            file.write(','.join(headers) + '\n')

    # Process current response from the LLM and add to the queue
    if current_response:
        with open("pushed_response.txt", "w", encoding="utf-8") as file:
            file.write(current_response)

        # Load current job queue file
        curr_job_queue = pd.read_csv("clean_queue.csv")

        # Parse the LLM response to be added to the current job queue
        proc_string = current_response.split("\n")
        proc_string = [i for i in proc_string if len(i) > 0]
        new = []
        for i in proc_string:
            new.append(i.split(":"))

        # Split the string into information pieces, the tail end will be
        # assumed to be the clean requirements which should be processed and
        # stored as a list and appended back to the main list
        new1 = new[0:7]
        req = new[8:]

        new1 = [i[1].strip() for i in new1]
        new1 = [None if "None" in i else i for i in new1]
        new1 = [
            int(i.split()[0]) if isinstance(i, str) and "sqft" in i else i
            for i in new1
        ]

        # Check if the cleaning requirement is in bullet point format or not
        if not req:
            req = new[7]
            req = req[1].split(",")
            req = [i.strip() for i in req]
            new1 = [dt.datetime.today().date()] + new1 + [req]
        else:
            req = [re.sub(r'\t• |• |\t\* |\* ', '', i[0]) for i in req]
            new1 = [dt.datetime.today().date()] + new1 + [req]

        new1 = pd.DataFrame(
            [new1],
            columns=[
                "date_added_to_queue",
                "project_name",
                "sqft",
                "supervisor",
                "supervisor_contact",
                "project_start",
                "cleans",
                "touchups",
                "project_requirements"
                ])

        # Append data to the job queue file
        curr_job_queue = pd.concat([curr_job_queue, new1], axis=0)

        # Save the appended file to the local folder
        curr_job_queue["date_added_to_queue"] = pd.to_datetime(
            curr_job_queue["date_added_to_queue"]
        )
        curr_job_queue.sort_values(["date_added_to_queue"])
        curr_job_queue.to_csv("clean_queue.csv", index=False)
        await say("Requst pushed to the queue successfully! :rocket:")

        # Print the current snapshot of the queue file
        display_jobs = curr_job_queue[[
            "date_added_to_queue",
            "project_name",
            "sqft",
            "project_start"
        ]]
        display_jobs.columns = ["Date Added", "Project", "SQFT", "Start Date"]
        display_jobs["Date Added"] = display_jobs["Date Added"]\
            .apply(lambda x: x.strftime("%m/%d/%Y"))
        display_jobs_str = display_jobs.to_string(index=False)
        await say(f":warning: Here is a summary of the current queue:"
            f"\n``` {display_jobs_str}\n```")

        # Call the parse new function to reset the LLM's memory and start new
        parse_new(ack, say)
    else:
        await say("No response from the LLM yet.")


@app.command("/queue")
async def check_queue_status(ack, say):
    """
    This function will get the contents on the current available request
    queue file and display it to the user.
    """
    # Acknowledge the command
    await ack()

    # Check if request queue file exists, if not, tell user it does not exist
    if os.path.exists("clean_queue.csv"):
        # Load current job queue file
        curr_job_queue = pd.read_csv("clean_queue.csv")
        curr_job_queue["date_added_to_queue"] = pd.to_datetime(
            curr_job_queue["date_added_to_queue"]
        )

        # Print the current snapshot of the queue file
        display_jobs = curr_job_queue[[
            "date_added_to_queue",
            "project_name",
            "sqft",
            "project_start"
            ]]
        display_jobs.columns = ["Date Added", "Project", "SQFT", "Start Date"]
        display_jobs["Date Added"] = display_jobs["Date Added"]\
            .apply(lambda x: x.strftime("%m/%d/%Y"))
        display_jobs_str = display_jobs.to_string(index=False)
        await say(f":warning: Here are the request(s) in the queue:"
            f"\n``` {display_jobs_str}\n```")
    else:
        await say("There are no requests queued up yet. Please create one first "
            "by adding a request to a queue using the */add-queue* command")


@app.event("app_mention")
async def mention_handler(say, ack):
    """
    This event handler functions to only let the user know what are the available
    Slash commands to be used during the session.
    """
    # Acknowledge message
    await ack()

    response = """
    Hi there, here are the available commands you can use on me:\n
    :pushpin:  */new* - Start a new session with me
    :pushpin:  */queue* - Check current queue status
    :pushpin:  */add-queue* - Add the completed message request to the queue

    Send me your clean request message and I'll try my best to extract the
    important information for you.
    """

    # say("You mentioned me, how can I help?")
    await say(response)


@app.event("message")
async def keyword_responder(body, say, ack):
    """
    This function will listen for a message input posted on a private Slack
    channel where the Slack Bot is in.

    It will return a acknowledgement message to make the interaction with
    the user more natural. The function will pass the message to the LLM with
    through the sub-function personal_assistant.

    The sub-function personal_assistant will return a parsed message with the
    7 categories back to the user in the same private Slack channel.

    During this session, the user is able to fine tune the request by
    interacting with the LLM until the /add-queue or /new slash command is
    invoked in which both commands will reset the LLM's memory to begin a new
    session with the user to work on parsing a new request.
    """
    # Initialize global variable to manipulate the LLM's response from the 
    # other function call
    global current_response

    # Acknowledge message
    await ack()

    # Add a acknowledgement message to make the bot sound more natural
    phrases = [
        "I’m working on it right now.",
        "Handling it as we speak.",
        "Working on it, please hold tight.",
        "I’m on it, just a moment.",
        "In progress, hang tight.",
        "I’m getting it done for you.",
        "Taking care of it now.",
        "Currently working on it, please wait.",
        "I’m on it, hold on a second.",
        "It’s being handled as we speak.",
        "I’m on it right now, just a second.",
        "Working on that for you now.",
        "Taking care of it, please hold on.",
        "In progress, just a moment.",
        "I’m handling that, one moment please.",
        "Working on it, I’ll be right back.",
        "I’m getting that sorted out now.",
        "I’m taking care of it, please wait.",
        "Currently handling it, hang tight.",
        "Working on it, please give me a moment."
    ]
    await say(np.random.choice(phrases))

    text = body["event"]["text"]
    response = project_assistant(text)
    await say(response)

    # Write response to a temp file on local machine
    with open("response.log", "a", encoding="utf-8") as file:
        file.write(f"Input: {text}\n")
        file.write(f"Response: {response}")
        file.write("\n")

    # Store response to global object
    current_response = response


if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()