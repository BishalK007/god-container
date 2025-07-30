"""
Utility Functions for JSON Configuration Management

This module provides utility functions for handling JSON with comments (JSONC)
files and merging configuration data. It includes special handling for
devcontainer-specific fields like postCreateCommand concatenation.

Author: Devcontainer God Project
Created: 2025-07-30
"""

import commentjson
from deepmerge import always_merger
from typing import Dict, Any


def load_jsonc(path: str) -> Dict[str, Any]:
    """
    Load a JSON with comments (JSONC) file.
    
    Args:
        path (str): Path to the JSONC file
        
    Returns:
        Dict[str, Any]: Parsed JSON data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    with open(path, 'r') as f:
        return commentjson.load(f)


def merge_jsonc_data(data1: Dict[str, Any], data2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two JSON configuration objects with special handling for devcontainer fields.
    
    This function performs a deep merge of two configuration dictionaries with
    special logic for the 'postCreateCommand' field, which gets concatenated
    rather than overwritten to preserve multiple setup commands.
    
    Args:
        data1 (Dict[str, Any]): Base configuration data
        data2 (Dict[str, Any]): Configuration data to merge in
        
    Returns:
        Dict[str, Any]: Merged configuration with combined commands
        
    Example:
        base = {"name": "container", "postCreateCommand": "apt update"}
        addon = {"features": {"node": {}}, "postCreateCommand": "npm install"}
        result = merge_jsonc_data(base, addon)
        # result["postCreateCommand"] == "apt update && npm install"
    """
    data1_cpy = data1.copy()
    data2_cpy = data2.copy()
    merged = always_merger.merge(data1_cpy, data2_cpy)

    # Special handling for postCreateCommand concatenation
    if "postCreateCommand" in data1 and "postCreateCommand" in data2:
        cmd1 = data1["postCreateCommand"].strip()
        cmd2 = data2["postCreateCommand"].strip()
        print(f"📋 Merging commands:")
        print(f"   Base: {cmd1}")
        print(f"   Addition: {cmd2}")
        
        # Concatenate with ' && ' if both are non-empty
        if cmd1 and cmd2:
            merged["postCreateCommand"] = f"{cmd1} && {cmd2}"
            print(f"   Result: {merged['postCreateCommand']}")
        else:
            merged["postCreateCommand"] = cmd1 or cmd2
            
    return merged


def save_jsonc(path: str, data: Dict[str, Any]) -> None:
    """
    Save data to a JSON with comments (JSONC) file with proper formatting.
    
    Args:
        path (str): Path where to save the file
        data (Dict[str, Any]): Data to save
        
    Raises:
        PermissionError: If unable to write to the specified path
        OSError: If there's an I/O error during writing
    """
    with open(path, 'w') as f:
        commentjson.dump(data, f, indent=4)