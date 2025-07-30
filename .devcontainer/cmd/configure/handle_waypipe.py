"""
Waypipe Configuration Module

This module handles the configuration of Waypipe for GUI application support
in devcontainers. Waypipe enables forwarding of Wayland applications from
the container to the host display server, allowing GUI applications to run
seamlessly in containerized environments.

Features:
- Interactive Waypipe setup
- Template-based configuration merging
- Linux host validation
- Socket and display environment setup

Author: Devcontainer God Project
Created: 2025-07-30
"""

from utils import utils
from InquirerPy import inquirer


def handle_waypipe(data1, devcontainer_path):
    """
    Handle Waypipe configuration for GUI application support.
    
    This function prompts the user to decide whether to enable Waypipe
    support in their devcontainer. If enabled, it merges the Waypipe
    template configuration which includes:
    - Environment variables for Wayland display
    - Volume mounts for socket sharing
    - Post-creation commands for Waypipe setup
    
    Args:
        data1 (dict): Current devcontainer configuration
        devcontainer_path (str): Path to devcontainer directory
        
    Returns:
        dict: Updated configuration with Waypipe settings if enabled
    """
    # Ask user for waypipe configuration
    answer = inquirer.select(
        message="Do you want Waypipe support for GUI applications?",
        choices=[
            "Yes - Enable GUI forwarding (Linux hosts only)",
            "No - Container only environment"
        ]
    ).execute()
    
    print(f"Selected: {answer}")
    
    if answer.startswith("Yes"):
        print("✅ Waypipe will be added to the configuration.")
        print("📺 This enables GUI applications in your devcontainer.")
        return utils.merge_jsonc_data(
            data1,
            utils.load_jsonc(f"{devcontainer_path}/templates/waypipe.jsonc")
        )
    else:
        print("⏭️  Skipping Waypipe configuration.")
        return data1