import configparser
import psycopg2
from sql_queries import copy_table_queries, insert_table_queries
import pandas as pd
from time import time
from sqlalchemy import create_engine


def load_staging_power_usage_copy(cur, conn):
    """
    This function loads the staging tables from S3 to Redshift based on sql_queries.py
    """
    for query in copy_table_queries:
        cur.execute(query)
        conn.commit()

def load_staging_process_electricity_costs(db):
    """
    This function processes the data from a csv file to a Redshift dimension table
    """
    df = pd.read_csv("data/Gemiddelde_energietarieven_31052021_164144.csv", delimiter = ';', header = 0)
    df['Perioden'] = pd.to_datetime(df['Perioden'], format="%Y %B")
    select_kwh = df[['Perioden', 'Elektriciteit/Variabel leveringstarief (Euro/kWh)']]
    select_kwh = select_kwh.rename(columns={"Perioden":"elec_prices_date_id", "Elektriciteit/Variabel leveringstarief (Euro/kWh)": "costperkwh"} )
    select_kwh['month'] = select_kwh['elec_prices_date_id'].dt.month
    select_kwh['year'] = select_kwh['elec_prices_date_id'].dt.year
    select_kwh['costperkwh'] = select_kwh['costperkwh'].replace(',', '.', regex=True)
        
    conn = db.connect()
    select_kwh.to_sql('staging_electricity_prices', con = conn, if_exists= 'append',chunksize=1000)

def insert_tables(cur, conn):
    """
    This function inserts data from the staging tables into the fact & dimension tables
    """
    for query in insert_table_queries:
        cur.execute(query)
        conn.commit()


def main():
    """
    This function connects to the redshift database and invokes the following functions:
    - load_staging_tables
    - insert_tables
    """
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    DWH_DB= config.get("CLUSTER","DB_NAME")
    DWH_DB_USER= config.get("CLUSTER","DB_USER")
    DWH_DB_PASSWORD= config.get("CLUSTER","DB_PASSWORD")
    DWH_PORT = config.get("CLUSTER","DB_PORT")
    HOST = config.get("CLUSTER", "HOST")

    
    conn_string="postgresql://{}:{}@{}:{}/{}".format(DWH_DB_USER, DWH_DB_PASSWORD, HOST, DWH_PORT,DWH_DB)
    
    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()
    db = create_engine(conn_string)

    #load_staging_power_usage_copy(cur, conn)
    #load_staging_process_electricity_costs(db)
    insert_tables(cur, conn)
    
    
    conn.close()


if __name__ == "__main__":
    main()