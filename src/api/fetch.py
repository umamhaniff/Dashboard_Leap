"""
API fetching module for Dashboard Leap.
Handles data retrieval from external APIs and databases.
"""

import requests
import yaml
import os
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    """Load configuration from db.yaml"""
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'db.yaml')
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def fetch_from_api(endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Fetch data from external API.
    
    Args:
        endpoint: API endpoint to fetch from
        params: Query parameters
        
    Returns:
        JSON response from API
    """
    config = load_config()
    base_url = config['api']['base_url']
    api_key = config['api']['key']
    
    headers = {'Authorization': f'Bearer {api_key}'} if api_key else {}
    
    url = f"{base_url}/{endpoint}"
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    return response.json()

def fetch_from_database(query: str) -> Any:
    """
    Fetch data from database.
    
    Args:
        query: SQL query to execute
        
    Returns:
        Query results
    """
    # Placeholder for database connection
    # In a real implementation, use libraries like psycopg2 for PostgreSQL
    config = load_config()
    
    # Mock implementation
    print(f"Executing query: {query}")
    return {"mock": "data"}