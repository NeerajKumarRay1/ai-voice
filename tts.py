#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Text-to-Speech Module

This module handles the conversion of text to speech using ElevenLabs API
or pyttsx3 as a fallback option.
"""

import os
import logging
import tempfile
from pathlib import Path
import requests
import pyttsx3
import io
import pygame

def is_elevenlabs_available():
    """
    Check if ElevenLabs API is available by verifying if the API key is set.
    
    Returns:
        bool: True if ElevenLabs API key is available, False otherwise.
    """
    return bool(os.environ.get('ELEVENLABS_API_KEY'))


def speak_text(text: str):
    """
    Convert text to speech using ElevenLabs if available, otherwise fallback to pyttsx3.
    
    Args:
        text (str): The text to convert to speech.
    """
    if not text:
        return
        
    logger = logging.getLogger(__name__)
    logger.info(f"Converting to speech: {text[:50]}..." if len(text) > 50 else f"Converting to speech: {text}")
    
    # Check if ElevenLabs is available
    if is_elevenlabs_available():
        try:
            # Get API key from environment variable
            api_key = os.environ.get('ELEVENLABS_API_KEY')
            
            # ElevenLabs API endpoint
            url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"  # Default voice ID
            
            # Request headers
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": api_key
            }
            
            # Request body
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            # Make the API call
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                # Save the audio to a temporary file
                output_file = "output.mp3"
                with open(output_file, "wb") as f:
                    f.write(response.content)
                
                # Initialize pygame mixer if not already initialized
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                
                # Play the audio using pygame
                pygame.mixer.music.load(output_file)
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                
                logger.info("Speech played using ElevenLabs")
                return
            else:
                logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error using ElevenLabs: {str(e)}")
            logger.info("Falling back to pyttsx3")
    
    # Fallback to pyttsx3
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        # Set a female voice if available
        for voice in voices:
            if 'female' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        engine.setProperty('rate', 175)  # Speed of speech
        engine.say(text)
        engine.runAndWait()
        logger.info("Speech played using pyttsx3")
    except Exception as e:
        logger.error(f"Error using pyttsx3: {str(e)}")


class TextToSpeech:
    """
    A class to handle text-to-speech conversion using ElevenLabs or pyttsx3.
    """
    
    def __init__(self, config):
        """
        Initialize the TextToSpeech engine.
        
        Args:
            config (dict): Configuration parameters including API keys, voice settings, etc.
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Configuration parameters
        self.use_elevenlabs = config.get('use_elevenlabs', True)
        self.elevenlabs_api_key = config.get('elevenlabs_api_key', '')
        self.elevenlabs_voice_id = config.get('elevenlabs_voice_id', 'Rachel')
        self.cache_dir = config.get('tts_cache_dir', 'tts_cache')
        
        # Create cache directory if it doesn't exist
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
        
        if self.use_elevenlabs and self.elevenlabs_api_key:
            self.logger.info("Initializing ElevenLabs TTS")
            try:
                # set_api_key(self.elevenlabs_api_key)
                self.engine_type = 'elevenlabs'
                self.logger.info("ElevenLabs TTS initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize ElevenLabs: {str(e)}")
                self.logger.info("Falling back to pyttsx3")
                self._init_pyttsx3()
        else:
            self.logger.info("ElevenLabs not configured, using pyttsx3")
            self._init_pyttsx3()
    
    def _init_pyttsx3(self):
        """
        Initialize the pyttsx3 engine as a fallback.
        """
        try:
            # Test if pyttsx3 can be initialized
            engine = pyttsx3.init()
            engine.stop()
            
            self.engine_type = 'pyttsx3'
            self.logger.info("pyttsx3 TTS initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize pyttsx3: {str(e)}")
            self.engine_type = 'none'
    
    def speak(self, text):
        """
        Convert text to speech and play it.
        
        Args:
            text (str): The text to convert to speech.
        """
        if not text:
            return
        
        self.logger.info(f"Converting to speech: {text[:50]}..." if len(text) > 50 else f"Converting to speech: {text}")
        
        try:
            if self.engine_type == 'elevenlabs':
                # Use the environment variable if available, otherwise use the config
                api_key = os.environ.get('ELEVENLABS_API_KEY', self.elevenlabs_api_key)
                
                if api_key:
                    # ElevenLabs API endpoint
                    url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.elevenlabs_voice_id}"
                    
                    # Request headers
                    headers = {
                        "Accept": "audio/mpeg",
                        "Content-Type": "application/json",
                        "xi-api-key": api_key
                    }
                    
                    # Request body
                    data = {
                        "text": text,
                        "model_id": "eleven_monolingual_v1",
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.5
                        }
                    }
                    
                    # Make the API call
                    response = requests.post(url, json=data, headers=headers)
                    
                    if response.status_code == 200:
                        # Save the audio to a temporary file in the cache directory
                        output_file = os.path.join(self.cache_dir, "output.mp3")
                        with open(output_file, "wb") as f:
                            f.write(response.content)
                        
                        # Initialize pygame mixer if not already initialized
                        if not pygame.mixer.get_init():
                            pygame.mixer.init()
                        
                        # Play the audio using pygame
                        pygame.mixer.music.load(output_file)
                        pygame.mixer.music.play()
                        
                        # Wait for playback to finish
                        while pygame.mixer.music.get_busy():
                            pygame.time.Clock().tick(10)
                        
                        self.logger.info("Speech played using ElevenLabs")
                        return
                    else:
                        self.logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
                        raise Exception(f"ElevenLabs API error: {response.status_code}")
                else:
                    self.logger.error("ElevenLabs API key not found")
                    raise Exception("ElevenLabs API key not found")
            elif self.engine_type == 'pyttsx3':
                engine = pyttsx3.init()
                voices = engine.getProperty('voices')
                # Set a female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
                engine.setProperty('rate', 175)  # Speed of speech
                engine.say(text)
                engine.runAndWait()
                self.logger.info("Speech played using pyttsx3")
            else:
                self.logger.warning("No TTS engine available")
        except Exception as e:
            self.logger.error(f"Error in text-to-speech: {str(e)}")
            if self.engine_type == 'elevenlabs':
                self.logger.info("Falling back to pyttsx3 for this request")
                self._init_pyttsx3()
                self.speak(text)  # Try again with pyttsx3
    
    def cleanup(self):
        """
        Clean up resources used by the TTS engine.
        """
        self.logger.info("Cleaning up TTS resources")
        
        # Remove temporary audio files if they exist
        output_file = os.path.join(self.cache_dir, "output.mp3")
        if os.path.exists(output_file):
            try:
                os.remove(output_file)
                self.logger.info(f"Removed temporary audio file: {output_file}")
            except Exception as e:
                self.logger.error(f"Error removing temporary file: {str(e)}")
        
        # No need to clean up pyttsx3 as we create a new instance each time