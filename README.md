# USING LLM FOR FEATURE EXTRACTION ON UNSTRUCTURED DATA THROUGH SLACK

## 1. Project Overview
This is a simple project to use an LLM to parse unstructured data, in this case, email messages to extract key information from them. The LLM is pre-prompted and served to the Sales Development Representatives (SDR) through a Slack App to perform the feature extraction.

## 2. Use Case
The client is a broker for retail cleaning jobs and they use an internally developed platform to manage their leads and sales. As they begin to scale their business, their SDR's time is increasingly being taken up to process and extract specific key information in new job bid emails that need to be entered into the internal platform. As email messages are unstructured data and come in different formats from different vendors, implementing a traditional rule-based approach to extract the desired information would require the rules to be constantly adjusted manually to achieve a satisfactory level of accuracy. Instead, the capabilities of a generative LLM to perform the extraction was used due to its ability to process unstructured data unsupervised and achieve excellent accuracy.

## Tech Used
1. Ollama (Llama3 model) - LLM model to perform feature extraction
2. LangChain - Chaining LLM conversation
3. Slack Bolt SDK - Interfacing with Slack API
5. Python - Scripting

## Implementation
As the client has a small number of SDRs and to minimize the cost of this project from Cloud infrastructure costs, the project was implemented locally on a local machine remotely. First the Slack App will need to be created and configured in asynchronous SocketMode. The configuration of the Slack App used for this project is in the Slack App manifest in this repo.

The Ollama application was installed on the machine serving the Python script and the Llama3 model image was pulled.

The pre-prompt to the LLM was designed to get the LLM to extract the specific features required by the client in an email message. The Python scripts were developed to present the parsed information back to the user in Slack. During the user's session with the LLM, the user can fine-tune the LLM's response by prompting the LLM to update features that are captured wrongly. Slack Commands were also configured in this project that will allow the user to start a new session with the LLM, push the final response with the correct features extracted to a batch file, or check the messages queued in the batch file.

## Project outcomes
Actual accuracy: 94%
Manual email processing (end to end): About 7 minutes per email
With automation (this project): About 1 minute per email
Average daily volume of emails to process: 20
Average time to process manually: 140 minutes per day
Average time to process with automation: 20 minutes per day
Time savings: 86%
