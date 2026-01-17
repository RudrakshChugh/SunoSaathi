"""
Test script for translation service
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Test the translator directly
from services.translation.app import GoogleTranslator

print("Testing Translation Service")
print("=" * 60)

translator = GoogleTranslator()

# Test cases
test_cases = [
    ("hello", "en", "hi"),
    ("thank you", "en", "ta"),
    ("good morning", "en", "bn"),
    ("How are you doing today?", "en", "hi"),
    ("I need help", "en", "te"),
]

for text, src, tgt in test_cases:
    result = translator.translate(text, src, tgt)
    print(f"\n{src} -> {tgt}")
    print(f"  Input:  {text}")
    print(f"  Output: {result}")

print("\n" + "=" * 60)
print("Translation service test complete!")
