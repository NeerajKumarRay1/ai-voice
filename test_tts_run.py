#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple Test Script for Text-to-Speech Module

This script allows you to test the text-to-speech functionality by entering text to be spoken.
"""

import os
import logging
import pygame
from tts import speak_text, is_elevenlabs_available

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize pygame
pygame.init()

def main():
    print("\nText-to-Speech Test Script")
    print("===========================")
    
    # Check if ElevenLabs is available
    if is_elevenlabs_available():
        print("ElevenLabs API is available.")
    else:
        print("ElevenLabs API is not available. Will use pyttsx3 fallback.")
    
    while True:
        # Get text input from user
        text = input("\nEnter text to speak (or 'exit' to quit): ")
        
        if text.lower() in ['exit', 'quit', 'q']:
            break
        
        if not text.strip():
            print("Please enter some text to speak.")
            continue
        
        # Speak the text
        print(f"Speaking: '{text}'")
        speak_text(text)
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()