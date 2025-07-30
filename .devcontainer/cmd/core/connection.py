"""
Devcontainer Connection Handler

This module orchestrates the complete container connection workflow:
1. Loading configuration from .conf file
2. Discovering and categorizing containers
3. Presenting user selection interface
4. Executing container connection


"""

import os
from typing import Optional
from .config import load_config
from .docker import find_containers, execute_container_connection
from .ui import create_container_selection_interface


def handle_container_connection(devcontainer_path: str) -> None:
    """
    Main orchestrator for the container connection workflow.
    
    This function coordinates the entire process of connecting to a devcontainer:
    1. Loads and validates configuration from .conf file
    2. Discovers all running containers and classifies them
    3. Presents organized selection interface to user
    4. Executes connection to selected container
    
    The workflow is designed to be user-friendly, providing clear feedback
    at each step and gracefully handling error conditions.
    
    Args:
        devcontainer_path (str): Absolute path to the .devcontainer directory
        
    Example:
        handle_container_connection('/path/to/project/.devcontainer')
    """
    # Step 1: Load and validate configuration
    config = load_config(devcontainer_path)
    if not config:
        return
    
    container_name = config.get('CONTAINER_NAME')
    remote_user = config.get('REMOTE_USER', 'vscode')
    
    print(f"📋 Container Name from config: {container_name}")
    print(f"👤 Remote User: {remote_user}")
    
    # Step 2: Discover and categorize containers
    all_containers = find_containers(container_name)
    
    if not all_containers:
        print("❌ No running containers found.")
        return
    
    # Separate matching containers from others
    matches = [c for c in all_containers if c['is_match']]
    others = [c for c in all_containers if not c['is_match']]
    
    # Step 3: Present selection interface
    selected_container = create_container_selection_interface(matches, others)
    
    if not selected_container:
        print("❌ No container selected or selection failed.")
        return
    
    # Step 4: Execute connection
    workspace_path = _determine_workspace_path(devcontainer_path)
    
    execute_container_connection(
        container_id=selected_container['id'],
        remote_user=remote_user,
        workspace_path=workspace_path
    )


def _determine_workspace_path(devcontainer_path: str) -> str:
    """
    Determine the workspace path inside the container based on project structure.
    
    VS Code devcontainers typically mount the project directory to
    /workspaces/{project-name} inside the container. This function
    extracts the project name from the local path structure.
    
    Args:
        devcontainer_path (str): Path to .devcontainer directory
        
    Returns:
        str: Workspace path inside container (e.g., '/workspaces/my-project')
    """
    # Extract project name from directory structure
    # devcontainer_path is typically: /path/to/project/.devcontainer
    # We want the project name for: /workspaces/project
    current_dir = os.path.basename(os.path.dirname(devcontainer_path))
    return f"/workspaces/{current_dir}"
