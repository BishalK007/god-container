#!/usr/bin/env python3
"""
Configuration File Management Module

This module handles the creation and management of the .conf file that stores
important devcontainer configuration for later use during container connection.

The .conf file contains essential configuration values that are needed when
connecting to running containers, such as container name, remote user, and
permission settings.

Author: Devcontainer God Project
Created: 2025-07-30
"""

import os
from typing import Dict, Any


def save_config_file(data: Dict[str, Any], devcontainer_path: str, custom_docker_container_name: str = "") -> str:
    """
    Save important configuration values to .conf file for later use.
    
    This function extracts key configuration values from the complete
    devcontainer configuration and saves them to a .conf file that
    can be easily parsed for container connection operations.
    
    Args:
        data: Complete devcontainer configuration dictionary
        devcontainer_path: Path to .devcontainer directory
        custom_docker_container_name: Custom Docker container name (if any)
        
    Returns:
        Path to the created .conf file
        
    Example:
        conf_path = save_config_file(config_data, '/path/to/.devcontainer', 'my-custom-name')
    """
    # Extract important values from the devcontainer configuration
    config_data = {
        'REMOTE_USER': data.get('remoteUser', 'vscode'),
        'CONTAINER_NAME': data.get('name', 'devcontainer'),
        'IMAGE': data.get('image', ''),
        'USER_ID': '',
        'GROUP_ID': '',
        'CUSTOM_DOCKER_CONTAINER_NAME': custom_docker_container_name
    }
    
    # Clean up temporary properties from the original data (don't save them in devcontainer.json)
    if '_temp_custom_docker_container_name' in data:
        del data['_temp_custom_docker_container_name']
    
    # Extract user ID and group ID from runArgs if present
    run_args = data.get('runArgs', [])
    for arg in run_args:
        if arg.startswith('--user='):
            user_info = arg.replace('--user=', '')
            if ':' in user_info:
                config_data['USER_ID'], config_data['GROUP_ID'] = user_info.split(':')
            else:
                config_data['USER_ID'] = user_info
    
    # Create .conf file content
    conf_content = f"""# Devcontainer Configuration
# Generated automatically - do not edit manually

# User Configuration
REMOTE_USER={config_data['REMOTE_USER']}
USER_ID={config_data['USER_ID']}
GROUP_ID={config_data['GROUP_ID']}

# Container Configuration  
CONTAINER_NAME={config_data['CONTAINER_NAME']}
IMAGE={config_data['IMAGE']}
CUSTOM_DOCKER_CONTAINER_NAME={config_data['CUSTOM_DOCKER_CONTAINER_NAME']}

# Usage Examples:
# docker exec -it $(docker ps -q --filter "label=devcontainer.local_folder") bash
# docker exec -it --user {config_data['REMOTE_USER']} $(docker ps -q --filter "name=vsc-") bash
"""
    
    # Save to .devcontainer/.conf
    conf_path = os.path.join(devcontainer_path, '.conf')
    with open(conf_path, 'w') as f:
        f.write(conf_content)
    
    print(f"📋 Configuration saved to {conf_path}")
    return conf_path


def update_config_file(devcontainer_path: str, **updates) -> str:
    """
    Update specific values in existing .conf file.
    
    Args:
        devcontainer_path: Path to .devcontainer directory
        **updates: Key-value pairs to update in the config
        
    Returns:
        Path to the updated .conf file
    """
    conf_path = os.path.join(devcontainer_path, '.conf')
    
    if not os.path.exists(conf_path):
        raise FileNotFoundError(f"Config file not found: {conf_path}")
    
    # Read existing config
    config_data = {}
    with open(conf_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                config_data[key.strip()] = value.strip()
    
    # Apply updates
    config_data.update(updates)
    
    # Recreate the file
    conf_content = f"""# Devcontainer Configuration
# Generated automatically - do not edit manually

# User Configuration
REMOTE_USER={config_data.get('REMOTE_USER', 'vscode')}
USER_ID={config_data.get('USER_ID', '')}
GROUP_ID={config_data.get('GROUP_ID', '')}

# Container Configuration  
CONTAINER_NAME={config_data.get('CONTAINER_NAME', 'devcontainer')}
IMAGE={config_data.get('IMAGE', '')}
CUSTOM_DOCKER_CONTAINER_NAME={config_data.get('CUSTOM_DOCKER_CONTAINER_NAME', '')}

# Usage Examples:
# docker exec -it $(docker ps -q --filter "label=devcontainer.local_folder") bash
# docker exec -it --user {config_data.get('REMOTE_USER', 'vscode')} $(docker ps -q --filter "name=vsc-") bash
"""
    
    with open(conf_path, 'w') as f:
        f.write(conf_content)
    
    print(f"📋 Configuration updated in {conf_path}")
    return conf_path
