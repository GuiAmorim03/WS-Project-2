#!/bin/bash

# Usage: ./init-repository.sh /path/to/config

CONFIG_DIR=${1:-/config}
CONFIG_FILE="$CONFIG_DIR/repository-template.ttl"

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
if [ -f "$CONFIG_FILE" ]; then
  echo "Config file found at $CONFIG_FILE"
else
  echo "ERROR: Config file not found at $CONFIG_FILE"
  echo "Listing directory contents:"
  ls -la "$CONFIG_DIR"
  exit 1
fi

# Check if repository exists
REPO_EXISTS=$(curl -s "http://localhost:7200/rest/repositories" | grep -c "football")

if [ "$REPO_EXISTS" -eq "0" ]; then
  echo "Creating 'football' repository..."
  # Create repository - use the correct path
  curl -X POST \
    -H "Content-Type: multipart/form-data" \
    -F "config=@$CONFIG_FILE" \
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
  echo "Deleting existing repository to avoid duplicates..."
  curl -X DELETE "http://localhost:7200/rest/repositories/football"
  
  if [ $? -eq 0 ]; then
    echo "Repository deleted successfully"
    sleep 2
    
    echo "Recreating 'football' repository..."
    curl -X POST \
      -H "Content-Type: multipart/form-data" \
      -F "config=@/config/repository-template.ttl" \
      "http://localhost:7200/rest/repositories"
    
    if [ $? -eq 0 ]; then
      echo "Repository recreated successfully"
      sleep 2
    else
      echo "Failed to recreate repository"
      exit 1
    fi
  else
    echo "Failed to delete repository"
    exit 1
  fi
fi

# Import the ontology to the football repository using REST API
echo "Importing ontology from server file..."
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "fileNames": [
      "ontology/football_ontology.n3"
    ]
  }' \
  "http://localhost:7200/rest/repositories/football/import/server"

if [ $? -eq 0 ]; then
    echo ""
    echo "Ontology import initiated successfully"
    # Wait a bit for ontology import to complete
    sleep 3
else
  echo "Failed to import ontology"
  exit 1
fi

# Import the dataset to the football repository using REST API
echo "Importing dataset from server file..."
IMPORT_DATASET=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "fileNames": [
      "football_rdf_data.nt"
    ]
  }' \
    "http://localhost:7200/rest/repositories/football/import/server")

if [ "$IMPORT_DATASET" -eq "202" ]; then
    echo ""
    echo "Dataset import initiated successfully"
    # Wait for import to complete
    sleep 5
else
  echo "Failed to import dataset"
  exit 1
fi

echo "Setup complete!"
