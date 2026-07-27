#!/bin/bash
set -e

# Changing to the project directory
PROJECT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_PATH"

LOG_FILE="$PROJECT_PATH/docker_pipeline.log"
exec > >(tee -a "$LOG_FILE") 2>&1
echo "===== Pipeline started at $(date) ====="

# Starting the project container
docker compose up --build --force-recreate --remove-orphans

# Checking for any failures during the `docker compose up`
if [ $? -eq 0 ]; then
    echo "$(date): Pipeline completed successfully."
else
    echo "$(date): Pipeline failed. See logs for details."
fi

# Stop all services to clean up
docker compose down

exit 0
