#!/usr/bin/env python3
"""
Devcontainer God - Main Entry Point

This is the main script for the Devcontainer God project, a comprehensive
tool for setting up and connecting to VS Code devcontainers with advanced
features like Waypipe support, automated package installation, and intelligent
container discovery.

Features:
- Interactive devcontainer configuration with templates
- Waypipe integration for GUI applications on Linux
- Automated package discovery and installation
- Smart container detection and connection
- User and permission management
- Feature integration from devcontainer marketplace

Usage:
    python main.py --conf    # Configure devcontainer.json
    python main.py --conn    # Connect to running container

Author: Devcontainer God Project
Created: 2025-07-30
Version: 1.0.0
"""

import argparse
import os
from utils import utils
from configure import handle_user, handle_waypipe, handle_add_feature, handle_add_programs
from core.connection import handle_container_connection

# Project paths
script_path = os.path.dirname(os.path.abspath(__file__))
devcontainer_path = os.path.dirname(script_path)
print(f"Devcontainer root: {devcontainer_path}")


def handle_configuration() -> None:
    """
    Handle the complete devcontainer configuration workflow.
    
    This function orchestrates the entire configuration process:
    1. Load base template (main.jsonc)
    2. Configure Waypipe for GUI applications (Linux only)
    3. Set up user permissions and UID/GID mapping
    4. Add devcontainer features from marketplace
    5. Install additional packages via apt
    6. Save final configuration to devcontainer.json
    
    The configuration is built incrementally by merging JSON templates
    and user preferences into a final devcontainer.json file.
    """
    print("🔧 Starting devcontainer configuration...")
    
    # Start with base template
    data = utils.load_jsonc(f"{devcontainer_path}/templates/main.jsonc")
    
    # Step 1: Configure Waypipe for GUI applications
    print("\n📺 Configuring Waypipe (GUI support)...")
    data = handle_waypipe.handle_waypipe(data, devcontainer_path)
    
    # Step 2: Configure user settings and permissions
    print("\n� Configuring user settings...")
    data = handle_user.handle_user(data, devcontainer_path)
    
    # Step 3: Add devcontainer features
    print("\n🔧 Adding devcontainer features...")
    data = handle_add_feature.handle_add_feature(data)
    
    # Step 4: Install additional programs
    print("\n📦 Installing additional programs...")
    data = handle_add_programs.handle_add_programs(data)
    
    # Step 5: Save final configuration
    print("\n💾 Saving configuration...")
    utils.save_jsonc(f"{devcontainer_path}/devcontainer.json", data)
    
    print("✅ Devcontainer configuration completed successfully!")
    print(f"📄 Configuration saved to: {devcontainer_path}/devcontainer.json")


def main() -> None:
    """
    Main entry point for the Devcontainer God application.
    
    Parses command line arguments and routes to appropriate handlers:
    - --conf: Launch configuration wizard
    - --conn: Connect to running devcontainer
    - No args: Show help and usage examples
    """
    parser = argparse.ArgumentParser(
        description="Devcontainer God - Advanced devcontainer management tool",
        epilog="""
Examples:
  %(prog)s --conf    Configure a new devcontainer with interactive wizard
  %(prog)s --conn    Connect to a running devcontainer with smart detection
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--conf', 
        action='store_true', 
        help='Launch interactive configuration wizard to set up devcontainer.json'
    )
    
    parser.add_argument(
        '--conn', 
        action='store_true', 
        help='Connect to running devcontainer with intelligent container detection'
    )
    
    args = parser.parse_args()
    
    if args.conf:
        print("=== Devcontainer Configuration Wizard ===")
        handle_configuration()
    elif args.conn:
        print("=== Devcontainer Connection Manager ===")
        handle_container_connection(devcontainer_path)
    else:
        # Show help when no arguments provided
        parser.print_help()
        print("\n" + "="*60)
        print("🚀 Welcome to Devcontainer God!")
        print("📖 Get started by running one of the commands above.")
        print("💡 Use --conf first to set up your devcontainer configuration.")


if __name__ == "__main__":
    main()