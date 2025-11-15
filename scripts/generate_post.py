from openai import OpenAI
import json
import os
import time
from datetime import datetime, timedelta

# Initialize OpenAI client
client = OpenAI()

# Folder to store posts
POSTS_DIR = "posts"
os.makedirs(POSTS_DIR, exist_ok=True)

# File to keep track of posts
POSTS_JSON = "posts.json"
STATE_FILE = "bot_state.json"   # <-- Nuevo archivo para almacenar el estado


def load_state():
    if not os.path.exists(STATE_FILE):
        # Primera ejecución: guardamos la hora de inicio
        state = {"start_time": datetime.now().isoformat()}
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
        return state
    else:
        with open(STATE_FILE, "r") as f:
            return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def generate_article():
    # Define today's date
    today = datetime.now().strftime("%Y-%m-%d")

    # Generate a topic
    topic_prompt = (
        "Generate a catchy, SEO-optimized title for an article about Artificial Intelligence "
        "and technology trends that would appeal to an English-speaking audience in the U.S."
    )
    topic_resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a creative AI journalist."},
            {"role": "user",  "content": topic_prompt},
        ],
    )
    topic = topic_resp.choices[0].message.content.strip().replace('"', '')

    # Generate article content
    article_prompt = (
        f"Write a detailed, well-structured, SEO-friendly blog post titled '{topic}'. "
        "Include an engaging introduction, 3–4 informative sections with headings, "
        "and a short conclusion. Focus on AI and technology topics that interest U.S. readers."
    )
    article_resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert technology writer."},
            {"role": "user",   "content": article_prompt},
        ],
    )
    content = article_resp.choices[0].message.content.strip()

    # File name based on date and topic
    safe_topic = (
        topic.lower()
        .replace(" ", "-")
        .replace("/", "-")
        .replace(":", "")
        .replace("?", "")
        .replace('"', "")
    )
    filename = f"{today}-{safe_topic}.md"
    filepath = os.path.join(POSTS_DIR, filename)

    # Save article
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {topic}\n\n{content}")

    # Update posts.json
    if os.path.exists(POSTS_JSON):
        with open(POSTS_JSON, "r", encoding="utf-8") as f:
            posts = json.load(f)
    else:
        posts = []

    posts.insert(0, {"date": today, "title": topic, "file": filename})

    with open(POSTS_JSON, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2)

    print(f"✅ Generated new article: {filename}")


def run_bot():
    state = load_state()
    start_time = datetime.fromisoformat(state["start_time"])

    while True:
        now = datetime.now()
        elapsed = now - start_time

        # Primeras 30 horas
        if elapsed < timedelta(hours=30):
            print("⏰ Modo: PUBLICACIÓN CADA HORA")
            generate_article()
            time.sleep(3600)

        else:
            print("📅 Modo: PUBLICACIÓN SEMANAL")
            generate_article()
            # 1 semana = 7 días
            time.sleep(7 * 24 * 3600)


if __name__ == "__main__":
    run_bot()
