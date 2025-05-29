# Multi_agent_system
Build a multi-agent AI system that accepts input in PDF, JSON, or Email (text) format, classifies the format and intent, and routes it to the appropriate agent. The system must maintain shared context (e.g., sender, topic, last extracted fields) to enable chaining and traceability.
Multi-Agent AI System
This project implements a multi-agent AI system designed to intelligently process and route various types of incoming information. It leverages Large Language Models (LLMs) for classification and data extraction, demonstrating a flexible and extensible architecture for handling diverse inputs like emails and structured data (JSON).

# Features
Intelligent Classification: Uses an LLM (Google Gemini) to classify incoming raw content by format (e.g., Text, JSON, PDF) and intent (e.g., RFQ, Invoice, Complaint).

Dynamic Routing: Routes classified input to specialized agents based on detected format and intent.

Specialized Agents:

Email Agent: Extracts key information from email content, such as sender, subject, intent, urgency, and a summary. Supports chaining of related email conversations.

JSON Agent: Processes and extracts structured data from JSON inputs based on a predefined schema, identifying anomalies if present.

Shared Context & Memory: Utilizes a SharedMemory module to maintain conversational context across different interactions using thread_ids, enabling traceability and follow-up processing.

LLM Integration: Configured to use the Google Gemini API for powerful and versatile natural language processing.

Extensible Architecture: Easily add new agents and routing rules to handle additional formats and intents (e.g., a PDF Agent).

# Project Structure
multi_agent_system/
├── .env                  # Environment variables (e.g., API keys)
├── .gitignore            # Specifies intentionally untracked files to ignore
├── main.py               # Orchestrator: entry point, classification, and routing logic
├── llm_wrapper.py        # Abstraction for LLM API calls (currently Google Gemini)
├── classifier_agent.py   # Agent for classifying input format and intent
├── email_agent.py        # Agent for processing and extracting data from email content
├── json_agent.py         # Agent for processing and extracting data from JSON content
├── memory_module.py      # Handles shared context and memory for interactions
└── README.md             # Project documentation (this file)
