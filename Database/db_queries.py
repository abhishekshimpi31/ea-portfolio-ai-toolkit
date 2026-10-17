# Polisher Bot SQL Query
def get_polisher_bot_query(latest_month: str) -> str:
    """Returns the SQL query to fetch applications that need polishing."""
    return f"""
        SELECT APP_ID, APP_NAME, SHORT_DESCRIPTION, LONG_DESCRIPTION, 
               APP_PLATFORM_HOST, APPLICATION_TYPE, IMPLEMENTATION_TYPE, 
               PROVISIONING_TYPE, BUSINESS_CAPABILITY
        FROM EA_PORTFOLIO_DB.APM_SCHEMA.APPLICATION_STATUS_ANALSYS
        WHERE MONTH_YEAR = '{latest_month}'
          AND STATUS IN ('Draft', 'Planned', 'Productive')
          AND POLISHED_LONG_DESCRIPTION IS NULL; -- Only process untouched apps
    """