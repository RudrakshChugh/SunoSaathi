"""
Test script for TTS service
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.tts.app import TTSEngine

print("Testing TTS Service")
print("=" * 60)

tts = TTSEngine()

# Test English
print("\nGenerating English TTS...")
audio = tts.synthesize("Hello, this is a test of the text to speech system.", "en")
print(f"Generated audio: {len(audio)} bytes")

# Save to file for verification
output_file = "test_tts_output.wav"
with open(output_file, 'wb') as f:
    f.write(audio)
print(f"Saved to: {output_file}")

print("\n" + "=" * 60)
print("TTS service test complete!")
print("You can play the test_tts_output.wav file to verify audio quality.")
