import pandas as pd
import requests
import json
import time

# 1. Load your generated CSV file
input_file = 'EA_APM_Applications.csv'
df = pd.read_csv(input_file)

# FOR TESTING: Only process the first 10 rows.
# Remove ".head(10)" to run the full dataset once you confirm it works.
df_process = df.copy()

def generate_descriptions(row):
    def safe_value(key, default="Not specified"):
        value = row.get(key, default)
        return default if pd.isna(value) else str(value).strip() or default

    app_name = safe_value('App_Name', 'Unknown application')
    component_type = safe_value('Component_Type', 'Unknown')
    app_category = safe_value('App_Category', 'Not specified')
    hosting = safe_value('App_Platform_Host', 'Not specified')
    business_criticality = safe_value('Business_Criticality', 'Not specified')

    # Stronger prompt to improve consistency, clarity, and JSON quality.
    prompt = f"""
    You are an experienced Enterprise Architect writing concise yet professional IT portfolio documentation.

    Use only the information provided below. Do not invent technical capabilities, integrations, ownership, or business context that are not present.
    If a field is missing or unspecified, state it as "Not specified" rather than making assumptions.

    Component details:
    - Name: {app_name}
    - Type: {component_type}
    - Category: {app_category}
    - Hosting: {hosting}
    - Business Criticality: {business_criticality}

    Task:
    1. Write a short summary in one sentence.
    2. Write a longer description in 3-4 sentences.
    3. Explain the component's purpose, operational context, and business relevance in neutral enterprise language.
    4. Keep the tone professional, concise, and suitable for an enterprise application catalog.

    Output requirements:
    - Respond in valid JSON only.
    - Use English only.
    - Make sure the JSON keys are exactly:
      "Short_Description" and "Long_Description"
    - Do not include markdown fences, explanations, or extra text outside the JSON object.

    JSON schema:
    {{
        "Short_Description": "Maximum 1 sentence as a brief summary.",
        "Long_Description": "3-4 sentences describing the component's technical purpose, operating model, and business value."
    }}
    """

    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.9
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        response_text = result.get('response', '{}')
        data = json.loads(response_text)

        short_description = data.get('Short_Description', '')
        long_description = data.get('Long_Description', '')
        return pd.Series([short_description, long_description], index=['Short_Description', 'Long_Description'])

    except Exception as e:
        print(f"Error processing {app_name}: {e}")
        return pd.Series([
            f"{app_name} is a {component_type.lower()} component within the enterprise application portfolio.",
            f"{app_name} supports business operations in the {app_category} domain and is hosted in {hosting}. It is classified as {business_criticality} and plays a role in the organization's IT landscape."
        ], index=['Short_Description', 'Long_Description'])

print("Starting AI generation via local Ollama... This may take a moment.")
start_time = time.time()

# 2. Apply the AI function to each row
df_process[['Short_Description', 'Long_Description']] = df_process.apply(generate_descriptions, axis=1)

# 3. Save the results to a new file
output_file = 'EA_APM_Applications_AI_Enriched.csv'
df_process.to_csv(output_file, index=False)

end_time = time.time()
print(f"\nDone! Generated {len(df_process)} records in {round(end_time - start_time, 1)} seconds.")
print(f"File saved as: {output_file}")


# we still have the duplicated prompts.... create function to create the description using llm that we can call..... standardised whole code