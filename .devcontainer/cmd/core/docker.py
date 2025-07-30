"""
Docker Container Discovery and Management Module

This module provides functionality to discover, filter, and interact with
Docker containers, specifically targeting VS Code devcontainers. It handles
container detection, pattern matching, and provides structured data for
container selection interfaces.


"""

import subprocess
from typing import List, Dict, Any
from .config import normalize_container_name


def find_containers(container_name: str) -> List[Dict[str, Any]]:
    """
    Discover all running Docker containers and classify them based on name matching.
    
    This function queries Docker for all running containers, then classifies them
    as either "matches" (containers whose image names contain the search pattern)
    or "others" (all other running containers). This is particularly useful for
    VS Code devcontainers which follow the naming pattern:
    vsc-{project-name}-{hash}-features-uid
    
    Args:
        container_name (str): The container name to search for (e.g., "God Container")
        
    Returns:
        List[Dict[str, Any]]: List of container dictionaries with the following structure:
            {
                'name': str,        # Docker assigned container name
                'id': str,          # Container ID (short form)
                'image': str,       # Full image name
                'status': str,      # Container status (e.g., "Up 5 minutes")
                'created': str,     # Creation timestamp
                'is_match': bool    # True if matches search pattern
            }
            
    Example:
        containers = find_containers("God Container")
        matches = [c for c in containers if c['is_match']]
        others = [c for c in containers if not c['is_match']]
    """
    try:
        # Use pipe-separated format for reliable parsing
        # This avoids issues with table formatting and whitespace
        result = subprocess.run(
            ['docker', 'ps', '--format', '{{.Names}}|{{.ID}}|{{.Image}}|{{.Status}}|{{.CreatedAt}}'], 
            capture_output=True, text=True, check=True
        )
        
        containers = []
        lines = result.stdout.strip().split('\n')
        
        # Create search pattern from container name
        search_pattern = normalize_container_name(container_name)
        print(f"🔍 Searching for containers containing: '{search_pattern}'")
        
        for line in lines:
            if line.strip():
                parts = line.split('|')
                
                if len(parts) >= 5:
                    name, container_id, image, status, created = parts[0], parts[1], parts[2], parts[3], parts[4]
                    
                    # VS Code devcontainers have the pattern in the image name
                    # Format: vsc-{project-name}-{hash}-features-uid
                    is_match = search_pattern in image.lower() and 'vsc-' in image.lower()
                    
                    containers.append({
                        'name': name,
                        'id': container_id,
                        'image': image,
                        'status': status,
                        'created': created,
                        'is_match': is_match
                    })
                elif len(parts) >= 3:
                    # Fallback for containers with incomplete info
                    name, container_id, image = parts[0], parts[1], parts[2]
                    is_match = search_pattern in image.lower() and 'vsc-' in image.lower()
                    
                    containers.append({
                        'name': name,
                        'id': container_id,
                        'image': image,
                        'status': 'Unknown',
                        'created': 'Unknown',
                        'is_match': is_match
                    })
        
        return containers
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running docker ps command: {e}")
        return []
    except Exception as e:
        print(f"❌ Error finding containers: {e}")
        return []


def execute_container_connection(container_id: str, remote_user: str, workspace_path: str) -> None:
    """
    Execute docker exec command to connect to a container with proper user and workspace.
    
    This function builds and executes the docker exec command with the correct
    user, working directory, and shell to provide a seamless development
    environment connection.
    
    Args:
        container_id (str): The Docker container ID to connect to
        remote_user (str): Username to use inside the container (e.g., 'vscode')
        workspace_path (str): Working directory path inside container (e.g., '/workspaces/project')
        
    Raises:
        KeyboardInterrupt: When user cancels the connection
        Exception: When Docker connection fails
        
    Example:
        execute_container_connection('abc123', 'vscode', '/workspaces/my-project')
    """
    # Build docker exec command with proper parameters
    docker_cmd = [
        'docker', 'exec', '-it',      # Interactive TTY
        '--user', remote_user,         # Run as specified user
        '-w', workspace_path,          # Set working directory
        container_id,                  # Target container
        'bash'                         # Shell to execute
    ]
    
    print(f"🔗 Connecting to container: {container_id}")
    print(f"👤 User: {remote_user}")
    print(f"📁 Working directory: {workspace_path}")
    print("=" * 60)
    
    # Execute the connection
    try:
        subprocess.run(docker_cmd)
    except KeyboardInterrupt:
        print("\n👋 Connection closed.")
    except Exception as e:
        print(f"❌ Error connecting to container: {e}")
        print("💡 Make sure the container is running and accessible.")
