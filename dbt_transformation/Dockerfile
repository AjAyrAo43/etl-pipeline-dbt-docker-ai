FROM python:3.10-slim

WORKDIR /app/dbt_transformation

# Install dbt core for postgres
RUN pip install dbt-core dbt-postgres

COPY . .

# Run the dbt command
CMD ["dbt", "build"]