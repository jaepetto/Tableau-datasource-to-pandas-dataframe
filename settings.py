from dotenv import load_dotenv
import os

load_dotenv()
DATASOURCE_NAME = "ZPU_CP04_STI_PRD"
HYPER_FILE_PATH = "{}.hyper".format(DATASOURCE_NAME)
SCHEMA_FILE_PATH = "{}.tds".format(DATASOURCE_NAME)
DF_PICKLE_NAME = "{}.pkl".format(DATASOURCE_NAME)

TABLEAU_SERVER = os.getenv("TABLEAU_SERVER")
TABLEAU_USERNAME = os.getenv("TABLEAU_USERNAME")
TABLEAU_PASSWORD = os.getenv("TABLEAU_PASSWORD")
