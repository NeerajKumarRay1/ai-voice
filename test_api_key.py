#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test OpenAI API Key

This script tests the OpenAI API key by making a simple API call using requests.
It verifies that the key is valid and working correctly without requiring the OpenAI package.
"""

import os
import sys
import time
import json
import logging
import argparse
import requests
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def get_api_key():
    """
    Get the OpenAI API key from environment variable or config file.
    
    Returns:
        str: The API key or None if not found
    """
    # Try environment variable first
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        return api_key
    
    # Try config file
    config_paths = ["config.json", "config_example.json"]
    for config_path in config_paths:
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                api_key = config.get("openai", {}).get("api_key")
                if api_key:
                    return api_key
        except Exception as e:
            logger.error(f"Error reading config file {config_path}: {str(e)}")
    
    return None


def test_api_key(api_key=None, model="gpt-3.5-turbo"):
    """
    Test the OpenAI API key by making a simple API call using requests.
    
    Args:
        api_key: The OpenAI API key (if None, will try to get from environment or config)
        model: The model to use for testing (default: gpt-3.5-turbo to save costs)
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not api_key:
        api_key = get_api_key()
    
    if not api_key:
        logger.error("No API key found. Please set the OPENAI_API_KEY environment variable or update config.json")
        return False
    
    # API endpoint
    url = "https://api.openai.com/v1/chat/completions"
    
    # Headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test message
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, this is a test message to verify my API key is working. Please respond with a short confirmation."}
        ],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    try:
        print(f"Testing OpenAI API with model: {model}")
        print("Sending test message...")
        
        # Record start time
        start_time = time.time()
        
        # Make API call
        response = requests.post(url, headers=headers, json=data)
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # Check response status
        if response.status_code == 200:
            # Parse response
            response_data = response.json()
            
            # Get response content
            content = response_data["choices"][0]["message"]["content"].strip()
            
            print(f"\nAPI Response (in {elapsed_time:.2f} seconds):")
            print(f"\n\"{content}\"\n")
            
            # Get usage information
            usage = response_data["usage"]
            print(f"Token Usage:")
            print(f"  Prompt tokens: {usage['prompt_tokens']}")
            print(f"  Completion tokens: {usage['completion_tokens']}")
            print(f"  Total tokens: {usage['total_tokens']}")
            
            logger.info(f"API test successful with model {model}")
            return True
        elif response.status_code == 401:
            logger.error(f"Authentication error: {response.text}")
            print(f"\nError: Invalid API key or authentication issue")
            print(f"Please check your API key and try again")
            return False
        elif response.status_code == 429:
            logger.error(f"Rate limit error: {response.text}")
            print(f"\nError: Rate limit exceeded")
            print(f"Your account has hit the rate limit. Please try again later or check your rate limits.")
            return False
        else:
            logger.error(f"API error: {response.status_code} - {response.text}")
            print(f"\nError: OpenAI API error")
            print(f"Status Code: {response.status_code}")
            print(f"Message: {response.text}")
            return False
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        print(f"\nError: Could not connect to OpenAI API")
        print(f"Message: {str(e)}")
        return False
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"\nUnexpected error: {str(e)}")
        return False


def main():
    """
    Main function to test the OpenAI API key.
    """
    parser = argparse.ArgumentParser(description="Test OpenAI API Key")
    parser.add_argument("--api-key", "-k", help="OpenAI API Key (if not provided, will use environment variable or config file)")
    parser.add_argument("--model", "-m", default="gpt-3.5-turbo", help="Model to use for testing (default: gpt-3.5-turbo)")
    
    args = parser.parse_args()
    
    print("\n===== OpenAI API Key Test =====\n")
    
    success = test_api_key(args.api_key, args.model)
    
    print("\n===== Test Summary =====\n")
    if success:
        print("✓ API key is valid and working correctly")
        print("  You can now use the chat module with this API key")
    else:
        print("✗ API key test failed")
        print("  Please check the error message above and try again")
    
    print("\n" + "=" * 30 + "\n")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())