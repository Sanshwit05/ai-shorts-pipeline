import subprocess
import sys
import time
from pathlib import Path
def run_agent(script_path, agent_name, *args):
    """Runs a Python script and stops everything if it fails."""
    print(f"\n{'='*50}")
    print(f"🚀 STARTING: {agent_name}")
    print(f"{'='*50}\n")
    
    # We use subprocess.run to execute the command exactly as you would in the terminal
    try:
        # Build the command list, including any extra arguments (like the topic)
        command = [sys.executable, script_path] + list(args)
        result = subprocess.run(command, check=True)
    except subprocess.CalledProcessError:
        print(f"\n❌ CRITICAL ERROR: {agent_name} failed to execute.")
        print("Stopping the automation pipeline to prevent corrupted files.")
        sys.exit(1)
        
    print(f"\n✅ SUCCESS: {agent_name} completed.")
    time.sleep(1) # Tiny pause so the terminal output is readable

def main():
    print("""
    ================================================
         🤖 YOUTUBE SHORTS AUTOMATION FACTORY 🤖
    ================================================
    """)
    
    # Define the absolute paths to your agents
    base_dir = Path(__file__).resolve().parent
    trend_scout = base_dir / "agents" / "trend_scout.py"
    script_writer = base_dir / "agents" / "script_writer.py"
    voiceover_engine = base_dir / "agents" / "voiceover.py"
    video_builder = base_dir / "agents" / "video_builder.py"
    youtube_uploader = base_dir / "agents" / "uploader.py"
    # The New Hybrid Menu
    print("\n🎬 What type of video are we making today?")
    print("  1: Tech Fact / Hacker Secret (Evergreen)")
    print("  2: Trending Tech News (Pros & Cons)")
    mode_choice = input("👉 Enter 1 or 2: ").strip()

    if mode_choice == "1":
        video_mode = "fact"
        print("\n🧠 Tech Fact Mode Selected!")
        daily_topic = input("👉 Enter a specific fact/hack, OR press ENTER to let AI invent a brand new obscure one: ").strip()
        if not daily_topic:
            daily_topic = "RANDOM_NOVEL_FACT"
            print("   -> AI will generate a totally unique, mind-blowing tech secret.")
        
        # Run Script Writer directly (skip trend scout)
        run_agent(str(script_writer), "Agent 2 (Script Writer)", video_mode, daily_topic)

    else:
        video_mode = "news"
        print("\n📰 Trending News Mode Selected!")
        daily_topic = input("👉 Press ENTER to Auto-Scout Trends, OR type a custom news topic: ").strip()
        
        if not daily_topic:
            print("\n🔍 Auto-Scout Mode Activated!")
            run_agent(str(trend_scout), "Agent 1 (Trend Scout)")
            run_agent(str(script_writer), "Agent 2 (Script Writer)", video_mode)
        else:
            print(f"\n🎯 Custom News Topic: {daily_topic}")
            run_agent(str(script_writer), "Agent 2 (Script Writer)", video_mode, daily_topic)
    
    # Step 3: Generate the audio (Agent 4)
    run_agent(str(voiceover_engine), "Agent 4 (Voiceover Engine)")
    
    # Step 3: Render the video (Agent 3)
    run_agent(str(video_builder), "Agent 3 (Video Builder)")
    
    # Step 4: The Human-in-the-Loop Safety Pause
    print("\n" + "*"*50)
    print("🎬 PIPELINE COMPLETE! YOUR VIDEO IS READY.")
    print("*"*50)
    print(f"File saved at: {base_dir / 'output' / 'final_short.mp4'}")
    
    while True:
        choice = input("\n👉 Please review the video file. Ready to upload to YouTube? (Y/N): ").strip().upper()
        
        if choice == 'Y':
            print("\n⏳ Initializing Agent 5 (YouTube Uploader)...")
            run_agent(str(youtube_uploader), "Agent 5 (YouTube Uploader)", "--privacy", "public")
            print("\n🎉 FACTORY CYCLE COMPLETE! Your Short has been processed.")
            break
        elif choice == 'N':
            print("\n🛑 Upload cancelled. You can edit the files and run the uploader manually later.")
            break
        else:
            print("⚠️ Invalid input. Please type 'Y' for Yes or 'N' for No.")

if __name__ == "__main__":
    main()