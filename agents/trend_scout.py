import sys
import json
from pathlib import Path
import feedparser

# 1. Link this sub-folder script back to the main config.py file
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config

def fetch_trending_topics():
    """Scrapes RSS feeds to find today's optimal video topic."""
    print("Agent 1: Trend Scout scanning the web for viral content...")
    
    discovered_topics = []

    # 2. Scrape the official Google Trends Daily RSS Feed
    try:
        google_trends_url = "https://trends.google.com/trending/rss?geo=US"
        feed = feedparser.parse(google_trends_url)
        # Capture the top 3 trending search terms
        for entry in feed.entries[:3]:  
            discovered_topics.append(entry.title)
    except Exception as e:
        print(f"[Error reading Google Trends]: {e}")

    # 3. Scrape a specific tech news RSS feed (NYT Tech) as a fallback
    try:
        tech_feed_url = "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"
        tech_feed = feedparser.parse(tech_feed_url)
        for entry in tech_feed.entries[:3]:
            discovered_topics.append(f"{entry.title} in the context of {config.TARGET_NICHE}")
    except Exception as e:
        print(f"[Error reading Tech Feed]: {e}")

    # Safety net: If offline or feeds fail, use a generic viral topic
    if not discovered_topics:
        discovered_topics.append(f"The Next Big Shift in {config.TARGET_NICHE}")

    # 4. Select the absolute top trend for today's video
    chosen_topic = discovered_topics[0]
    print(f"-> Selected Daily Topic: '{chosen_topic}'")

    # 5. Save the data to the structural data/ directory for Agent 2 to use
    handoff_data = {
        "trending_topic": chosen_topic,
        "all_scouted_trends": discovered_topics
    }
    
    output_path = config.DATA_DIR / "trending_topic.json"
    with open(output_path, "w") as file:
        json.dump(handoff_data, file, indent=4)
        
    print(f"Agent 1 Complete. Handoff saved securely to: {output_path}")
    return chosen_topic

if __name__ == "__main__":
    fetch_trending_topics()