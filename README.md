# USING LLM FOR FEATURE EXTRACTION ON UNSTRUCTURED DATA THROUGH SLACK
## 0. File Organization
llm_prompt.py - LangChain setup and pre-prompt message for the LLM in this file
slack_llm.py - Slack interactivity integration code in this file
manifest.json - Slack App configuration parameters

## 1. Project Overview
This project focuses on building a robust solution to parse unstructured data—specifically, email messages—and efficiently return structured information to users. By leveraging a Large Language Model (LLM), the extraction of key information was automated and integrated into a Slack App, empowering Sales Development Representatives (SDRs) to streamline their workflow and reduce manual effort.

## 2. Use Case
The client, a broker specializing in retail cleaning services, operates an internal platform for managing leads and sales. As their business scaled, their SDRs were increasingly bogged down by the need to manually extract key details from bid emails—each arriving in a different, unstructured format. Implementing a rule-based extraction system would have required constant manual updates to maintain accuracy. Instead, a cutting-edge LLM approach that adapts to the varied email formats was adopted, autonomously processing the data with high precision. The result was a scalable, adaptable solution that eliminated the need for continuous manual intervention.

## Tech Used
1. Ollama (Llama3 model) - LLM for feature extraction
2. LangChain - Framework for chaining LLM conversation
3. Slack Bolt SDK - Interfacing with the Slack API
5. Python - Scripting and automation

## Implementation
To keep infrastructure costs low for the client’s small team, the solution was deployed on a local machine rather than relying on cloud services. The Slack App was set up using asynchronous SocketMode, and the Llama3 model was deployed locally using Ollama.

The LLM was pre-prompted to extract the specific features needed from the client’s bid emails. Python scripts were written to deliver the extracted data directly through Slack. During interaction, users could refine the LLM’s output, correcting any inaccuracies in real time. Additionally, Slack Commands were incorporated to allow users to start new LLM sessions, push final data to a batch file, and review pending messages.

## Project outcomes
| **Metric**                          | **Before Automation** | **After Automation** | **Improvement** |
|-------------------------------------|-----------------------|----------------------|-----------------|
| Accuracy                            | N/A                   | 94%                  | N/A             |
| Processing Time per Email           | 7 minutes             | 1 minute             | 6 minutes saved |
| Average Daily Email Volume          | 20 emails             | 20 emails            | N/A             |
| Total Processing Time per Day       | 140 minutes           | 20 minutes           | 86% time saved  |

## Project Challenges & Learnings
One of the main challenges was designing an effective pre-prompt to guide the LLM toward consistent, accurate feature extraction. Through an iterative process, the pre-prompt was refined by combining few-shot learning and chain-of-thought prompting techniques. This approach significantly improved the model’s ability to deliver reliable results, even with varied email structures.

## Project Expansion
As the client continues to scale and increase their SDR team, transitioning this solution to the cloud will enable 24/7 availability and support a larger user base, ensuring seamless scalability and enhanced efficiency.
