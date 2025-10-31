from openai import OpenAI
import json
import os
from datetime import datetime

# Initialize OpenAI client
client = OpenAI()

# Folder to store posts
POSTS_DIR = "posts"
os.makedirs(POSTS_DIR, exist_ok=True)

# File to keep track of posts
POSTS_JSON = "posts.json"


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
            {"role": "user", "content": topic_prompt},
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
            {"role": "user", "content": article_prompt},
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


if __name__ == "__main__":
    generate_article()
