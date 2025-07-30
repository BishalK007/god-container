"""
Devcontainer Configuration Management Module

This module handles loading, validating, and managing devcontainer configuration
from the .conf file. It provides utilities for reading container settings,
user preferences, and environment details.


"""

import os
from typing import Dict, Optional


def load_config(devcontainer_path: str) -> Optional[Dict[str, str]]:
    """
    Load and validate configuration from .devcontainer/.conf file.
    
    This function reads the configuration file that contains essential
    devcontainer settings like container name, remote user, UID/GID, etc.
    
    Args:
        devcontainer_path (str): Absolute path to the .devcontainer directory
        
    Returns:
        Optional[Dict[str, str]]: Configuration dictionary if successful, None if failed
        
    Example:
        config = load_config('/path/to/.devcontainer')
        if config:
            container_name = config.get('CONTAINER_NAME')
            remote_user = config.get('REMOTE_USER', 'vscode')
    """
    conf_path = os.path.join(devcontainer_path, '.conf')
    config = {}
    
    if not os.path.exists(conf_path):
        print(f"❌ Configuration file not found: {conf_path}")
        print("Please run with --conf first to configure the devcontainer")
        return None
    
    try:
        with open(conf_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
        
        # Validate required fields
        if 'CONTAINER_NAME' not in config or not config['CONTAINER_NAME']:
            print("❌ CONTAINER_NAME not found in configuration file")
            return None
            
        return config
    except Exception as e:
        print(f"❌ Error reading config file: {e}")
        return None


def normalize_container_name(container_name: str) -> str:
    """
    Convert human-readable container name to search pattern.
    
    This function transforms container names with spaces and special characters
    into lowercase, hyphen-separated strings suitable for matching against
    Docker container image names.
    
    Args:
        container_name (str): Human-readable container name (e.g., "God Container")
        
    Returns:
        str: Normalized search pattern (e.g., "god-container")
        
    Example:
        pattern = normalize_container_name("My Dev Container")
        # Returns: "my-dev-container"
    """
    return container_name.lower().replace(' ', '-')
