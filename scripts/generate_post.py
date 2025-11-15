from openai import OpenAI
import json
import os
from datetime import datetime

client = OpenAI()

POSTS_DIR = "posts"
os.makedirs(POSTS_DIR, exist_ok=True)

POSTS_JSON = "posts.json"


def generate_article():

    today = datetime.utcnow().strftime("%Y-%m-%d-%H-%M")

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

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {topic}\n\n{content}")

    if os.path.exists(POSTS_JSON):
        with open(POSTS_JSON, "r", encoding="utf-8") as f:
            posts = json.load(f)
    else:
        posts = []

    posts.insert(0, {"date": today, "title": topic, "file": filename})

    with open(POSTS_JSON, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2)

    print(f"✅ New article generated: {filename}")


if __name__ == "__main__":
    generate_article()
