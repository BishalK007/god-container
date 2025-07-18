# This is a helper python script to setup and connect to devcontainer
import argparse
import subprocess
import os
from InquirerPy import inquirer
from utils import utils
from configure import handle_user, handle_waypipe, handle_add_feature, handle_add_programs

script_path = os.path.dirname(os.path.abspath(__file__))
devcontainer_path = os.path.dirname(script_path)
print(f"Devcontainer root: {devcontainer_path}")



    
def handle_conf():
    data1 = utils.load_jsonc(f"{devcontainer_path}/templates/main.jsonc")

    # handle waypipe configuration
    data1 = handle_waypipe.handle_waypipe(data1, devcontainer_path)

    # Ask user for user configuration
    data1 = handle_user.handle_user(data1, devcontainer_path)

    # Ask user for dev-container features
    data1 = handle_add_feature.handle_add_feature(data1)

    # Ask user for programs
    data1 = handle_add_programs.handle_add_programs(data1)

    # Save the merged configuration
    utils.save_jsonc(f"{devcontainer_path}/devcontainer.json", data1)


def load_config():
    """Load configuration from .conf file"""
    conf_path = os.path.join(devcontainer_path, '.conf')
    config = {}
    
    if not os.path.exists(conf_path):
        print(f"Configuration file not found: {conf_path}")
        print("Please run with --conf first to configure the devcontainer")
        return None
    
    try:
        with open(conf_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
        return config
    except Exception as e:
        print(f"Error reading config file: {e}")
        return None


def find_containers(container_name):
    """Find running containers matching the container name"""
    try:
        # Get all running containers
        result = subprocess.run(['docker', 'ps', '--format', 'table {{.Names}}\t{{.ID}}\t{{.Image}}'], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print("Error running docker ps command")
            return []
        
        containers = []
        lines = result.stdout.strip().split('\n')[1:]  # Skip header
        
        for line in lines:
            if line.strip():
                parts = line.split('\t')
                if len(parts) >= 3:
                    name, container_id, image = parts[0], parts[1], parts[2]
                    # Look for containers that match the pattern (usually contain project name)
                    if 'vsc-' in name.lower() or container_name.lower().replace(' ', '-') in name.lower():
                        containers.append({
                            'name': name,
                            'id': container_id,
                            'image': image
                        })
        
        return containers
    except Exception as e:
        print(f"Error finding containers: {e}")
        return []


def handle_conn():
    """Handle connection to devcontainer"""
    # Load configuration
    config = load_config()
    if not config:
        return
    
    container_name = config.get('CONTAINER_NAME', 'devcontainer')
    remote_user = config.get('REMOTE_USER', 'vscode')
    
    print(f"Looking for containers matching: {container_name}")
    
    # Find matching containers
    containers = find_containers(container_name)
    
    if not containers:
        print("No running devcontainers found.")
        print("Make sure your devcontainer is running in VS Code.")
        return
    
    # If multiple containers, let user choose
    selected_container = None
    if len(containers) == 1:
        selected_container = containers[0]
        print(f"Found container: {selected_container['name']}")
    else:
        print(f"Found {len(containers)} matching containers:")
        choices = [f"{c['name']} (ID: {c['id'][:12]}) - {c['image']}" for c in containers]
        
        selection = inquirer.select(
            message="Select container to connect to:",
            choices=choices
        ).execute()
        
        # Find the selected container
        selected_index = choices.index(selection)
        selected_container = containers[selected_index]
    
    # Get current directory name for workspace path
    current_dir = os.path.basename(os.path.dirname(devcontainer_path))
    workspace_path = f"/workspaces/{current_dir}"
    
    # Build docker exec command
    docker_cmd = [
        'docker', 'exec', '-it',
        '--user', remote_user,
        '-w', workspace_path,
        selected_container['id'],
        'bash'
    ]
    
    print(f"Connecting to container {selected_container['name']} as user {remote_user}")
    print(f"Working directory: {workspace_path}")
    print("=" * 50)
    
    # Execute the command
    try:
        subprocess.run(docker_cmd)
    except KeyboardInterrupt:
        print("\nConnection closed.")
    except Exception as e:
        print(f"Error connecting to container: {e}")


def main():
    parser = argparse.ArgumentParser(description="Devcontainer setup and connect helper")
    parser.add_argument('--conf', action='store_true', help='Configure devcontainer.json file')
    parser.add_argument('--conn', action='store_true', help='Connect to running devcontainer')
    args = parser.parse_args()

    if args.conf:
        print("=== Configuring Devcontainer ===")
        handle_conf()
    elif args.conn:
        print("=== Connecting to Devcontainer ===")
        handle_conn()
    else:
        # Default behavior - show help
        parser.print_help()
        print("\nExample usage:")
        print("  python main.py --conf    # Configure devcontainer")
        print("  python main.py --conn    # Connect to running container")



if __name__ == "__main__":
    main()

'''
 - Ask for base
 - Ask for customfeatures(waypipe, pipewire, minikube)
 - Ask for user configuration
 - Ask for features
 - Save the configuration to devcontainer.json
'''