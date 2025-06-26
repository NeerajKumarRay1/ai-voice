#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Speech-to-Text Module

This module handles the conversion of speech to text using OpenAI's Whisper model.
It provides functionality to capture audio from the microphone and transcribe it to text.
"""

import os
import tempfile
import logging
import numpy as np
import whisper
import sounddevice as sd
from scipy.io.wavfile import write as write_wav

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global model instance for performance (load once)
_whisper_model = None

def get_whisper_model(model_name='base'):
    """
    Get or initialize the Whisper model (singleton pattern).
    
    Args:
        model_name (str): Name of the Whisper model to use ('tiny', 'base', 'small', 'medium', 'large')
        
    Returns:
        whisper.Model: Loaded Whisper model
    """
    global _whisper_model
    
    if _whisper_model is None:
        try:
            logger.info(f"Loading Whisper model: {model_name}")
            _whisper_model = whisper.load_model(model_name)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading Whisper model: {str(e)}")
            raise
    
    return _whisper_model

def record_audio(filename, duration=5, sample_rate=16000):
    """
    Record audio from the microphone and save to a file.
    
    Args:
        filename (str): Path to save the recorded audio file
        duration (int): Duration of recording in seconds
        sample_rate (int): Sample rate for recording
        
    Returns:
        bool: True if recording was successful, False otherwise
    """
    try:
        logger.info(f"Recording audio for {duration} seconds...")
        
        # Record audio from microphone
        audio_data = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='float32'
        )
        sd.wait()  # Wait until recording is finished
        
        # Check if audio contains speech (simple energy threshold)
        energy = np.mean(np.abs(audio_data))
        logger.info(f"Audio energy level: {energy}")
        if energy < 0.001:  # Lower threshold to be more sensitive
            logger.info("No speech detected")
            return False
        
        # Save audio to file
        logger.info(f"Saving audio to {filename}")
        write_wav(filename, sample_rate, audio_data)
        return True
        
    except Exception as e:
        logger.error(f"Error recording audio: {str(e)}")
        return False

def transcribe_audio(file_path):
    """
    Transcribe audio file to text using Whisper.
    
    Args:
        file_path (str): Path to the audio file (WAV or MP3)
        
    Returns:
        str: Transcribed text, or empty string if transcription failed
    """
    if not os.path.exists(file_path):
        logger.error(f"Audio file not found: {file_path}")
        return ""
    
    try:
        # Get or initialize the model
        model = get_whisper_model()
        
        # Transcribe audio
        logger.info(f"Transcribing audio file: {file_path}")
        # Verify file exists and print absolute path for debugging
        abs_path = os.path.abspath(file_path)
        logger.info(f"Absolute path: {abs_path}, File exists: {os.path.exists(abs_path)}")
        
        # Load audio directly using scipy instead of whisper.load_audio
        import scipy.io.wavfile as wav
        sample_rate, audio_data = wav.read(abs_path)
        # Convert to float32 and normalize if needed
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32) / (2**15 if audio_data.dtype == np.int16 else 1)
        
        # Transcribe the loaded audio data
        result = model.transcribe(
            audio_data,
            fp16=False  # Use fp16=True if you have GPU support
        )
        
        transcription = result["text"].strip()
        logger.info(f"Transcription complete: {transcription[:50]}..." if len(transcription) > 50 else f"Transcription complete: {transcription}")
        
        return transcription
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        return ""

class SpeechToText:
    """
    A class to handle speech-to-text conversion using OpenAI's Whisper.
    """
    
    def __init__(self, config):
        """
        Initialize the SpeechToText engine.
        
        Args:
            config (dict): Configuration parameters including model size, language, etc.
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Configuration parameters
        self.model_name = config.get('whisper_model', 'base')
        self.language = config.get('language', 'en')
        self.sample_rate = config.get('sample_rate', 16000)
        self.record_duration = config.get('record_duration', 5)  # seconds
        
        self.logger.info(f"Initializing Whisper with model: {self.model_name}")
        self.model = get_whisper_model(self.model_name)
        self.logger.info("Whisper model loaded successfully")
    
    def listen(self):
        """
        Listen to the microphone and convert speech to text.
        
        Returns:
            str: Transcribed text from speech, or empty string if no speech detected.
        """
        self.logger.info(f"Recording audio for {self.record_duration} seconds...")
        
        try:
            # Create a temporary file for the recording
            temp_dir = tempfile.gettempdir()
            temp_filename = os.path.join(temp_dir, f"whisper_recording_{os.getpid()}.wav")
            self.logger.info(f"Using temporary file: {temp_filename}")
            
            # Record audio to the temporary file
            if record_audio(temp_filename, self.record_duration, self.sample_rate):
                # Verify file exists before transcription
                if os.path.exists(temp_filename):
                    self.logger.info(f"Temporary file exists, size: {os.path.getsize(temp_filename)} bytes")
                    # Transcribe the recorded audio
                    transcription = transcribe_audio(temp_filename)
                else:
                    self.logger.error(f"Temporary file not found: {temp_filename}")
                    transcription = ""
            else:
                transcription = ""
            
            # Clean up temporary file
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
                self.logger.info(f"Removed temporary file: {temp_filename}")
            
            return transcription
            
        except Exception as e:
            self.logger.error(f"Error in speech recognition: {str(e)}")
            return ""
    
    def cleanup(self):
        """
        Clean up resources used by the STT engine.
        """
        self.logger.info("Cleaning up STT resources")
        # Any cleanup code would go here