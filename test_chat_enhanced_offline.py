#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Offline test script for demonstrating conversation management

This script implements a simple conversation manager and demonstrates
conversation history features without making actual API calls to OpenAI.
"""

import os
import sys
import argparse
import uuid
import json
from pathlib import Path
from datetime import datetime


class SimpleConversationManager:
    """
    A simplified conversation manager for demonstration purposes.
    """
    
    def __init__(self, session_id, max_history=10, save_history=True):
        """
        Initialize the conversation manager.
        
        Args:
            session_id: Unique identifier for this conversation session
            max_history: Maximum number of messages to keep in history
            save_history: Whether to save history to disk
        """
        self.session_id = session_id
        self.max_history = max_history
        self.save_history = save_history
        self.messages = []
        self.history_dir = Path("conversation_history")
        
        # Create history directory if it doesn't exist
        if self.save_history:
            self.history_dir.mkdir(exist_ok=True)
        
        # Load existing history if available
        self._load_history()
    
    def add_message(self, role, content):
        """
        Add a message to the conversation history.
        
        Args:
            role: Message role ("system", "user", or "assistant")
            content: Message content
        """
        self.messages.append({"role": role, "content": content})
        
        # Trim history if it exceeds max_history
        if len(self.messages) > self.max_history + 1:  # +1 for system message
            system_messages = [m for m in self.messages if m["role"] == "system"]
            non_system = [m for m in self.messages if m["role"] != "system"]
            
            # Keep only the most recent messages
            keep_count = self.max_history - len(system_messages)
            recent_messages = non_system[-keep_count:] if keep_count > 0 else []
            
            # Reconstruct messages list with system messages first, then recent messages
            self.messages = system_messages + recent_messages
        
        # Save updated history
        if self.save_history:
            self._save_history()
    
    def get_messages(self):
        """
        Get the current conversation messages.
        
        Returns:
            List of message dictionaries
        """
        return self.messages
    
    def clear_history(self, keep_system=True):
        """
        Clear the conversation history.
        
        Args:
            keep_system: Whether to keep system messages
        """
        if keep_system:
            self.messages = [m for m in self.messages if m["role"] == "system"]
        else:
            self.messages = []
        
        # Save updated (empty) history
        if self.save_history:
            self._save_history()
        print(f"Cleared conversation history for session {self.session_id}")
    
    def _get_history_path(self):
        """
        Get the path to the history file for this session.
        
        Returns:
            Path object for the history file
        """
        return self.history_dir / f"{self.session_id}.json"
    
    def _load_history(self):
        """
        Load conversation history from disk if it exists.
        """
        if not self.save_history:
            return
            
        history_path = self._get_history_path()
        
        if history_path.exists():
            try:
                with open(history_path, 'r') as f:
                    self.messages = json.load(f)
                print(f"Loaded conversation history for session {self.session_id}")
            except Exception as e:
                print(f"Error loading conversation history: {str(e)}")
                self.messages = []
    
    def _save_history(self):
        """
        Save conversation history to disk.
        """
        if not self.save_history:
            return
        
        history_path = self._get_history_path()
        
        try:
            with open(history_path, 'w') as f:
                json.dump(self.messages, f, indent=2)
            # print(f"Saved conversation history for session {self.session_id}")
        except Exception as e:
            print(f"Error saving conversation history: {str(e)}")


def simulate_bot_response(user_input, conversation):
    """
    Simulate a bot response without making API calls.
    
    Args:
        user_input: The user's input text
        conversation: ConversationManager instance
        
    Returns:
        str: Simulated response
    """
    # Add user message to conversation
    conversation.add_message("user", user_input)
    
    # Generate a simple response based on the input
    if "hello" in user_input.lower() or "hi" in user_input.lower():
        response = "Hello! How can I help you with your insurance needs today?"
    elif "insurance" in user_input.lower():
        response = "We offer various insurance products including auto, home, life, and health insurance. Would you like more information about any specific type?"
    elif "claim" in user_input.lower():
        response = "To file a claim, you'll need your policy number, date of incident, and relevant documentation. Would you like me to guide you through the process?"
    elif "price" in user_input.lower() or "cost" in user_input.lower() or "quote" in user_input.lower():
        response = "Insurance prices vary based on many factors including coverage type, history, and location. I can help you get a personalized quote if you provide more details."
    elif "thank" in user_input.lower():
        response = "You're welcome! Is there anything else I can help you with?"
    elif "history" in user_input.lower():
        # Show conversation history
        messages = conversation.get_messages()
        response = f"Here's our conversation history ({len(messages)} messages):\n"
        for i, msg in enumerate(messages):
            if msg["role"] != "system":
                response += f"\n{i}. {msg['role'].upper()}: {msg['content'][:50]}{'...' if len(msg['content']) > 50 else ''}"
        return response
    else:
        response = "I understand you're asking about '" + user_input + "'. As this is an offline demo, I can only provide limited responses. In the full version, I would connect to OpenAI's GPT-4o for more helpful answers."
    
    # Add assistant response to conversation
    conversation.add_message("assistant", response)
    return response


def main():
    """
    Main function to test the conversation management features.
    """
    parser = argparse.ArgumentParser(description="Test conversation management offline")
    parser.add_argument("--session", help="Session ID for conversation history (default: random UUID)")
    parser.add_argument("--no-history", action="store_true", help="Disable conversation history saving")
    parser.add_argument("--max-history", type=int, default=10, help="Maximum conversation history length")
    args = parser.parse_args()
    
    # Generate or use provided session ID
    session_id = args.session if args.session else str(uuid.uuid4())
    
    print("\n===== Conversation Management Offline Test =====\n")
    print(f"Session ID: {session_id}")
    print("Type 'exit', 'quit', or Ctrl+C to end the conversation.")
    print("Type 'clear' to clear conversation history.")
    print("Type 'history' to view conversation history.")
    print("Type 'help' to see all available commands.\n")
    
    # Initialize conversation manager
    conversation = SimpleConversationManager(
        session_id=session_id,
        max_history=args.max_history,
        save_history=not args.no_history
    )
    
    # Add system message if not present
    messages = conversation.get_messages()
    if not messages or all(m["role"] != "system" for m in messages):
        system_prompt = "You are an insurance support assistant. You help users understand their insurance options, file claims, and answer questions about policies."
        conversation.add_message("system", system_prompt)
    
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
                conversation.clear_history()
                print("\nConversation history cleared.\n")
                continue
                
            elif user_input.lower() == "help":
                print("\nAvailable commands:")
                print("  exit, quit - End the conversation")
                print("  clear - Clear conversation history")
                print("  history - Show conversation history")
                print("  help - Show this help message\n")
                continue
            
            # Get simulated response
            response = simulate_bot_response(user_input, conversation)
            
            # Display response
            print(f"\nAssistant: {response}\n")
    
    except KeyboardInterrupt:
        print("\n\nExiting chat. Goodbye!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())