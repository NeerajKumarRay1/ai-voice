#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration Demo for Chat Module

This script demonstrates how to load and use configuration settings
for the chat module from a JSON file.
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def load_config(config_path="config_example.json"):
    """
    Load configuration from a JSON file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        dict: Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            logger.info(f"Loaded configuration from {config_path}")
            return config
    except FileNotFoundError:
        logger.error(f"Configuration file {config_path} not found")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing configuration file: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error loading configuration: {str(e)}")
        return None


def display_config(config):
    """
    Display the configuration settings.
    
    Args:
        config: Configuration dictionary
    """
    if not config:
        print("No configuration loaded.")
        return
    
    print("\n===== Configuration Settings =====\n")
    
    # OpenAI settings
    print("OpenAI Settings:")
    openai_config = config.get("openai", {})
    print(f"  Model: {openai_config.get('model', 'Not specified')}")
    print(f"  Temperature: {openai_config.get('temperature', 'Not specified')}")
    print(f"  Max Tokens: {openai_config.get('max_tokens', 'Not specified')}")
    
    # Format system prompt with current time
    system_prompt = openai_config.get("system_prompt", "Not specified")
    if "{current_time}" in system_prompt:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        system_prompt = system_prompt.replace("{current_time}", current_time)
    print(f"  System Prompt: {system_prompt[:50]}..." if len(system_prompt) > 50 else f"  System Prompt: {system_prompt}")
    
    # Rate limiting settings
    print("\nRate Limiting Settings:")
    rate_config = config.get("rate_limiting", {})
    print(f"  Max Retries: {rate_config.get('max_retries', 'Not specified')}")
    print(f"  Initial Backoff: {rate_config.get('initial_backoff', 'Not specified')} seconds")
    print(f"  Backoff Multiplier: {rate_config.get('backoff_multiplier', 'Not specified')}")
    print(f"  Max Backoff: {rate_config.get('max_backoff', 'Not specified')} seconds")
    
    # Conversation settings
    print("\nConversation Settings:")
    conv_config = config.get("conversation", {})
    print(f"  Max History: {conv_config.get('max_history', 'Not specified')} messages")
    print(f"  Save History: {conv_config.get('save_history', 'Not specified')}")
    print(f"  History Directory: {conv_config.get('history_dir', 'Not specified')}")
    
    # Retrieval settings
    print("\nRetrieval Settings:")
    retrieval_config = config.get("retrieval", {})
    print(f"  Enabled: {retrieval_config.get('enabled', 'Not specified')}")
    print(f"  Knowledge Base Path: {retrieval_config.get('knowledge_base_path', 'Not specified')}")
    print(f"  Top K: {retrieval_config.get('top_k', 'Not specified')}")
    print(f"  Similarity Threshold: {retrieval_config.get('similarity_threshold', 'Not specified')}")
    
    # Logging settings
    print("\nLogging Settings:")
    logging_config = config.get("logging", {})
    print(f"  Level: {logging_config.get('level', 'Not specified')}")
    print(f"  File: {logging_config.get('file', 'Not specified')}")
    print(f"  Console: {logging_config.get('console', 'Not specified')}")
    
    print("\n" + "=" * 35 + "\n")


def main():
    """
    Main function to demonstrate configuration loading.
    """
    # Check if a config file was specified
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = "config_example.json"
    
    # Load configuration
    config = load_config(config_path)
    
    if config:
        # Display configuration
        display_config(config)
        
        # Demonstrate how to use configuration values
        print("\nDemonstrating configuration usage:\n")
        
        # Example: Setting up OpenAI client with config values
        openai_config = config.get("openai", {})
        model = openai_config.get("model", "gpt-4o")
        temperature = openai_config.get("temperature", 0.7)
        max_tokens = openai_config.get("max_tokens", 500)
        
        print(f"Would initialize OpenAI client with model={model}, temperature={temperature}, max_tokens={max_tokens}")
        
        # Example: Setting up conversation manager with config values
        conv_config = config.get("conversation", {})
        max_history = conv_config.get("max_history", 10)
        save_history = conv_config.get("save_history", True)
        history_dir = conv_config.get("history_dir", "conversation_history")
        
        print(f"Would initialize ConversationManager with max_history={max_history}, save_history={save_history}, history_dir={history_dir}")
        
        # Example: Setting up logging with config values
        logging_config = config.get("logging", {})
        log_level = logging_config.get("level", "INFO")
        log_file = logging_config.get("file", "chat.log")
        log_console = logging_config.get("console", True)
        
        print(f"Would configure logging with level={log_level}, file={log_file}, console={log_console}")
    else:
        print(f"Failed to load configuration from {config_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())