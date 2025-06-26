#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test Script for Text-to-Speech Module

This script demonstrates how to use the text-to-speech functionality.
"""

import os
import argparse
import logging
import pygame
from tts import speak_text, is_elevenlabs_available, TextToSpeech

# Initialize pygame
pygame.init()

# Try to import utils, but don't fail if it doesn't exist
try:
    from utils import get_config
except ImportError:
    # Define a simple get_config function if utils is not available
    def get_config():
        return {
            'use_elevenlabs': True,
            'elevenlabs_api_key': os.environ.get('ELEVENLABS_API_KEY', ''),
            'elevenlabs_voice_id': '21m00Tcm4TlvDq8ikWAM',  # Default voice ID
            'tts_cache_dir': 'tts_cache'
        }

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_standalone_functions():
    """
    Test the standalone speak_text function.
    """
    print("\n=== Testing Standalone Functions ===\n")
    
    # Check if ElevenLabs is available
    if is_elevenlabs_available():
        print("ElevenLabs API is available.")
    else:
        print("ElevenLabs API is not available. Will use pyttsx3 fallback.")
    
    # Test speak_text function
    text = "This is a test of the text to speech functionality."
    print(f"Speaking: '{text}'")
    speak_text(text)

def test_tts_class():
    """
    Test the TextToSpeech class.
    """
    print("\n=== Testing TextToSpeech Class ===\n")
    
    # Load configuration (or create default)
    try:
        config = get_config()
    except:
        # If get_config is not available, use a default config
        config = {
            'use_elevenlabs': True,
            'elevenlabs_api_key': os.environ.get('ELEVENLABS_API_KEY', ''),
            'elevenlabs_voice_id': '21m00Tcm4TlvDq8ikWAM',  # Default voice ID
            'tts_cache_dir': 'tts_cache'
        }
    
    # Initialize TextToSpeech
    print("Initializing TextToSpeech...")
    tts = TextToSpeech(config)
    
    # Test speaking
    text = "This is a test of the TextToSpeech class."
    print(f"Speaking: '{text}'")
    tts.speak(text)
    
    # Clean up
    tts.cleanup()

def main():
    parser = argparse.ArgumentParser(description="Test the text-to-speech functionality")
    parser.add_argument("--mode", choices=["standalone", "class", "both"], default="both",
                        help="Test mode: standalone functions, TextToSpeech class, or both")
    parser.add_argument("--set-api-key", type=str, help="Set ElevenLabs API key for testing")
    
    args = parser.parse_args()
    
    # Set API key if provided
    if args.set_api_key:
        os.environ['ELEVENLABS_API_KEY'] = args.set_api_key
        print(f"Set ELEVENLABS_API_KEY environment variable for this session")
    
    print("Text-to-Speech Test Script")
    print("===========================")
    
    if args.mode in ["standalone", "both"]:
        test_standalone_functions()
    
    if args.mode in ["class", "both"]:
        test_tts_class()
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()