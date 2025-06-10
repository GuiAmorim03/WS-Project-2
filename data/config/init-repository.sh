#!/bin/bash

# Wait for GraphDB to start
echo "Waiting for GraphDB to start..."
until curl -s -f -o /dev/null "http://localhost:7200/rest/repositories"
do
  echo "GraphDB is not running yet, waiting..."
  sleep 5
done

echo "GraphDB is running!"

# Verify that config file exists
echo "Checking if config file exists..."
if [ -f "/config/repository-template.ttl" ]; then
  echo "Config file found at /config/repository-template.ttl"
else
  echo "ERROR: Config file not found at /config/repository-template.ttl"
  echo "Listing directory contents:"
  ls -la /config/
  exit 1
fi

# Check if repository exists
REPO_EXISTS=$(curl -s "http://localhost:7200/rest/repositories" | grep -c "football")

if [ "$REPO_EXISTS" -eq "0" ]; then
  echo "Creating 'football' repository..."
  # Create repository - use the correct path
  curl -X POST \
    -H "Content-Type: multipart/form-data" \
    -F "config=@/config/repository-template.ttl" \
    "http://localhost:7200/rest/repositories"
  
  # Check if repository was created
  REPO_CHECK=$(curl -s "http://localhost:7200/rest/repositories" | grep -c "football")
  if [ "$REPO_CHECK" -eq "1" ]; then
    echo "Repository 'football' created successfully"
  else
    echo "Failed to create repository"
    exit 1
  fi
else
  echo "Repository 'football' already exists"
fi

# Import the dataset to the football repository using REST API
echo "Importing dataset from server file..."
IMPORT_DATASET=$(curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "fileNames": [
      "football_rdf_data.nt"
    ]
  }' \
    "http://localhost:7200/rest/repositories/football/import/server")

if "$IMPORT_DATASET"; then
    echo ""
    echo "Dataset import initiated successfully"
else
  echo "Failed to import dataset"
fi

echo "Setup complete!"
