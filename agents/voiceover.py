import sys
import json
from pathlib import Path

import soundfile as sf

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config

try:
    from kokoro import KPipeline
except ImportError:
    print("❌ Error: Kokoro is missing. Run: pip install kokoro soundfile")
    sys.exit(1)

def generate_audio():
    print("Agent 4: Multi-Voice Audio Engine initializing...")

    # Ensure this matches exactly what Agent 2 outputs
    script_path = config.DATA_DIR / "current_script.json"
    if not script_path.exists():
        print(f"❌ Error: Could not find {script_path}. Run script_writer.py first.")
        return
    
    # Using utf-8 here as well to safely read any special characters
    with open(script_path, "r", encoding="utf-8") as file:
        script_data = json.load(file)
    
    conversation = script_data.get("conversation", [])
    if not conversation:
        print("❌ Error: No conversation found in script.")
        return
    
    print("-> Loading Kokoro AI Voice Models (this may take a few seconds)...")
    pipeline = KPipeline(lang_code='a')

    # UPDATED: The new hybrid characters mapped to their voices
    voice_map = {
        'Dex': 'am_puck', # Deep, authoritative voice
        'Zack': 'am_adam'    # Higher, energetic voice
    }

    for index, segment in enumerate(conversation):
        speaker = segment.get("character_name", "Dex")
        text = segment.get("dialogue_text", "")

        # Fallback to Dex's voice if a name is misspelled
        chosen_voice = voice_map.get(speaker, 'am_puck')
        output_file = config.ASSETS_DIR / f"dialogue_{index}.wav"

        print(f"-> Synthesizing Line {index + 1} ({speaker}): '{text[:30]}...'")

        generator = pipeline(
            text,
            voice=chosen_voice,
            speed=1.0,
            split_pattern=r'\n+'
        )

        all_audio = []
        sample_rate = 24000

        for _, _, audio in generator:
            all_audio.extend(audio)
        
        if all_audio:
            sf.write(str(output_file), all_audio, sample_rate)
            print(f"   ✓ Saved to {output_file.name}")
        else:
            print(f"   ⚠️ Failed to generate audio for Line {index + 1}")

    print("\n✅ Agent 4 Complete! All voiceover files are ready for the Video Builder.")

if __name__ == "__main__":
    generate_audio()