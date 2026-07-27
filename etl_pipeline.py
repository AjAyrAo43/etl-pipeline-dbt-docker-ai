import os
import requests
import pandas as pd
from sqlalchemy import create_engine, text

from config import database_url, source_url, schema_name, source_folder, table_name


def get_source_data():
    # Downloads the CSV file from the source link. Saves it to the Raw folder.

    print("Starting download process")
    # Create Folder "Raw" if not exists
    os.makedirs(source_folder, exist_ok=True)
    print(f"Created Destination folder {source_folder}")
    
    file_path = os.path.join(source_folder, source_url.split("/")[-1])

    try:
        response = requests.get(source_url, stream=True)
        response.raise_for_status()
        
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Download successful: '{file_path}' created")
        return file_path
    except Exception as e:
        print(f"Download failed: {e}")
        return None
    
def convert_data(file_path):
    # Reads the csv file from folder "Raw" into pandas Dataframe
    
    print("Starting Conversion to Dataframe")
    try:
        finance_data = pd.read_csv(file_path)
        print("Successfully read the csv data")
        
        # Convert all column names to lowercase
        finance_data.columns = finance_data.columns.str.lower()
        print("Transformed all Column names to Lower case")
        return finance_data
    
    except FileNotFoundError:
        print(f"Conversion failed: {file_path} not found")
        return None

def load_data(finance_data: pd.DataFrame, conn_string: str, table_name: str, schema_name: str):
    # Loads the Dataframe into PostgreSQL table or local SQLite database.
    print(f"Start loading data into database table '{table_name}'")
    
    use_sqlite = False
    try:
        engine = create_engine(conn_string, connect_args={'connect_timeout': 3})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        print(f"PostgreSQL connection offline ({e}). Using local SQLite database 'finance_pipeline.db'.")
        use_sqlite = True
        engine = create_engine("sqlite:///finance_pipeline.db")

    try:
        with engine.connect() as conn:
            if not use_sqlite:
                conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS {schema_name}'))
                conn.commit()
                target_schema = schema_name
                print(f"Schema '{schema_name}' created/verified successfully.")
            else:
                target_schema = None
            
            finance_data.to_sql(
                name=table_name,
                con=conn,
                schema=target_schema,
                if_exists="replace",
                index=False
            )
        dest_str = f"'{schema_name}.{table_name}'" if not use_sqlite else f"'{table_name}' (SQLite)"
        print(f"Loading successful: Data written to {dest_str}.")
    except Exception as e:
        print(f"Loading failed: {e}")
        
            
def run_etl_pipeline():
    # Executes the full ETL pipeline.
   
    file_path = get_source_data()
    
    if file_path:
        finance_data = convert_data(file_path)
        
        if finance_data is not None:
            load_data(finance_data, database_url, table_name, schema_name)
            
            # Trigger AI Executive Insights summary if table is loaded
            try:
                from llm_insights import run_llm_insights_pipeline
                run_llm_insights_pipeline()
            except Exception as e:
                print(f"Skipping AI insights generation: {e}")
        
if __name__ == "__main__":
    run_etl_pipeline()