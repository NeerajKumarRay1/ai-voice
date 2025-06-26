#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Update OpenAI API Key

This script updates the OpenAI API key in environment variables and configuration files.
It can be used to change the API key without modifying the source code.
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def update_environment_variable(api_key):
    """
    Update the OPENAI_API_KEY environment variable.
    
    Args:
        api_key: The OpenAI API key
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Set environment variable for current process
        os.environ["OPENAI_API_KEY"] = api_key
        logger.info("Updated OPENAI_API_KEY environment variable for current process")
        
        # For Windows, also set it at the system level (requires admin privileges)
        if os.name == 'nt':
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS)
                winreg.SetValueEx(key, "OPENAI_API_KEY", 0, winreg.REG_SZ, api_key)
                winreg.CloseKey(key)
                logger.info("Updated OPENAI_API_KEY in Windows registry (user level)")
                print("NOTE: You may need to log out and log back in for the environment variable to take effect system-wide.")
            except Exception as e:
                logger.warning(f"Could not update Windows registry: {str(e)}")
                logger.warning("The environment variable will only be available for the current process.")
        
        return True
    except Exception as e:
        logger.error(f"Error updating environment variable: {str(e)}")
        return False


def update_config_file(api_key, config_path):
    """
    Update the API key in a configuration file.
    
    Args:
        api_key: The OpenAI API key
        config_path: Path to the configuration file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if file exists
        if not os.path.exists(config_path):
            logger.warning(f"Configuration file {config_path} not found")
            return False
        
        # Load existing config
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Update API key
        if "openai" not in config:
            config["openai"] = {}
        
        config["openai"]["api_key"] = api_key
        
        # Write updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Updated API key in configuration file {config_path}")
        return True
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing configuration file: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error updating configuration file: {str(e)}")
        return False


def create_config_file(api_key, config_path):
    """
    Create a new configuration file with the API key.
    
    Args:
        api_key: The OpenAI API key
        config_path: Path to the configuration file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create default config
        config = {
            "openai": {
                "api_key": api_key,
                "model": "gpt-4o",
                "temperature": 0.7,
                "max_tokens": 500
            },
            "rate_limiting": {
                "max_retries": 5,
                "initial_backoff": 1,
                "backoff_multiplier": 2,
                "max_backoff": 60
            },
            "conversation": {
                "max_history": 10,
                "save_history": True
            }
        }
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
        
        # Write config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Created new configuration file {config_path} with API key")
        return True
    except Exception as e:
        logger.error(f"Error creating configuration file: {str(e)}")
        return False


def main():
    """
    Main function to update the OpenAI API key.
    """
    parser = argparse.ArgumentParser(description="Update OpenAI API Key")
    parser.add_argument("api_key", help="OpenAI API Key")
    parser.add_argument("--config", "-c", default="config.json", help="Path to configuration file")
    parser.add_argument("--create", "-n", action="store_true", help="Create configuration file if it doesn't exist")
    
    args = parser.parse_args()
    
    # Validate API key format (basic check)
    if not args.api_key.startswith("sk-"):
        logger.warning("Warning: API key doesn't start with 'sk-'. This may not be a valid OpenAI API key.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return 1
    
    # Update environment variable
    env_success = update_environment_variable(args.api_key)
    
    # Update or create configuration file
    config_success = False
    if os.path.exists(args.config):
        config_success = update_config_file(args.api_key, args.config)
    elif args.create:
        config_success = create_config_file(args.api_key, args.config)
    else:
        logger.warning(f"Configuration file {args.config} not found. Use --create to create it.")
    
    # Print summary
    print("\n===== Update Summary =====\n")
    print(f"Environment Variable: {'✓ Updated' if env_success else '✗ Failed'}")
    print(f"Configuration File: {'✓ Updated' if config_success else '✗ Not Updated'}")
    print("\nTo use the new API key in your scripts:")
    print("1. For new terminal sessions: The environment variable will be available")
    print("2. For current terminal session: The environment variable is already set")
    print("3. For configuration-based applications: The config file has been updated")
    
    return 0 if env_success or config_success else 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: API key is required")
        print("Usage: python update_api_key.py <api_key> [--config CONFIG_PATH] [--create]")
        sys.exit(1)
    
    sys.exit(main())