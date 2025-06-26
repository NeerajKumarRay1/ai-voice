#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Verify OpenAI API Key

This script verifies that the OpenAI API key is correctly set in the environment
and configuration files. It does not make any actual API calls to OpenAI.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def check_environment_variable():
    """
    Check if the OPENAI_API_KEY environment variable is set.
    
    Returns:
        tuple: (bool, str) - (is_set, api_key_masked)
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        # Mask the API key for security
        masked_key = f"{api_key[:7]}...{api_key[-4:]}" if len(api_key) > 11 else "***masked***"
        return True, masked_key
    return False, None


def check_config_file(config_path):
    """
    Check if the API key is set in the configuration file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        tuple: (bool, str) - (is_set, api_key_masked)
    """
    try:
        if not os.path.exists(config_path):
            logger.warning(f"Configuration file {config_path} not found")
            return False, None
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        api_key = config.get("openai", {}).get("api_key")
        if api_key:
            # Mask the API key for security
            masked_key = f"{api_key[:7]}...{api_key[-4:]}" if len(api_key) > 11 else "***masked***"
            return True, masked_key
        return False, None
    except Exception as e:
        logger.error(f"Error checking configuration file: {str(e)}")
        return False, None


def main():
    """
    Main function to verify the OpenAI API key.
    """
    print("\n===== OpenAI API Key Verification =====\n")
    
    # Check environment variable
    env_set, env_key = check_environment_variable()
    print(f"Environment Variable (OPENAI_API_KEY):")
    if env_set:
        print(f"  ✓ Set: {env_key}")
    else:
        print(f"  ✗ Not set")
    
    # Check default config file
    default_config = "config.json"
    config_set, config_key = check_config_file(default_config)
    print(f"\nDefault Configuration File ({default_config}):")
    if config_set:
        print(f"  ✓ Set: {config_key}")
    else:
        print(f"  ✗ Not set or file not found")
    
    # Check example config file
    example_config = "config_example.json"
    example_set, example_key = check_config_file(example_config)
    print(f"\nExample Configuration File ({example_config}):")
    if example_set:
        print(f"  ✓ Set: {example_key}")
    else:
        print(f"  ✗ Not set or file not found")
    
    # Summary
    print("\n===== Summary =====\n")
    if env_set or config_set or example_set:
        print("✓ OpenAI API key is available from at least one source")
        print("  The chat module should be able to use the API key")
    else:
        print("✗ OpenAI API key is not available from any source")
        print("  The chat module will not be able to make API calls")
        print("  Please set the API key using update_api_key.py")
    
    print("\n" + "=" * 40 + "\n")
    
    return 0 if env_set or config_set or example_set else 1


if __name__ == "__main__":
    sys.exit(main())