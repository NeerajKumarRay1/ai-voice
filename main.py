import os
import sys
import time
import tempfile

# Add the parent directory to the Python path to allow imports from stt, chat, and tts
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from stt import record_audio, transcribe_audio
from chat import get_bot_response
from tts import speak_text

def main():
    print("Starting the Voice AI loop. Press 'n' to exit after each round.")
    while True:
        try:
            print("\nRecording your voice for 5 seconds...")
            # Record audio to a temporary file
            temp_dir = tempfile.gettempdir()
            temp_filename = os.path.join(temp_dir, f"voice_recording_{os.getpid()}.wav")
            success = record_audio(temp_filename, duration=5, sample_rate=16000)
            if not success:
                print("No speech detected or failed to record audio. Please try again.")
                continue

            # Transcribe the recorded audio
            user_query = transcribe_audio(temp_filename)
            print(f"You said: {user_query}")

            # Clean up temporary file
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

            if not user_query:
                print("Could not transcribe audio. Please try again.")
                continue

            if user_query.lower() == 'exit':
                print("Exiting the Voice AI loop.")
                break

            print("Getting bot response...")
            bot_response = get_bot_response(user_query)
            if not bot_response:
                print("Bot failed to generate a response.")
                continue
            print(f"Bot says: {bot_response}")

            print("Speaking bot response...")
            speak_text(bot_response)

        except Exception as e:
            print(f"An error occurred: {e}")
            print("Please ensure your microphone is working and necessary models are loaded.")

        while True:
            choice = input("Do you want to continue? (y/n): ").lower()
            if choice == 'n':
                print("Exiting the Voice AI loop.")
                return
            elif choice == 'y':
                break
            else:
                print("Invalid input. Please type 'y' or 'n'.")

if __name__ == "__main__":
    main()