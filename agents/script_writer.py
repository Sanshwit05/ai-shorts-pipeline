import sys
import json
import time
from pathlib import Path
from google import genai  # Updated to the clean import pattern for the new SDK
from pydantic import BaseModel, Field
import random
# Ensure we can import from the main project folder
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config

# Define the exact JSON structure we want Gemini to return
class DialogueSegment(BaseModel):
    character_name: str = Field(description="The name of the character speaking (must be exactly 'Dex' or 'Zack').")
    dialogue_text: str = Field(description="The spoken dialogue line.")
    visual_context: str = Field(description="Visual keywords describing the context.")

class VideoScript(BaseModel):
    title: str = Field(description="Catchy YouTube Shorts title.")
    description: str = Field(description="SEO-friendly YouTube description with hashtags.")
    conversation: list[DialogueSegment] = Field(description="The sequence of spoken lines.")

def generate_daily_script(mode, topic):
    print(f"Agent 2: Script Writer initializing...")
    print(f"   -> Drafting a conversational skit for mode: '{mode}', topic: '{topic}'")
    
    # 1. Initialize the NEW GenAI Client
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    
    # 2. Dynamically build the prompt based on the Mode
    # 2. Dynamically build the prompt based on the Mode
    # 2. Dynamically build the prompt based on the Mode
    if mode == "fact":
        if topic == "RANDOM_NOVEL_FACT":
            # 1. INJECT REAL PYTHON RANDOMNESS
            tech_niches = [
                "Hidden Windows OS performance tweaks (e.g., registry, services)",
                "Advanced AI prompting secrets (e.g., system prompts, token optimization)",
                "Hardware secrets (e.g., thermal dynamics, RAM cache, GPU scheduling)",
                "Everyday cybersecurity loopholes hackers exploit",
                "Hidden browser developer tools or network tab secrets",
                "Command Prompt/Terminal tricks that save hours of time"
            ]
            selected_niche = random.choice(tech_niches)
            random_seed = random.randint(10000, 99999) # Forces a unique token generation path
            
            topic_instruction = f"""Focus exclusively on this highly specific category: {selected_niche}.
(System Randomization Seed: {random_seed} - Ensure this output is entirely unique from previous generations.)

CRITICAL: Pick a highly obscure, actionable fact within this category. Do NOT pick basic tips like 'clear your cache', 'use a strong password', or 'ask the AI to act as an expert'. Go deep into technical secrets that 99% of people do not know."""

        else:
            topic_instruction = f"Explain this specific actionable tech/PC hack or AI secret: {topic}"
            
        # 2. THE ENGINEERED SYSTEM PROMPT
        system_prompt = f"""You are an elite YouTube Shorts scriptwriter specializing in viral, high-retention technical education.
Write a fast-paced, highly engaging 45-second conversational script between two characters:
1. 'Zack': A frustrated, everyday user struggling with a slow PC or generic tech issues.
2. 'Dex': A master tech engineer who reveals a mind-blowing, hidden solution.

Task: {topic_instruction}

STRICT SCRIPT STRUCTURE:
- THE PAIN (0-5s): Zack aggressively complains about a relatable tech problem.
- THE PATTERN INTERRUPT (5-10s): Dex cuts him off with a bold, controversial statement or secret fix. 
- THE SECRET MECHANISM (10-25s): Dex explains *why* the secret works using a simple real-world analogy.
- THE ACTION PROTOCOL (25-40s): Dex gives exact, step-by-step instructions on what to click, type, or toggle.
- THE LOOP (40-45s): Zack makes a final realization that perfectly wraps up the video.

RULES:
- ZERO JARGON without immediate explanation.
- No emojis in the dialogue text.
- Character names must be exactly 'Zack' or 'Dex'.
- The total combined word count of all dialogue_text MUST be strictly between 100 and 115 words.
"""
    
    # Exponential Backoff Retry Logic
    max_attempts = 5
    base_delay = 15

    for attempt in range(max_attempts):
        try:
            print(f"   -> Contacting Gemini to generate structured script... (Attempt {attempt + 1}/{max_attempts})")
            
            # 3. Call the new client.models.generate_content API pattern
            response = client.models.generate_content(
                model='gemini-3.5-flash-lite',
                contents=system_prompt,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': VideoScript,
                    'temperature': 0.7  # Slight creativity boost
                }
            )
            # If successful, break out of the retry loop
            break
            
        except Exception as e:
            if attempt < max_attempts - 1:
                # Calculate exponential backoff delay: 15, 30, 60, 120...
                delay = base_delay * (2 ** attempt)
                print(f"⚠️ Gemini API busy or error encountered: {e}")
                print(f"⏳ Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("❌ Max retries reached. Script generation failed.")
                raise e
    
    # Parse the returned JSON back into our Python model
    script_data = VideoScript.model_validate_json(response.text)
    print(f"   -> Success! Script generated with {len(script_data.conversation)} dialogue segments.")
    
    # Step 5: Save the script to your data folder (using utf-8 to prevent emoji crashes)
    script_path = config.DATA_DIR / "current_script.json"
    with open(script_path, "w", encoding="utf-8") as file:
        file.write(script_data.model_dump_json(indent=4))
        
    print(f"✅ Agent 2 Complete! Script saved to {script_path}")


if __name__ == "__main__":
    # Default fallback values
    mode = "news"
    # Concrete fallback topic so the LLM always has specific facts to write about
    daily_topic = "Figure 02 humanoid AI robot features, capabilities, and factory deployment testing"
    
    # Check if the Orchestrator sent arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
    if len(sys.argv) > 2:
        daily_topic = sys.argv[2]
    elif mode == "news":
        # If news mode and no custom topic, read the output from Agent 1 (Trend Scout)
        trend_file = config.DATA_DIR / "trending_topic.json"
        if trend_file.exists():
            with open(trend_file, "r", encoding="utf-8") as file:
                trends = json.load(file)
                # Grab the hottest topic, or use the specific robot topic if empty
                daily_topic = trends[0].get("topic", "Figure 02 humanoid AI robot features and capabilities")
                print(f"   -> Read auto-scouted topic: {daily_topic}")
        else:
            print("⚠️ Warning: No trending_topic.json found. Using fallback topic.")
            
    generate_daily_script(mode, daily_topic)