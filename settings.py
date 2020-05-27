from dotenv import load_dotenv
import os

load_dotenv()
DATASOURCE_NAME = "ZPU_CP04_STI_PRD"
HYPER_FILE_PATH = "{}.hyper".format(DATASOURCE_NAME)
SCHEMA_FILE_PATH = "{}.tds".format(DATASOURCE_NAME)

TABLEAU_SERVER = os.getenv("TABLEAU_SERVER")
TABLEAU_USERNAME = os.getenv("TABLEAU_USERNAME")
TABLEAU_PASSWORD = os.getenv("TABLEAU_PASSWORD")

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_SCHEMA = os.getenv("DB_SCHEMA")
DB_TABLE_SAP_FI = os.getenv("DB_TABLE_SAP_FI")
