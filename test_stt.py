#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test Script for Speech-to-Text Module

This script demonstrates how to use the speech-to-text functionality.
"""

import os
import argparse
from stt import record_audio, transcribe_audio, SpeechToText
from utils import get_config

def test_standalone_functions():
    """
    Test the standalone record_audio and transcribe_audio functions.
    """
    print("\n=== Testing Standalone Functions ===\n")
    
    # Create a temporary recording
    temp_file = "temp_recording.wav"
    print(f"Recording audio to {temp_file}...")
    print("Please speak for 5 seconds...")
    
    if record_audio(temp_file, duration=5):
        print("Recording successful!")
        
        # Transcribe the recording
        print("\nTranscribing audio...")
        transcription = transcribe_audio(temp_file)
        
        if transcription:
            print(f"Transcription: {transcription}")
        else:
            print("Transcription failed or returned empty result.")
    else:
        print("Recording failed or no speech detected.")
    
    # Clean up
    if os.path.exists(temp_file):
        os.remove(temp_file)
        print(f"Removed temporary file: {temp_file}")

def test_stt_class():
    """
    Test the SpeechToText class.
    """
    print("\n=== Testing SpeechToText Class ===\n")
    
    # Load configuration (or create default)
    config = get_config()
    
    # Initialize SpeechToText
    print("Initializing SpeechToText...")
    stt = SpeechToText(config)
    
    # Listen and transcribe
    print("\nListening for speech...")
    print("Please speak for 5 seconds...")
    
    transcription = stt.listen()
    
    if transcription:
        print(f"Transcription: {transcription}")
    else:
        print("Transcription failed or no speech detected.")
    
    # Clean up
    stt.cleanup()

def main():
    parser = argparse.ArgumentParser(description="Test the speech-to-text functionality")
    parser.add_argument("--mode", choices=["standalone", "class", "both"], default="both",
                        help="Test mode: standalone functions, SpeechToText class, or both")
    
    args = parser.parse_args()
    
    print("Speech-to-Text Test Script")
    print("==========================")
    
    if args.mode in ["standalone", "both"]:
        test_standalone_functions()
    
    if args.mode in ["class", "both"]:
        test_stt_class()
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()
