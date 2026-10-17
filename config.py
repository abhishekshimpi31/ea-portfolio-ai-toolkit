import os
from pathlib import Path

# Load environment variables from .env file if dotenv is installed

from dotenv import load_dotenv
from langchain_ollama import OllamaLLM

load_dotenv(override=True)


SNOWFLAKE_USER = os.getenv('SNOWFLAKE_USER')
SNOWFLAKE_PASSWORD = os.getenv('SNOWFLAKE_PASSWORD')
SNOWFLAKE_ACCOUNT = os.getenv('SNOWFLAKE_ACCOUNT')
SNOWFLAKE_WAREHOUSE = os.getenv('SNOWFLAKE_WAREHOUSE')
SNOWFLAKE_DATABASE = os.getenv('SNOWFLAKE_DATABASE')
SNOWFLAKE_SCHEMA = os.getenv('SNOWFLAKE_SCHEMA')

# 2. Langflow Konfiguration
LANGFLOW_API_URL = os.getenv('LANGFLOW_API_URL')
LANGFLOW_API_KEY = os.getenv('LANGFLOW_API_KEY')


# LLM setup
LLM_MODEL = OllamaLLM(model="llama3.1:latest", base_url="http://localhost:11434")

# Polisher Bot configuration
POLISHER_SYSTEM_PROMPT = """You are an expert in Enterprise Architecture Management (EAM).
Your task is to write a professional, clear, and comprehensive application description (Long Description) for an EA portfolio system.
Maintain a factual, concise, and business-oriented tone.
If specific fields are missing or empty (None/NULL), omit them logically without mentioning their absence.
IMPORTANT: Reply ONLY with the final generated description. Do not include any introductions, explanations, summaries, or markdown formatting."""

# Define the User Prompt (Injects the actual dynamic data)
POLISHER_USER_PROMPT = """Here is the application metadata (As of: {time}):
- Name: {app_name}
- Short Description: {short_desc}
- Current Description: {long_desc}
- Platform/Host: {platform}
- Application Type: {app_type}
- Implementation Type: {impl_type}
- Provisioning Type: {prov_type}
- Business Capability: {bus_cap}

Write a cohesive, professional description (approx. 3-5 sentences) based on this data."""               
