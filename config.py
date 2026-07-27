import os
from dotenv import load_dotenv # pyright: ignore[reportMissingImports]

# Load environment variables from .env file
load_dotenv()

# Database connection details
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5434")
DB_NAME = os.getenv("DB_NAME", "posey")

database_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

source_url = "https://www.stats.govt.nz/assets/Uploads/Annual-enterprise-survey/Annual-enterprise-survey-2023-financial-year-provisional/Download-data/annual-enterprise-survey-2023-financial-year-provisional.csv"
source_folder = "Raw"
schema_name = "dev_staging"
table_name = "finance_2023"
