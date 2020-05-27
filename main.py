"""
Reference: https://help.tableau.com/current/api/hyper_api/en-us/

Point of interest: https://pantab.readthedocs.io/en/latest/index.html
"""
import os
import xml.etree.ElementTree as ET
import zipfile

import pandas as pd
import tableauserverclient as TSC
from tableauhyperapi import Connection, HyperProcess, TableName, Telemetry
from sqlalchemy import create_engine

import settings


def cleanup():
    os.remove(settings.HYPER_FILE_PATH)
    os.remove(settings.SCHEMA_FILE_PATH)
    os.remove("{}.tdsx".format(settings.DATASOURCE_NAME))


def download_datasource():
    server = TSC.Server(settings.TABLEAU_SERVER, use_server_version=True)
    tableau_auth = TSC.TableauAuth(settings.TABLEAU_USERNAME, settings.TABLEAU_PASSWORD)
    server.auth.sign_in(tableau_auth)
    all_datasources, pagination_item = server.datasources.get()
    for datasource in all_datasources:
        if datasource.name == settings.DATASOURCE_NAME:
            server.datasources.download(
                datasource.id, filepath=settings.DATASOURCE_NAME, include_extract=True
            )
            break

    with zipfile.ZipFile("{}.tdsx".format(settings.DATASOURCE_NAME), "r") as zip_file:
        for zip_info in zip_file.infolist():
            if zip_info.filename[-1] == "/":
                continue
            zip_info.filename = os.path.basename(zip_info.filename)
            zip_file.extract(zip_info, ".")

    server.auth.sign_out()


def get_table_names():
    """
    Returns the list of the tables contained into the Tableau data source.
    Normally, there is usually only one table: Extract.Extract
    """
    return_value = []

    with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
        with Connection(
            endpoint=hyper.endpoint, database=settings.HYPER_FILE_PATH
        ) as connection:
            table_names = connection.catalog.get_table_names(schema="Extract")

            for table in table_names:
                return_value.append(table)
    return return_value


def get_table_columns(table):
    """
    Returns the list of the columns in the table.
    This is a list of dictionaries having the following keys:
    * name: the Tableau caption of the column (when found)
    * type: the data type contained in that column
    * nullability: a flag indicating if the column may contain null values
    """
    return_value = []

    columns_mappings = get_columns_mappings()

    with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
        with Connection(
            endpoint=hyper.endpoint, database=settings.HYPER_FILE_PATH
        ) as connection:
            table_definition = connection.catalog.get_table_definition(name=table)
            for column in table_definition.columns:
                name = str(column.name).replace('"', "")
                if name in columns_mappings.keys():
                    name = columns_mappings[name]
                return_value.append(
                    {
                        "name": name,
                        "type": str(column.type),
                        "nullability": str(column.nullability),
                    }
                )
    return return_value


def get_table_rows(table):
    """
    Returns a list of list representing all the rows in the table
    """
    with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
        with Connection(
            endpoint=hyper.endpoint, database=settings.HYPER_FILE_PATH
        ) as connection:
            rows_in_table = connection.execute_list_query(
                query=f"SELECT * FROM {table}"
            )
            return rows_in_table


def get_columns_mappings():
    """
    Returns a dictionary object representing the mapping between the real name of the column and the caption displayed on Tableau
    """
    return_value = {}

    tree = ET.parse(settings.SCHEMA_FILE_PATH)
    root = tree.getroot()
    for column in root.findall("column"):
        name = column.get("name").replace("[", "").replace("]", "")
        caption = column.get("caption")
        return_value[name] = caption

    return return_value


def __cast_tableau_date_to_datetime(tableau_date):
    return pd.to_datetime(str(tableau_date))


def clean_and_cast(df):
    # Cast the Tableau Hyper date type into a 'regular' Timestamp
    df["Exercice comptable"] = df.apply(
        lambda x: __cast_tableau_date_to_datetime(x["Exercice comptable"]), axis=1
    )

    return df


def upload_to_db(df):
    engine = create_engine(
        "postgresql://{}:{}@{}:{}/{}".format(
            settings.DB_USERNAME,
            settings.DB_PASSWORD,
            settings.DB_HOST,
            settings.DB_PORT,
            settings.DB_SCHEMA,
        )
    )
    df.to_sql(settings.DB_TABLE_SAP_FI, con=engine, if_exists="replace", index=False)


if __name__ == "__main__":
    # download the data source from Tableau
    download_datasource()

    # Get all the information about the data table in that Tableau data source
    tables = get_table_names()
    columns = get_table_columns(tables[0])
    rows = get_table_rows(tables[0])

    # dumps the table into a pickled pandas dataframe for later use
    columns_names = []
    [columns_names.append(column["name"]) for column in columns]
    df = pd.DataFrame.from_records(rows, columns=columns_names)

    # clean data that may not be recognized by regular date engines
    df = clean_and_cast(df)

    # uploads the dataframe into a database for easier use
    upload_to_db(df)

    # remove any temporary files
    cleanup()
