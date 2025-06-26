#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for the chat module

This script demonstrates how to use the chat.py module to interact with OpenAI's GPT-4o.
"""

import os
import sys
import argparse

# Import the chat module
from chat import get_bot_response
from chat_enhanced import ChatEngine


def main():
    """
    Main function to test the chat module functionality.
    """
    parser = argparse.ArgumentParser(description="Test the chat module with OpenAI GPT-4o")
    parser.add_argument("--api-key", help="OpenAI API key (if not set in environment)")
    parser.add_argument("--class-mode", action="store_true", help="Use ChatEngine class instead of direct function")
    args = parser.parse_args()
    
    # Set API key if provided
    if args.api_key:
        os.environ["OPENAI_API_KEY"] = args.api_key
    
    # Check if API key is available
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please set it or provide it with --api-key argument.")
        return 1
    
    print("\n===== OpenAI GPT-4o Chat Test =====\n")
    print("Type 'exit', 'quit', or Ctrl+C to end the conversation.\n")
    
    # Initialize ChatEngine if using class mode
    chat_engine = None
    if args.class_mode:
        config = {
            'openai_api_key': os.environ.get("OPENAI_API_KEY"),
            'openai_model': 'gpt-4o',
            'temperature': 0.7,
            'max_tokens': 500,
            'assistant_name': 'Insurance Assistant',
            'use_retrieval': False
        }
        chat_engine = ChatEngine(config)
        print("Using ChatEngine class mode\n")
    else:
        print("Using direct function mode\n")
    
    # Main conversation loop
    try:
        while True:
            # Get user input
            user_input = input("You: ")
            
            # Check for exit command
            if user_input.lower() in ["exit", "quit"]:
                print("\nExiting chat. Goodbye!")
                break
            
            # Get response based on mode
            if args.class_mode and chat_engine:
                response = chat_engine.process(user_input)
            else:
                response = get_bot_response(user_input)
            
            # Display response
            print(f"\nAssistant: {response}\n")
    
    except KeyboardInterrupt:
        print("\n\nExiting chat. Goodbye!")
    
    # Cleanup
    if args.class_mode and chat_engine:
        chat_engine.cleanup()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())