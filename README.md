# 🤖 Multi-Agent YouTube Shorts Factory

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Gemini API](https://img.shields.io/badge/Google_GenAI-Gemini_3.5_Flash-orange.svg)
![Kokoro AI](https://img.shields.io/badge/Voice_Synthesis-Kokoro_82M-green.svg)
![MoviePy](https://img.shields.io/badge/Video_Processing-MoviePy-red.svg)

A fully autonomous, multi-agent AI pipeline that automatically scouts trends, writes highly engaging educational scripts, synthesizes multi-character voiceovers, edits B-roll footage, and uploads the final video to YouTube Shorts. 

This project demonstrates applied Artificial Intelligence by combining Large Language Models (LLMs) with strict structured data generation, local voice synthesis, and headless API integrations.

---

## 🏗️ The 5-Agent Architecture

This system is built on a modular "Agent" framework, where each agent handles a highly specific task in the production pipeline and securely hands off structured JSON data to the next.

* **🔍 Agent 1: Trend Scout** 
  Scrapes the web for viral tech topics, AI model releases, or cybersecurity facts, ensuring the content is always relevant.
* **✍️ Agent 2: Script Writer (Google Gemini 3.5 Flash / Lite)** 
  Generates conversational, 45-second scripts between two characters ("Zack" and "Dex"). Uses Python-injected random seeds to prevent LLM hallucination and repetition, enforcing strict Pydantic JSON schemas for outputs.
* **🎙️ Agent 3: Voiceover Engine** 
  Utilizes the `Kokoro-82M` local model to generate distinct voice profiles for each character.
* **🎬 Agent 4: Video Builder (Gameplay Slicer)** 
  Powered by `MoviePy`. Slices master B-roll/gameplay footage at random timestamps, dynamically overlays the generated audio segments, and renders the final `.mp4`.
* **🚀 Agent 5: YouTube Uploader** 
  Handles OAuth 2.0 authentication and interacts with the YouTube Data API v3 to upload the final Short with auto-generated SEO descriptions and tags.

---

## 🚀 Technical Highlights & Challenges Solved

* **Strict LLM Output Parsing:** Utilized `google-genai` SDK and Pydantic models to force the LLM to return strictly formatted JSON with specific word-count limitations (100-115 words) for timing constraints.
* **Prompt Entropy Injection:** Solved the "Illusion of LLM Randomness" by injecting Python-generated seeds and randomized sub-niches into the system prompt, ensuring 100% unique script generation on every run.
* **API Rate Limit Handling:** Engineered a custom exponential backoff retry loop with randomized jitter to handle `503 UNAVAILABLE` and `429 RESOURCE_EXHAUSTED` errors gracefully without crashing the factory.
* **Chunked Video Uploads:** Configured the YouTube API integration to process video uploads in 1MB chunks, bypassing standard connection timeout limitations for media rendering.

---

## 🛠️ Tech Stack

* **Language:** Python
* **AI / LLMs:** Google GenAI SDK (Gemini-3.5-Flash, Gemini-3.5-Flash-Lite)
* **Data Structuring:** Pydantic
* **Audio Synthesis:** Kokoro-82M (Hugging Face)
* **Video Editing:** MoviePy
* **Integrations:** YouTube Data API v3, Google OAuth 2.0

---

## ⚙️ Installation & Setup

**1. Clone the repository:**
```bash
git clone [https://github.com/YOUR_USERNAME/multi-agent-youtube-factory.git](https://github.com/YOUR_USERNAME/multi-agent-youtube-factory.git)
cd multi-agent-youtube-factory