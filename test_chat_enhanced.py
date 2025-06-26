#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for the enhanced chat module

This script demonstrates how to use the chat_enhanced.py module to interact with OpenAI's GPT-4o,
showcasing conversation history, rate limiting, and other improvements.
"""

import os
import sys
import argparse
import uuid

# Import the enhanced chat module
from chat_enhanced import get_bot_response, ChatEngine, ConversationManager


def main():
    """
    Main function to test the enhanced chat module functionality.
    """
    parser = argparse.ArgumentParser(description="Test the enhanced chat module with OpenAI GPT-4o")
    parser.add_argument("--api-key", help="OpenAI API key (if not set in environment)")
    parser.add_argument("--class-mode", action="store_true", help="Use ChatEngine class instead of direct function")
    parser.add_argument("--session", help="Session ID for conversation history (default: random UUID)")
    parser.add_argument("--no-history", action="store_true", help="Disable conversation history saving")
    args = parser.parse_args()
    
    # Set API key if provided
    if args.api_key:
        os.environ["OPENAI_API_KEY"] = args.api_key
    
    # Check if API key is available
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please set it or provide it with --api-key argument.")
        return 1
    
    # Generate or use provided session ID
    session_id = args.session if args.session else str(uuid.uuid4())
    
    print("\n===== Enhanced OpenAI GPT-4o Chat Test =====\n")
    print(f"Session ID: {session_id}")
    print("Type 'exit', 'quit', or Ctrl+C to end the conversation.")
    print("Type 'clear' to clear conversation history.")
    print("Type 'help' to see all available commands.\n")
    
    # Initialize ChatEngine or ConversationManager
    chat_engine = None
    conversation = None
    
    if args.class_mode:
        config = {
            'openai_api_key': os.environ.get("OPENAI_API_KEY"),
            'openai_model': 'gpt-4o',
            'temperature': 0.7,
            'max_tokens': 500,
            'assistant_name': 'Insurance Assistant',
            'use_retrieval': False,
            'session_id': session_id,
            'system_prompt': "You are {assistant_name}, a helpful, friendly, and conversational AI assistant. "
                             "The current date and time is {current_time}. "
                             "Be concise but informative in your responses. If you don't know something, admit it. "
                             "Avoid harmful, unethical, or illegal content."
        }
        chat_engine = ChatEngine(config)
        print("Using ChatEngine class mode\n")
    else:
        conversation = ConversationManager(session_id)
        print("Using direct function mode with ConversationManager\n")
    
    # Main conversation loop
    try:
        while True:
            # Get user input
            user_input = input("You: ")
            
            # Process commands
            if user_input.lower() in ["exit", "quit"]:
                print("\nExiting chat. Goodbye!")
                break
                
            elif user_input.lower() == "clear":
                if args.class_mode and chat_engine:
                    chat_engine.clear_conversation()
                elif conversation:
                    conversation.clear_history()
                print("\nConversation history cleared.\n")
                continue
                
            elif user_input.lower() == "help":
                print("\nAvailable commands:")
                print("  exit, quit - End the conversation")
                print("  clear - Clear conversation history")
                print("  help - Show this help message\n")
                continue
            
            # Get response based on mode
            if args.class_mode and chat_engine:
                response = chat_engine.process(user_input)
            else:
                response = get_bot_response(user_input, None, session_id, conversation)
            
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