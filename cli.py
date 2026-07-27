import sys
import argparse
import logging
from etl_pipeline import get_source_data, convert_data, load_data
from llm_insights import run_llm_insights_pipeline
from config import database_url, schema_name, table_name

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] CLI: %(message)s")
logger = logging.getLogger("CLI_Runner")

def main():
    parser = argparse.ArgumentParser(description="ETL & GenAI Pipeline CLI Runner")
    parser.add_argument("--extract", action="store_true", help="Download raw source data")
    parser.add_argument("--transform", action="store_true", help="Process and load data into database")
    parser.add_argument("--insights", action="store_true", help="Generate AI/LLM Executive Insights")
    parser.add_argument("--all", action="store_true", help="Run full end-to-end pipeline")
    
    args = parser.parse_args()
    
    # Default to --all if no specific arguments provided
    if not (args.extract or args.transform or args.insights or args.all):
        args.all = True
        
    if args.all:
        logger.info("Executing full end-to-end pipeline...")
        file_path = get_source_data()
        if file_path:
            df = convert_data(file_path)
            if df is not None:
                load_data(df, database_url, table_name, schema_name)
                run_llm_insights_pipeline()
        return

    if args.extract:
        logger.info("Running extraction step...")
        get_source_data()
        
    if args.transform:
        logger.info("Running transformation & database load step...")
        file_path = get_source_data()
        if file_path:
            df = convert_data(file_path)
            if df is not None:
                load_data(df, database_url, table_name, schema_name)

    if args.insights:
        logger.info("Running AI Insights generator...")
        run_llm_insights_pipeline()

if __name__ == "__main__":
    main()
