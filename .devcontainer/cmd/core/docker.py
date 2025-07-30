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


def find_containers(container_name: str, custom_docker_container_name: str = "", directory_name: str = "") -> List[Dict[str, Any]]:
    """
    Discover all running Docker containers and classify them based on name matching.
    
    This function queries Docker for all running containers, then classifies them
    as either "matches" (containers that match our search criteria) or "others" 
    (all other running containers). It searches for matches in two ways:
    1. Custom Docker container name (if provided in config)
    2. Directory name pattern in image names (vsc-{directory-name}-{hash})
    
    Args:
        container_name (str): The display container name (e.g., "God Container")
        custom_docker_container_name (str): Custom Docker container name from --name flag
        directory_name (str): Project directory name for image pattern matching
        
    Returns:
        List[Dict[str, Any]]: List of container dictionaries with the following structure:
            {
                'name': str,        # Docker assigned container name  
                'id': str,          # Container ID (short form)
                'image': str,       # Full image name
                'status': str,      # Container status (e.g., "Up 5 minutes")
                'created': str,     # Creation timestamp
                'is_match': bool    # True if matches search criteria
            }
            
    Example:
        containers = find_containers("God Container", "my-custom-name", "my-project")
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
        seen_container_ids = set()  # Track container IDs to avoid duplicates
        
        # Create search patterns
        search_pattern = normalize_container_name(container_name)
        directory_pattern = directory_name.lower().replace(' ', '-') if directory_name else ""
        
        print(f"🔍 Searching for containers...")
        if custom_docker_container_name:
            print(f"   - Custom name: '{custom_docker_container_name}'")
        if directory_pattern:
            print(f"   - Directory pattern: 'vsc-{directory_pattern}-*'")
        print(f"   - Fallback pattern: '{search_pattern}'")
        
        for line in lines:
            if line.strip():
                parts = line.split('|')
                
                if len(parts) >= 5:
                    name, container_id, image, status, created = parts[0], parts[1], parts[2], parts[3], parts[4]
                    
                    # Skip if we've already seen this container ID
                    if container_id in seen_container_ids:
                        continue
                    seen_container_ids.add(container_id)
                    
                    # Check for matches using multiple criteria
                    is_match = False
                    
                    # Priority 1: Match custom Docker container name (exact match)
                    if custom_docker_container_name and name == custom_docker_container_name:
                        is_match = True
                        print(f"✅ Found custom name match: {name}")
                    
                    # Priority 2: Match directory pattern in image name  
                    elif directory_pattern and f'vsc-{directory_pattern}-' in image.lower():
                        is_match = True
                        print(f"✅ Found directory pattern match: {image}")
                    
                    # Priority 3: Fallback to container name pattern in image
                    elif search_pattern in image.lower() and 'vsc-' in image.lower():
                        is_match = True
                        print(f"✅ Found fallback pattern match: {image}")
                    
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
                    
                    # Skip if we've already seen this container ID
                    if container_id in seen_container_ids:
                        continue
                    seen_container_ids.add(container_id)
                    
                    # Apply same matching logic
                    is_match = False
                    if custom_docker_container_name and name == custom_docker_container_name:
                        is_match = True
                    elif directory_pattern and f'vsc-{directory_pattern}-' in image.lower():
                        is_match = True
                    elif search_pattern in image.lower() and 'vsc-' in image.lower():
                        is_match = True
                    
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
