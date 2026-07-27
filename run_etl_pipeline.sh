#!/bin/bash

# Setup Environment for either Git Bash or WSL Ubuntu
if [[ "$OSTYPE" == "msys" ]]; then
  LOG_FILE="$(pwd)/pipeline.log"
  exec > >(tee -a "$LOG_FILE") 2>&1
  echo "===== Pipeline started at $(date) ====="
  # Running on Git Bash on Windows
  echo "Detected Git Bash on Windows. Configuring Conda paths."
  CONDA_BIN_PATH="/c/anaconda3/Scripts"

elif [[ "$OSTYPE" == "linux-gnu" ]]; then
  # Running on WSL Ubuntu
  SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
  cd "$SCRIPT_DIR"
  LOG_FILE="$SCRIPT_DIR/pipeline.log"
  exec > >(tee -a "$LOG_FILE") 2>&1
  echo "===== Pipeline started at $(date) ====="
  echo "Detected WSL Ubuntu. Configuring Conda paths."
  CONDA_BIN_PATH="/home/ojo_dev/miniconda3/bin"
  export DB_HOST=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
  echo "DB_HOST set to $DB_HOST"

else
  echo "Unsupported OS: $OSTYPE"
  exit 1
fi

export PATH="${CONDA_BIN_PATH}:${PATH}"

# Exit immediately if any command fails
set -e

# Conda environment name
CONDA_ENV_NAME="venv310"

# Define script's directory needed
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE}")" && pwd)
DBT_PROJECT_DIR="$SCRIPT_DIR/dbt_transformation"

# Run python ETL script
echo "Starting Python ETL script..."
conda run --name "$CONDA_ENV_NAME" python "$SCRIPT_DIR/etl_pipeline.py"

# Run DBT Transformation
echo "Starting dbt transformation..."
cd "$DBT_PROJECT_DIR"
conda run --name "$CONDA_ENV_NAME" dbt build

echo "$(date): Pipeline completed successfully."
