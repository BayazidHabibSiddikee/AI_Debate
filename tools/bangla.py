#!/usr/bin/env python3
# tools/bangla.py — Bangla Voice Translator, runs as its own process
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.tts import speak_female

from datetime import datetime

class BanglaVoiceTranslator:
    def speak(self, text: str):
        speak_female(text)

    def listen(self) -> str | None:
        try:
            text = input("Bangla input: ").strip()
            if text:
                print(f"[Bangla] {text}")
                return text
        except EOFError:
            pass
        return None

    def translate(self, bangla_text: str) -> str | None:
        try:
            from deep_translator import GoogleTranslator
            result = GoogleTranslator(source='bn', target='en').translate(bangla_text)
            return result
        except Exception as e:
            print(f"[Bangla Translation Error] {e}")
            return None

# CLI for translation from English to target language (with shortcuts)
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Bangla Voice Translator - CLI for translation')
    parser.add_argument('-b', '--bangla', action='store_true', help='Translate from English to Bangla')
    parser.add_argument('-c', '--chinese', action='store_true', help='Translate from English to Chinese')
    parser.add_argument('-en', '--english', action='store_true', help='Translate from English to English (identity)')
    parser.add_argument('text', nargs='?', help='The text to translate (if not provided, reads from stdin)')
    
    args = parser.parse_args()
    
    # Determine target language
    target_lang = None
    if args.bangla:
        target_lang = 'bn'
    elif args.chinese:
        target_lang = 'zh-CN'
    elif args.english:
        target_lang = 'en'
    
    if target_lang is None:
        parser.error("Please specify one of -b/--bangla, -c/--chinese, -en/--english")
    
    # Get text: either from command line argument or stdin
    if args.text is not None:
        text = args.text
    else:
        # Read from stdin
        text = sys.stdin.read().strip()
    
    if not text:
        print("Error: No text provided", file=sys.stderr)
        sys.exit(1)
    
    # Translate from English to target_lang
    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source='en', target=target_lang)
        result = translator.translate(text)
        if result is None:
            print("Translation failed", file=sys.stderr)
            sys.exit(1)
        else:
            print(result)
    except Exception as e:
        print(f"Translation error: {e}", file=sys.stderr)
        sys.exit(1)