import os
import logging
import requests
import pandas as pd
from sqlalchemy import create_engine, text

from config import database_url, source_url, schema_name, source_folder, table_name

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ETL_Pipeline")


def get_source_data():
    """Downloads the CSV file from the source link. Saves it to the Raw folder."""
    logger.info("Starting download process from source URL")
    os.makedirs(source_folder, exist_ok=True)
    file_path = os.path.join(source_folder, source_url.split("/")[-1])

    try:
        response = requests.get(source_url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info(f"Download successful: '{file_path}' created")
        return file_path
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return None


def validate_dataframe(df: pd.DataFrame) -> bool:
    """Pre-ingestion quality validation on raw DataFrame."""
    if df is None or df.empty:
        logger.error("Data validation failed: DataFrame is empty")
        return False

    required_cols = {"year", "value", "units", "variable_code"}
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        logger.error(f"Data validation failed: Missing required columns {missing_cols}")
        return False

    logger.info(f"Pre-ingestion validation passed: {len(df)} records verified across {len(df.columns)} columns")
    return True


def convert_data(file_path):
    """Reads the CSV file from folder 'Raw' into pandas DataFrame and normalizes schema."""
    logger.info(f"Reading CSV data from '{file_path}'")
    try:
        finance_data = pd.read_csv(file_path)
        finance_data.columns = finance_data.columns.str.lower()
        
        if validate_dataframe(finance_data):
            return finance_data
        return None
    except FileNotFoundError:
        logger.error(f"Conversion failed: '{file_path}' not found")
        return None
    except Exception as e:
        logger.error(f"Conversion error: {e}")
        return None


def load_data(finance_data: pd.DataFrame, conn_string: str, table_name: str, schema_name: str):
    """Loads the DataFrame into PostgreSQL table or local SQLite database."""
    logger.info(f"Start loading data into database table '{table_name}'")
    
    use_sqlite = False
    try:
        engine = create_engine(conn_string, connect_args={'connect_timeout': 3})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        logger.warning(f"PostgreSQL connection offline ({e}). Falling back to local SQLite 'finance_pipeline.db'.")
        use_sqlite = True
        engine = create_engine("sqlite:///finance_pipeline.db")

    try:
        with engine.connect() as conn:
            if not use_sqlite:
                conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS {schema_name}'))
                conn.commit()
                target_schema = schema_name
                logger.info(f"Schema '{schema_name}' verified successfully.")
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
        logger.info(f"Loading successful: {len(finance_data)} records written to {dest_str}.")
    except Exception as e:
        logger.error(f"Loading failed: {e}")


def run_etl_pipeline():
    """Executes the full ETL pipeline."""
    logger.info("===== ETL Pipeline Execution Started =====")
    file_path = get_source_data()
    
    if file_path:
        finance_data = convert_data(file_path)
        if finance_data is not None:
            load_data(finance_data, database_url, table_name, schema_name)
            
            try:
                from llm_insights import run_llm_insights_pipeline
                run_llm_insights_pipeline()
            except Exception as e:
                logger.warning(f"Skipping AI insights generation: {e}")
    logger.info("===== ETL Pipeline Execution Completed =====")


if __name__ == "__main__":
    run_etl_pipeline()