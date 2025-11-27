"""
Configuration for QB-Bitrix24 Connector
"""

# QuickBooks Settings
QB_APP_NAME = "QB-Bitrix24 Connector"
QB_COMPANY_FILE = ""  # Leave empty to use currently open company file

# Bitrix24 Settings
BITRIX24_URL = "https://hartzell.app"
BITRIX24_WEBHOOK = "https://hartzell.app/rest/1/rdz3zqhd8m0bqcxd/"

# Web Connector SOAP Service Settings
SOAP_HOST = "127.0.0.1"
SOAP_PORT = 8080
SOAP_USERNAME = "qbconnector"
SOAP_PASSWORD = "change_this_password"  # Change this!

# Sync Settings
SYNC_INTERVAL_SECONDS = 300  # 5 minutes (controlled by Web Connector)

# Database for tracking sync state
DATABASE_PATH = "C:/Users/max/qb-bitrix-connector/sync_state.db"

# Logging
LOG_FILE = "C:/Users/max/qb-bitrix-connector/connector.log"
LOG_LEVEL = "INFO"
