import logging
import snowflake.connector
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from Database.db_helper import get_db_connection
from Database.db_queries import get_polisher_bot_query
import config

# ==========================================
# 1. LOGGING CONFIGURATION
# ==========================================
# Configure the logging format to include timestamps and log levels
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ==========================================
# 2. LLM & PROMPT INITIALIZATION
# ==========================================
# Initialize connection to the local Llama 3.1 model via Ollama
llm = config.LLM_MODEL

# Combine system and human messages into a structured prompt
prompt_template = ChatPromptTemplate.from_messages([
    ("system", config.POLISHER_SYSTEM_PROMPT),
    ("human", config.POLISHER_USER_PROMPT)
])

# Create the LangChain pipeline
polisher_chain = prompt_template | llm

# ==========================================
# 4. MAIN AGENT WORKFLOW
# ==========================================

def run_polisher_bot():
    """Main execution function optimized for batch processing."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Define how many applications to process at once
    BATCH_SIZE = 50
    
    try:
        logging.info("Starting Application Polisher Bot in BATCH MODE...")
        
        cursor.execute("SELECT MAX(MONTH_YEAR) FROM EA_PORTFOLIO_DB.APM_SCHEMA.APPLICATION_STATUS_ANALSYS;")
        latest_month = cursor.fetchone()[0]
        
        if not latest_month:
            logging.warning("No month data found in the database. Exiting process.")
            return
            
        logging.info(f"Target execution month identified: {latest_month}")

        query = get_polisher_bot_query(latest_month)
        cursor.execute(query)
        apps_to_polish = cursor.fetchall()
        
        total_apps = len(apps_to_polish)
        logging.info(f"Discovered {total_apps} applications requiring polishing.")
        
        # Process the data in chunks (batches)
        for i in range(0, total_apps, BATCH_SIZE):
            batch = apps_to_polish[i:i + BATCH_SIZE]
            batch_number = (i // BATCH_SIZE) + 1
            logging.info(f"--- Processing Batch {batch_number} ({len(batch)} apps) ---")
            
            # 4.1 Prepare the input list for the LLM
            llm_inputs = []
            for app in batch:
                llm_inputs.append({
                    "app_name": app[1],
                    "short_desc": app[2],
                    "long_desc": app[3],
                    "platform": app[4],
                    "app_type": app[5],
                    "impl_type": app[6],
                    "prov_type": app[7],
                    "bus_cap": app[8],
                    "time": latest_month
                })
            
            # 4.2 Execute LLM Inference in bulk
            # Using .batch() processes the list concurrently where possible
            logging.info("Sending batch to LLM for inference...")
            batch_results = polisher_chain.batch(llm_inputs)
            
            # 4.3 Prepare the data for bulk database insertion
            db_update_payload = []
            for app, generated_text in zip(batch, batch_results):
                app_id = app[0]
                clean_text = generated_text.strip()
                # Append a tuple matching the %s variables in the UPDATE query
                db_update_payload.append((clean_text, app_id, latest_month))
            
            # 4.4 Execute a bulk SQL UPDATE (executemany)
            update_query = """
            UPDATE EA_PORTFOLIO_DB.APM_SCHEMA.APPLICATION_STATUS_ANALSYS
            SET POLISHED_LONG_DESCRIPTION = %s
            WHERE APP_ID = %s AND MONTH_YEAR = %s
            """
            logging.info("Writing batch results back to Snowflake...")
            cursor.executemany(update_query, db_update_payload)
            
            # Commit after every successful batch
            conn.commit()
            logging.info(f"Batch {batch_number} successfully saved to database.")

        logging.info("All batches completed successfully!")

    except Exception as e:
        logging.error(f"Critical error encountered: {e}")
        conn.rollback() 
        logging.info("Transaction rolled back due to failure.")
    finally:
        cursor.close()
        conn.close()
        logging.info("Snowflake database connection closed.")

if __name__ == "__main__":
    run_polisher_bot()