from stt import record_audio, transcribe_audio

if __name__ == "__main__":
    print("Recording... Speak into the mic.")
    record_audio("test_audio.wav", duration=5)  # You can adjust duration
    
    print("Transcribing...")
    result = transcribe_audio("test_audio.wav")
    
    print("Transcription:")
    print(result)
