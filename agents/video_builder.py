import sys
import json
import random
from pathlib import Path

# --- Compatibility Patch for MoviePy 1.0.3 and Pillow 10+ ---
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS
# -------------------------------------------------------------

# 1. Connect to config
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config

from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, TextClip, CompositeVideoClip, concatenate_videoclips
from moviepy.config import change_settings

# --- IMPORTANT: Point this to your actual ImageMagick installation path ---
change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"})

def assemble_final_video():
    print("Agent 3: Video Builder (Gameplay Slicer Edition) initializing...")

    # Load Script
    script_path = config.DATA_DIR / "current_script.json"
    if not script_path.exists():
        print("❌ Error: current_script.json not found.")
        return

    with open(script_path, "r") as file:
        script_data = json.load(file)
    conversation = script_data.get("conversation", [])

    # Load Master Gameplay Video
    master_bg_path = config.ASSETS_DIR / "gameplay_master.mp4"
    if not master_bg_path.exists():
        print(f"❌ Error: Master gameplay video not found at {master_bg_path}")
        return
    
    print("   -> Loading Master Gameplay Video...")
    master_bg = VideoFileClip(str(master_bg_path))
    
    # Calculate Total Audio Duration to ensure we have enough gameplay
    total_audio_duration = 0
    audio_clips = []
    
    for index in range(len(conversation)):
        audio_path = config.ASSETS_DIR / f"dialogue_{index}.wav"
        if audio_path.exists():
            clip = AudioFileClip(str(audio_path))
            audio_clips.append(clip)
            total_audio_duration += clip.duration
        else:
            print(f"❌ Error: Missing audio file {audio_path.name}")
            return

    # Pick a random starting point in the gameplay video
    # Ensures we don't pick a time too close to the end
    max_start_time = max(0, master_bg.duration - total_audio_duration - 5) 
    current_bg_time = random.uniform(0, max_start_time)
    print(f"   -> Random Gameplay Start Time Selected: {current_bg_time:.2f} seconds")

    scene_clips = []
    target_resolution = (1080, 1920)

    # Build the video scene by scene
    for index, segment in enumerate(conversation):
        speaker = segment.get("character_name", "Tech_Expert")
        text_content = segment.get("dialogue_text", "")
        print(f"\n🎬 Rendering Scene {index + 1} ({speaker})...")

        audio_clip = audio_clips[index]
        scene_duration = audio_clip.duration

        # --- STREAMING_CHUNK: Slicing and Cropping the Background ---
        # Slice a consecutive chunk from the master gameplay video
        bg_clip = master_bg.subclip(current_bg_time, current_bg_time + scene_duration)
        current_bg_time += scene_duration # Advance the playhead for the next scene

        # Smart Center-Crop to fit 9:16 vertical natively
        orig_w, orig_h = bg_clip.size
        scale_factor = max(target_resolution[0] / orig_w, target_resolution[1] / orig_h)
        new_w = int(orig_w * scale_factor)
        new_h = int(orig_h * scale_factor)
        
        bg_clip = bg_clip.resize(newsize=(new_w, new_h))
        bg_clip = bg_clip.crop(
            x_center=new_w / 2,
            y_center=new_h / 2,
            width=target_resolution[0],
            height=target_resolution[1]
        )

        layers = [bg_clip]

        # --- STREAMING_CHUNK: Adding the Character ---
        char_image_path = config.ASSETS_DIR / f"{speaker}.png"
        if char_image_path.exists():
            # Raise the character slightly so it doesn't get covered by YouTube's UI
            char_clip = ImageClip(str(char_image_path))
            char_clip = char_clip.set_duration(scene_duration)
            char_clip = char_clip.resize(height=750) 
            char_clip = char_clip.set_position(("center", target_resolution[1] - 850))
            layers.append(char_clip)
        else:
            print(f"      ⚠️ Warning: Could not find {char_image_path.name}")

        # --- STREAMING_CHUNK: Generating the Captions ---
        try:
            txt_clip = TextClip(
                txt=text_content,
                fontsize=75,
                font="Arial-Bold",
                color="white",
                stroke_color="black",
                stroke_width=4,
                method="caption",
                size=(950, None) # 950px wide text box so it wraps neatly
            )
            # Position the text above the character's head
            txt_clip = txt_clip.set_duration(scene_duration).set_position(("center", 350))
            layers.append(txt_clip)
        except Exception as e:
            print(f"      ⚠️ Warning: Could not generate captions. Is ImageMagick installed? Error: {e}")

        # --- STREAMING_CHUNK: Baking the Scene ---
        final_scene = CompositeVideoClip(layers, size=target_resolution)
        final_scene = final_scene.set_audio(audio_clip)
        scene_clips.append(final_scene)

    # Stitch it all together
    print("\n🧵 Stitching all scenes together into the final Short...")
    final_video = concatenate_videoclips(scene_clips, method="compose")
    
    output_file_path = config.OUTPUT_DIR / "final_short.mp4"
    final_video.write_videofile(
        str(output_file_path),
        fps=30, # Upped to 30fps for smoother gameplay playback
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast" # Renders faster during testing
    )
    
    print(f"\n✅ Agent 3 Complete! Your vertical gameplay Short is ready at: {output_file_path}")

if __name__ == "__main__":
    assemble_final_video()