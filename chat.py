#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Local LLM Chat Module

Uses Hugging Face transformers with local models instead of OpenAI API.
"""

import os
import requests
import json
from typing import Optional

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
SYSTEM_PROMPT = "You are a helpful insurance support agent."

def get_bot_response(user_input: str) -> Optional[str]:
    """
    Generate a response from the Gemini 1.5 Flash model.
    
    Args:
        user_input: The user's message.
        
    Returns:
        str: The generated response, or None if an error occurred.
    """
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY environment variable not set.")
        return None

    headers = {
        "Content-Type": "application/json"
    }
    params = {
        "key": GEMINI_API_KEY
    }
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": SYSTEM_PROMPT},
                    {"text": user_input}
                ]
            }
        ]
    }

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        
        response_data = response.json()
        
        if "candidates" in response_data and response_data["candidates"]:
            first_candidate = response_data["candidates"][0]
            if "content" in first_candidate and "parts" in first_candidate["content"]:
                for part in first_candidate["content"]["parts"]:
                    if "text" in part:
                        return part["text"]
        print("Error: No text found in Gemini API response.")
        return None

    except requests.exceptions.RequestException as e:
        print(f"Error making request to Gemini API: {e}")
        return None
    except json.JSONDecodeError:
        print("Error: Could not decode JSON response from Gemini API.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

if __name__ == "__main__":
    print("Testing Gemini 1.5 Flash integration...")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit"]:
            break
        
        bot_response = get_bot_response(user_input)
        if bot_response:
            print(f"Bot: {bot_response}")
        else:
            print("Failed to get a response from the bot.")