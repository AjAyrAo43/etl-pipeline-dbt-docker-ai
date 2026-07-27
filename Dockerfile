FROM python:3.10-bookworm

WORKDIR /app

# Copy only the requirements file first to leverage build cache
COPY requirements.txt .

# Install dependencies without using the cache to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Run the ETL pipeline script and exit
CMD ["python", "etl_pipeline.py"]
