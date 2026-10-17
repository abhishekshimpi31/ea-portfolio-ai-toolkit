EA Portfolio AI Toolkit

An intelligent Enterprise Architecture (EA) application portfolio management suite. This project combines a modern frontend dashboard for data quality monitoring with an autonomous AI agent that automatically enhances and polishes application metadata directly in Snowflake.

Features

1. Issue Management Dashboard (app.py)

A fast, interactive Streamlit web application acting as the frontend for EA managers.

Data Quality Auditing: Automatically flags applications missing mandatory checks or containing empty fields.

Advanced Filtering: Filter by App ID, Name, Month/Year, Status, and Transition Category with pagination for high performance.

Integrated Communication: Draft and simulate sending targeted email reminders to Application Owners and Managers.

Audit Trail: Logs every sent notification directly into a dedicated Snowflake table (EMAIL_NOTIFICATION_LOG).

2. Application Polisher Bot (polisher_bot.py)

An autonomous backend AI agent built with LangChain and local Llama 3.1 (via Ollama).

Automated Enrichment: Scans the database for specific applications and rewrites their technical descriptions into professional, business-oriented summaries.

Batch Processing: Utilizes LangChain batching and Snowflake bulk updates (executemany) for scalable data processing.

Data Preservation: Writes AI-generated content into a dedicated POLISHED_LONG_DESCRIPTION column to preserve raw historical data.

Tech Stack

Frontend: Streamlit

AI / Orchestration: LangChain, Ollama (Llama 3.1)

Database: Snowflake (snowflake-connector-python)

Data Manipulation: Pandas

Prerequisites

Python 3.9+ installed.

Ollama installed and running locally with the llama3.1 model (ollama run llama3.1).

Access to a Snowflake account with the appropriate database, schema, and table structures (e.g., APPLICATION_STATUS_ANALSYS).

Setup & Installation

Clone the repository:

git clone https://github.com/your-org/ea-portfolio-ai-toolkit.git
cd ea-portfolio-ai-toolkit


Install dependencies:

pip install streamlit pandas snowflake-connector-python langchain langchain-ollama


Configure Database Credentials:
Create a config.py file in the root directory and add your Snowflake credentials:

# config.py
SNOWFLAKE_USER = "your_username"
SNOWFLAKE_PASSWORD = "your_password"
SNOWFLAKE_ACCOUNT = "your_account_identifier"
SNOWFLAKE_WAREHOUSE = "your_warehouse"
SNOWFLAKE_DATABASE = "EA_PORTFOLIO_DB"
SNOWFLAKE_SCHEMA = "APM_SCHEMA"


(Note: Ensure config.py is added to your .gitignore file to prevent leaking credentials!)

Usage

Running the Dashboard

To start the Issue Management UI, run:

streamlit run app.py


The dashboard will be available at http://localhost:8501.

Running the AI Agent

To execute the Application Polisher Bot (can be scheduled via cron or Task Scheduler):

python polisher_bot.py


Check the console output for detailed logging information regarding the batch processing status.

Snowflake Schema Setup

Ensure the following column exists to store the AI results without overwriting user data:

ALTER TABLE EA_PORTFOLIO_DB.APM_SCHEMA.APPLICATION_STATUS_ANALSYS 
ADD COLUMN POLISHED_LONG_DESCRIPTION VARCHAR;
