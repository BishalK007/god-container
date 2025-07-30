"""
User Interface Module for Container Selection

This module provides a clean, organized interface for users to select
Docker containers from a categorized list. It uses InquirerPy to create
an interactive selection menu with proper visual organization and
non-selectable headers.

Author: Devcontainer God Project
Created: 2025-07-30
"""

from typing import List, Dict, Any, Optional
from InquirerPy import inquirer
from InquirerPy.separator import Separator


def create_container_selection_interface(matches: List[Dict[str, Any]], 
                                       others: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Create an interactive container selection interface with organized categories.
    
    This function presents containers in two organized sections:
    1. "Matches" - Containers that match the search pattern (prioritized)
    2. "Other Containers" - All other running containers
    
    The interface uses visual indicators and separators to clearly distinguish
    between categories while preventing accidental selection of headers.
    
    Args:
        matches (List[Dict[str, Any]]): Containers matching the search pattern
        others (List[Dict[str, Any]]): Other running containers
        
    Returns:
        Optional[Dict[str, Any]]: Selected container dictionary, or None if selection failed
        
    Example:
        matches = [container1, container2]
        others = [container3, container4]
        selected = create_container_selection_interface(matches, others)
        if selected:
            print(f"User selected: {selected['name']}")
    """
    # Build choices list with proper separators
    choices = []
    
    # Add matches section if any exist
    if matches:
        choices.append(Separator("=== Matches ==="))
        for container in matches:
            choice_text = _format_container_choice(container, "🎯")
            choices.append(choice_text)
    
    # Add others section if any exist
    if others:
        if matches:  # Add visual separator between sections
            choices.append(Separator())
        choices.append(Separator("=== Other Containers ==="))
        for container in others:
            choice_text = _format_container_choice(container, "📦")
            choices.append(choice_text)
    
    # Create mapping from choice text to container object
    choice_to_container = _create_choice_mapping(choices, matches, others)
    
    # Present selection interface to user
    try:
        selection = inquirer.select(
            message="Select container to connect to:",
            choices=choices,
            instruction="[Use ↑↓ to navigate, Enter to select]"
        ).execute()
        
        # Return the selected container
        return choice_to_container.get(selection)
    except (KeyboardInterrupt, EOFError):
        print("\n👋 Selection cancelled.")
        return None


def _format_container_choice(container: Dict[str, Any], icon: str) -> str:
    """
    Format a container entry for display in the selection interface.
    
    Args:
        container (Dict[str, Any]): Container dictionary with name, image, status, created
        icon (str): Visual icon to prepend (e.g., "🎯" for matches, "📦" for others)
        
    Returns:
        str: Formatted choice string for display
    """
    return f"{icon} {container['name']} | {container['image'][:50]}... | {container['status']} | {container['created']}"


def _create_choice_mapping(choices: List, matches: List[Dict[str, Any]], 
                          others: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Create mapping from choice strings to container objects.
    
    This function creates a lookup dictionary that maps the formatted choice
    strings back to their corresponding container objects, enabling easy
    retrieval of the selected container.
    
    Args:
        choices (List): Complete list of choices including separators
        matches (List[Dict[str, Any]]): Matching containers
        others (List[Dict[str, Any]]): Other containers
        
    Returns:
        Dict[str, Dict[str, Any]]: Mapping from choice text to container object
    """
    choice_to_container = {}
    match_index = 0
    other_index = 0
    
    for choice in choices:
        if isinstance(choice, str):  # Skip Separator objects
            if choice.startswith("🎯"):
                choice_to_container[choice] = matches[match_index]
                match_index += 1
            elif choice.startswith("📦"):
                choice_to_container[choice] = others[other_index]
                other_index += 1
    
    return choice_to_container
