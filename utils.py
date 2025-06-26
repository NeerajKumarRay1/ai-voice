#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utility Functions Module

This module provides helper functions for the voice assistant application,
including logging setup, configuration management, and other utilities.
"""

import os
import json
import logging
from pathlib import Path
import sys
from datetime import datetime

def setup_logging(log_level=logging.INFO, log_file=None):
    """
    Set up logging configuration for the application.
    
    Args:
        log_level: The logging level (default: INFO)
        log_file: Path to log file (default: None, logs to console only)
        
    Returns:
        logger: Configured logger instance
    """
    # Create logs directory if logging to file
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configure handlers
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    # Apply configuration
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers
    )
    
    logger = logging.getLogger('voice_assistant')
    logger.info("Logging initialized")
    
    return logger

def get_config(config_path='config.json'):
    """
    Load configuration from a JSON file, or create default if not exists.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        dict: Configuration parameters
    """
    # Default configuration
    default_config = {
        # General settings
        'assistant_name': 'Voice Assistant',
        'language': 'en',
        'log_level': 'INFO',
        'log_file': 'logs/assistant.log',
        
        # API keys (to be filled by user)
        'openai_api_key': '',
        'elevenlabs_api_key': '',
        
        # STT settings
        'whisper_model': 'base',  # tiny, base, small, medium, large
        'sample_rate': 16000,
        'record_duration': 5,  # seconds
        
        # TTS settings
        'use_elevenlabs': True,
        'elevenlabs_voice_id': 'Rachel',  # Default voice
        'tts_cache_dir': 'tts_cache',
        
        # LLM settings
        'openai_model': 'gpt-4o',
        'temperature': 0.7,
        'max_tokens': 150,
        
        # Knowledge base settings
        'knowledge_dir': 'knowledge',
        'index_path': 'faiss_index',
        'chunk_size': 1000,
        'chunk_overlap': 200,
        
        # UI settings
        'ui_type': 'gradio',  # 'flask' or 'gradio'
        'port': 7860,
        'host': '127.0.0.1',
        'debug': False
    }
    
    # Create config file with defaults if it doesn't exist
    if not os.path.exists(config_path):
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=4)
        logging.info(f"Created default configuration at {config_path}")
        return default_config
    
    # Load existing configuration
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        logging.info(f"Loaded configuration from {config_path}")
        
        # Update with any missing default values
        for key, value in default_config.items():
            if key not in config:
                config[key] = value
        
        return config
    except Exception as e:
        logging.error(f"Error loading configuration: {str(e)}")
        logging.info("Using default configuration")
        return default_config

def create_directories(config):
    """
    Create necessary directories for the application.
    
    Args:
        config: Application configuration
    """
    directories = [
        'logs',
        config.get('knowledge_dir', 'knowledge'),
        config.get('tts_cache_dir', 'tts_cache'),
        os.path.dirname(config.get('log_file', 'logs/assistant.log'))
    ]
    
    for directory in directories:
        if directory:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logging.info(f"Created directory: {directory}")

def format_time(seconds):
    """
    Format seconds into a human-readable time string.
    
    Args:
        seconds: Number of seconds
        
    Returns:
        str: Formatted time string (e.g., "2m 30s")
    """
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def sanitize_filename(text):
    """
    Convert text to a safe filename.
    
    Args:
        text: Input text
        
    Returns:
        str: Safe filename
    """
    # Replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        text = text.replace(char, '_')
    
    # Limit length
    max_length = 100
    if len(text) > max_length:
        text = text[:max_length]
    
    # Add timestamp for uniqueness
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{text}_{timestamp}"