import snowflake.connector
import config


# ==========================================
# 3. DATABASE CONNECTION
# ==========================================
def get_db_connection():
    """Establish and return a connection to the Snowflake database."""
    return snowflake.connector.connect(
        user=config.SNOWFLAKE_USER,
        password=config.SNOWFLAKE_PASSWORD,
        account=config.SNOWFLAKE_ACCOUNT,
        warehouse=config.SNOWFLAKE_WAREHOUSE,
        database=config.SNOWFLAKE_DATABASE,
        schema=config.SNOWFLAKE_SCHEMA
    )