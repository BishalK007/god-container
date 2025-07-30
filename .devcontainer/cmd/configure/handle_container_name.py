#!/usr/bin/env python3
"""
Handle Container Name Configuration

This module handles the configuration of the devcontainer name,
allowing users to customize the container name that appears in VS Code
and other devcontainer tools.

Features:
- Interactive name input with validation
- Default fallback to "God Container"
- Name sanitization for devcontainer compatibility
- Updates configuration with user-specified name

Author: Devcontainer God Project
Created: 2025-07-30
"""

from InquirerPy import inquirer
from typing import Dict, Any, Tuple
import re


def sanitize_container_name(name: str) -> str:
    """
    Sanitize container name for devcontainer compatibility.
    
    Args:
        name: Raw container name input
        
    Returns:
        Sanitized container name safe for devcontainers
    """
    # Remove invalid characters and normalize whitespace
    sanitized = re.sub(r'[^\w\s\-_.]', '', name)
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    # Ensure it's not empty
    if not sanitized:
        return "God Container"
    
    return sanitized


def sanitize_docker_container_name(name: str) -> str:
    """
    Sanitize Docker container name according to Docker naming rules.
    Docker container names can only contain [a-zA-Z0-9-].
    
    Args:
        name: Raw Docker container name input
        
    Returns:
        Sanitized Docker container name safe for Docker
    """
    # Remove all characters except alphanumeric and hyphens
    sanitized = re.sub(r'[^a-zA-Z0-9\-]', '-', name)
    
    # Remove multiple consecutive hyphens
    sanitized = re.sub(r'-+', '-', sanitized)
    
    # Remove leading/trailing hyphens
    sanitized = sanitized.strip('-')
    
    # Ensure it's not empty
    if not sanitized:
        return "my-container"
    
    return sanitized


def handle_container_name(data: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    """
    Handle container name configuration workflow.
    
    Args:
        data: Existing devcontainer configuration
        
    Returns:
        Tuple of (updated devcontainer configuration, custom docker container name)
    """
    print("🏷️  Configure container name...")
    print("📝 This name will appear in VS Code and devcontainer tools")
    
    current_name = data.get("name", "God Container")
    
    # Ask if user wants to set a custom Docker container name
    use_custom_name = inquirer.confirm(
        message="Do you want to set a custom Docker container name? (y/N)",
        default=False,
        instruction="\nThis will add --name argument to runArgs for easier container identification"
    ).execute()
    
    custom_docker_container_name = None
    if use_custom_name:
        # Ask user for custom Docker container name
        custom_docker_container_name = inquirer.text(
            message="Enter custom Docker container name:",
            default="",
            validate=lambda text: len(text.strip()) > 0 if text.strip() else True,
            invalid_message="Container name cannot be empty if provided",
            instruction="\nThis name will be used for 'docker run --name=<name>' (only [a-zA-Z0-9-] allowed)"
        ).execute()
        
        if custom_docker_container_name.strip():
            original_name = custom_docker_container_name.strip()
            custom_docker_container_name = sanitize_docker_container_name(original_name)
            
            if custom_docker_container_name != original_name:
                print(f"⚠️  Docker name sanitized: '{original_name}' → '{custom_docker_container_name}'")
            
            # Add --name argument to runArgs
            run_args = data.get("runArgs", [])
            # Remove any existing --name arguments
            run_args = [arg for arg in run_args if not arg.startswith("--name=")]
            # Add new --name argument
            run_args.append(f"--name={custom_docker_container_name}")
            data["runArgs"] = run_args
            print(f"✅ Custom Docker container name set to: '{custom_docker_container_name}'")
        else:
            custom_docker_container_name = None
            print("📝 No custom Docker container name provided")
    
    # Ask user for display name (always required)
    container_name = inquirer.text(
        message="Enter container display name:",
        default=current_name,
        validate=lambda text: len(text.strip()) > 0,
        invalid_message="Container display name cannot be empty",
        instruction="\nThis name appears in VS Code and devcontainer tools"
    ).execute()
    
    # Sanitize the display name
    sanitized_name = sanitize_container_name(container_name)
    
    if sanitized_name != container_name:
        print(f"⚠️  Name sanitized: '{container_name}' → '{sanitized_name}'")
    
    # Update the configuration
    data["name"] = sanitized_name
    
    print(f"✅ Container display name set to: '{sanitized_name}'")
    
    return data, custom_docker_container_name or ""


def validate_container_name(name: str) -> bool:
    """
    Validate if a container name is acceptable.
    
    Args:
        name: Container name to validate
        
    Returns:
        True if name is valid, False otherwise
    """
    if not name or not name.strip():
        return False
    
    # Check for reasonable length
    if len(name) > 100:
        return False
    
    # Basic character validation (allowing common punctuation)
    if not re.match(r'^[\w\s\-_.]+$', name):
        return False
    
    return True
