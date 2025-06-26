#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enhanced Chat Engine Module

This module handles the interaction with OpenAI's GPT-4o model using direct API calls
with improved rate limiting, conversation history, and better error handling.
It also includes placeholders for retrieval-augmented generation (RAG).
"""

import os
import logging
import time
import json
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path

# Import OpenAI library
import openai

# Configure logging with more structured format
log_format = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
logger = logging.getLogger(__name__)

# Default paths
CONFIG_PATH = Path("config.json")
CONVERSATION_HISTORY_PATH = Path("conversation_history")

# Ensure conversation history directory exists
CONVERSATION_HISTORY_PATH.mkdir(exist_ok=True)

# Load configuration from file if available
def load_config() -> Dict[str, Any]:
    """
    Load configuration from config.json file.
    
    Returns:
        Dict[str, Any]: Configuration dictionary
    """
    try:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
                logger.info(f"Loaded configuration from {CONFIG_PATH}")
                return config
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
    
    # Default configuration
    return {
        "openai": {
            "model": "gpt-4o",
            "temperature": 0.7,
            "max_tokens": 500,
            "system_prompt": "You are an insurance support assistant. Your goal is to provide helpful, accurate, and clear information about insurance policies, claims, and procedures."
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

# Load configuration
CONFIG = load_config()

# Default system prompt
DEFAULT_SYSTEM_PROMPT = CONFIG.get("openai", {}).get("system_prompt", """
You are an insurance support assistant. Your goal is to provide helpful, accurate, and clear information about insurance policies, claims, and procedures.

Respond politely and informatively to user queries. If you don't know the answer, acknowledge this and suggest where the user might find the information.

Keep responses concise but complete.
""")

# Model configuration
DEFAULT_MODEL = CONFIG.get("openai", {}).get("model", "gpt-4o")
DEFAULT_TEMPERATURE = CONFIG.get("openai", {}).get("temperature", 0.7)
DEFAULT_MAX_TOKENS = CONFIG.get("openai", {}).get("max_tokens", 500)

# Rate limiting configuration
MAX_RETRIES = CONFIG.get("rate_limiting", {}).get("max_retries", 5)
INITIAL_BACKOFF = CONFIG.get("rate_limiting", {}).get("initial_backoff", 1)
BACKOFF_MULTIPLIER = CONFIG.get("rate_limiting", {}).get("backoff_multiplier", 2)
MAX_BACKOFF = CONFIG.get("rate_limiting", {}).get("max_backoff", 60)

# Conversation history configuration
MAX_HISTORY = CONFIG.get("conversation", {}).get("max_history", 10)
SAVE_HISTORY = CONFIG.get("conversation", {}).get("save_history", True)


def initialize_openai_client() -> Optional[openai.OpenAI]:
    """
    Initialize the OpenAI client with API key from environment variables.
    
    Returns:
        Optional[openai.OpenAI]: OpenAI client instance or None if API key is not available
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable not set")
        return None
    
    try:
        client = openai.OpenAI(api_key=api_key)
        return client
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {str(e)}")
        return None


def call_openai_with_retry(client: openai.OpenAI, messages: List[Dict[str, str]], 
                          model: str = DEFAULT_MODEL, 
                          temperature: float = DEFAULT_TEMPERATURE,
                          max_tokens: int = DEFAULT_MAX_TOKENS) -> Tuple[Optional[str], Optional[str]]:
    """
    Call OpenAI API with exponential backoff retry for rate limiting.
    
    Args:
        client: OpenAI client instance
        messages: List of message dictionaries
        model: Model name
        temperature: Temperature parameter
        max_tokens: Maximum tokens parameter
        
    Returns:
        Tuple[Optional[str], Optional[str]]: (response text, error message)
    """
    retries = 0
    backoff = INITIAL_BACKOFF
    
    while retries <= MAX_RETRIES:
        try:
            logger.info(f"Sending request to OpenAI API with {len(messages)} messages (attempt {retries + 1})")
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content, None
            else:
                logger.warning("Received empty response from OpenAI API")
                return None, "Empty response received"
                
        except openai.RateLimitError as e:
            retries += 1
            if retries > MAX_RETRIES:
                logger.error(f"Rate limit exceeded after {MAX_RETRIES} retries")
                return None, "Rate limit exceeded"
            
            logger.warning(f"Rate limit hit, retrying in {backoff} seconds (attempt {retries})")
            time.sleep(backoff)
            backoff = min(backoff * BACKOFF_MULTIPLIER, MAX_BACKOFF)
            
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return None, f"API error: {str(e)}"
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return None, f"Unexpected error: {str(e)}"
    
    return None, "Maximum retries exceeded"


class ConversationManager:
    """
    Manages conversation history for chat sessions.
    """
    
    def __init__(self, session_id: str = "default", max_history: int = MAX_HISTORY):
        """
        Initialize conversation manager.
        
        Args:
            session_id: Unique identifier for this conversation session
            max_history: Maximum number of messages to keep in history
        """
        self.session_id = session_id
        self.max_history = max_history
        self.history: List[Dict[str, str]] = []
        self.history_file = CONVERSATION_HISTORY_PATH / f"{session_id}.json"
        
        # Load existing history if available
        self._load_history()
    
    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            role: Message role ("system", "user", or "assistant")
            content: Message content
        """
        message = {"role": role, "content": content}
        self.history.append(message)
        
        # Trim history if it exceeds max_history
        if len(self.history) > self.max_history:
            # Always keep the first message (system prompt)
            system_message = None
            if self.history and self.history[0]["role"] == "system":
                system_message = self.history[0]
                self.history = self.history[1:]
            
            # Remove oldest messages (excluding system message)
            excess = len(self.history) - self.max_history + (1 if system_message else 0)
            if excess > 0:
                self.history = self.history[excess:]
            
            # Add system message back at the beginning
            if system_message:
                self.history.insert(0, system_message)
        
        # Save history
        if SAVE_HISTORY:
            self._save_history()
    
    def get_messages(self) -> List[Dict[str, str]]:
        """
        Get the current conversation history.
        
        Returns:
            List[Dict[str, str]]: List of message dictionaries
        """
        return self.history
    
    def clear_history(self, keep_system_prompt: bool = True) -> None:
        """
        Clear the conversation history.
        
        Args:
            keep_system_prompt: Whether to keep the system prompt
        """
        if keep_system_prompt and self.history and self.history[0]["role"] == "system":
            system_message = self.history[0]
            self.history = [system_message]
        else:
            self.history = []
        
        if SAVE_HISTORY:
            self._save_history()
    
    def _load_history(self) -> None:
        """
        Load conversation history from file.
        """
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
                logger.info(f"Loaded conversation history from {self.history_file}")
        except Exception as e:
            logger.error(f"Error loading conversation history: {str(e)}")
            self.history = []
    
    def _save_history(self) -> None:
        """
        Save conversation history to file.
        """
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
            logger.debug(f"Saved conversation history to {self.history_file}")
        except Exception as e:
            logger.error(f"Error saving conversation history: {str(e)}")


def get_bot_response(user_input: str, context: Optional[List[str]] = None, 
                    session_id: str = "default", conversation: Optional[ConversationManager] = None) -> str:
    """
    Get a response from the AI assistant based on user input and optional context.
    
    Args:
        user_input (str): The user's query or message
        context (Optional[List[str]]): Optional context from knowledge retrieval
        session_id (str): Session identifier for conversation history
        conversation (Optional[ConversationManager]): Existing conversation manager
        
    Returns:
        str: The assistant's response
    """
    if not user_input.strip():
        return "I didn't receive any input. How can I help you with your insurance needs?"
    
    # Initialize OpenAI client
    client = initialize_openai_client()
    if not client:
        return "I'm having trouble connecting to my knowledge base. Please try again later."
    
    # Initialize or use provided conversation manager
    conv = conversation if conversation else ConversationManager(session_id)
    
    # Check if we need to add a system message
    if not conv.history or conv.history[0]["role"] != "system":
        conv.add_message("system", DEFAULT_SYSTEM_PROMPT)
    
    # Add context from retrieval if available
    if context and len(context) > 0:
        context_text = "\n\n".join(context)
        context_message = f"""Additional context information:\n{context_text}\n\nPlease use this information to help answer the user's question if relevant."""
        conv.add_message("system", context_message)
    
    # Add user message to history
    conv.add_message("user", user_input)
    
    # Get messages for API call
    messages = conv.get_messages()
    
    # Call OpenAI API with retry
    response_text, error = call_openai_with_retry(client, messages)
    
    if response_text:
        # Add assistant response to history
        conv.add_message("assistant", response_text)
        return response_text
    else:
        # Handle error cases
        error_message = "I'm experiencing technical difficulties. Please try again later."
        
        if error == "Rate limit exceeded":
            error_message = "I'm currently handling too many requests. Please try again in a moment."
        elif error and "API error" in error:
            error_message = "I encountered an issue while processing your request. Please try again later."
        
        return error_message


# Placeholder for RAG integration
class KnowledgeRetriever:
    """
    A class to handle retrieval-augmented generation using FAISS.
    This is a placeholder for future implementation.
    """
    
    def __init__(self, knowledge_base_path: str = "knowledge"):
        """
        Initialize the knowledge retriever.
        
        Args:
            knowledge_base_path (str): Path to the knowledge base directory
        """
        self.knowledge_base_path = knowledge_base_path
        self.index = None
        logger.info(f"Knowledge retriever initialized with path: {knowledge_base_path}")
        # TODO: Initialize FAISS index here
    
    def query(self, user_input: str, top_k: int = 3) -> List[str]:
        """
        Query the knowledge base for relevant context.
        
        Args:
            user_input (str): The user's query
            top_k (int): Number of top results to return
            
        Returns:
            List[str]: List of relevant context passages
        """
        logger.info(f"Querying knowledge base for: {user_input[:50]}...")
        # TODO: Implement FAISS query logic
        return []  # Placeholder return


def get_bot_response_with_retrieval(user_input: str, session_id: str = "default",
                                   conversation: Optional[ConversationManager] = None) -> str:
    """
    Get a response from the AI assistant with retrieval-augmented generation.
    
    Args:
        user_input (str): The user's query or message
        session_id (str): Session identifier for conversation history
        conversation (Optional[ConversationManager]): Existing conversation manager
        
    Returns:
        str: The assistant's response
    """
    try:
        # Initialize retriever (placeholder for now)
        # retriever = KnowledgeRetriever()
        # context = retriever.query(user_input)
        
        # For now, just pass empty context
        context = []
        
        # Get response with context
        return get_bot_response(user_input, context, session_id, conversation)
    
    except Exception as e:
        logger.error(f"Error in retrieval-augmented response: {str(e)}")
        # Fall back to regular response without retrieval
        return get_bot_response(user_input, None, session_id, conversation)


class ChatEngine:
    """
    A class to handle interactions with the LLM using direct API calls.
    This maintains compatibility with the existing codebase while adding new functionality.
    """
    
    def __init__(self, config):
        """
        Initialize the ChatEngine.
        
        Args:
            config (dict): Configuration parameters including API keys, model settings, etc.
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Configuration parameters
        self.openai_api_key = config.get('openai_api_key', '')
        self.model_name = config.get('openai_model', DEFAULT_MODEL)
        self.temperature = config.get('temperature', DEFAULT_TEMPERATURE)
        self.max_tokens = config.get('max_tokens', DEFAULT_MAX_TOKENS)
        self.assistant_name = config.get('assistant_name', 'Insurance Assistant')
        self.use_retrieval = config.get('use_retrieval', False)
        self.session_id = config.get('session_id', 'default')
        
        # Set API key in environment if provided in config
        if self.openai_api_key and not os.environ.get("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = self.openai_api_key
        
        if not self.openai_api_key and not os.environ.get("OPENAI_API_KEY"):
            self.logger.warning("OpenAI API key not provided. Chat functionality will be limited.")
        
        # Initialize conversation manager
        self.conversation = ConversationManager(self.session_id)
        
        # Add system prompt to conversation
        system_prompt = config.get('system_prompt', DEFAULT_SYSTEM_PROMPT)
        if system_prompt:
            # Replace placeholder if present
            system_prompt = system_prompt.replace("{assistant_name}", self.assistant_name)
            self.conversation.add_message("system", system_prompt)
        
        self.logger.info(f"Initializing ChatEngine with model: {self.model_name}")
    
    def process(self, user_input):
        """
        Process user input and return the response.
        
        Args:
            user_input (str): The user's input text.
            
        Returns:
            str: The AI's response.
        """
        if not user_input.strip():
            return "I didn't catch that. Could you please repeat?"
        
        try:
            self.logger.info("Processing user input")
            
            # Use the appropriate response function
            if self.use_retrieval:
                return get_bot_response_with_retrieval(user_input, self.session_id, self.conversation)
            else:
                return get_bot_response(user_input, None, self.session_id, self.conversation)
                
        except Exception as e:
            self.logger.error(f"Error processing input: {str(e)}")
            return "I'm having trouble processing your request right now. Please try again later."
    
    def clear_conversation(self, keep_system_prompt: bool = True):
        """
        Clear the conversation history.
        
        Args:
            keep_system_prompt (bool): Whether to keep the system prompt
        """
        self.conversation.clear_history(keep_system_prompt)
        self.logger.info("Conversation history cleared")
    
    def cleanup(self):
        """
        Clean up resources used by the ChatEngine.
        """
        self.logger.info("Cleaning up ChatEngine resources")
        # Save conversation history one last time
        if hasattr(self, 'conversation') and self.conversation:
            try:
                self.conversation._save_history()
            except Exception as e:
                self.logger.error(f"Error saving conversation history during cleanup: {str(e)}")


# For direct script execution
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test the enhanced chat module")
    parser.add_argument("--api-key", help="OpenAI API key (if not set in environment)")
    parser.add_argument("--session", default="default", help="Session ID for conversation history")
    args = parser.parse_args()
    
    if args.api_key:
        os.environ["OPENAI_API_KEY"] = args.api_key
    
    print("\n===== Enhanced Chat Module Test =====\n")
    print("Type 'exit', 'quit', or Ctrl+C to end the conversation.")
    print("Type 'clear' to clear conversation history.\n")
    
    # Initialize conversation manager
    conversation = ConversationManager(args.session)
    
    try:
        while True:
            user_input = input("You: ")
            
            if user_input.lower() in ["exit", "quit"]:
                print("\nExiting chat. Goodbye!")
                break
            
            if user_input.lower() == "clear":
                conversation.clear_history()
                print("\nConversation history cleared.\n")
                continue
            
            response = get_bot_response(user_input, None, args.session, conversation)
            print(f"\nAssistant: {response}\n")
    
    except KeyboardInterrupt:
        print("\n\nExiting chat. Goodbye!")