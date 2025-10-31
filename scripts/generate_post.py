#!/usr/bin/env python3
# scripts/generate_post.py
import os
import re
import json
import openai
import random
from datetime import datetime

# ---------- CONFIG ----------
MODEL = os.getenv("OPENAI_MODEL", "gpt-5")
TOPICS = [
    "AI tools for productivity",
    "Machine learning trends in 2025",
    "How AI affects daily life",
    "Best AI startups to watch",
    "Ethical challenges of artificial intelligence",
    "AI for small businesses",
    "AI image generation tools comparison",
    "Prompt engineering tips for beginners",
]
POSTS_DIR = "posts"
INDEX_FILE = "posts.json"
# ----------------------------

openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise SystemExit("ERROR: OPENAI_API_KEY environment variable not found. Set it before running.")

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'\s+', '-', text).strip('-')
    return text[:80]

def build_prompt(topic):
    return f"""Write a detailed, useful and original blog article in Markdown (about 700-900 words)
for a US tech audience about "{topic}". Start with a catchy title on the first line (Markdown H1 or plain title),
include a short description meta (one sentence), then use subheadings (### or ##) and at least one bullet list.
Finish with a short conclusion and a suggested slug line.

Please return the article in the following exact format (so the script can parse it):

Title: <the title text here>
Description: <one-sentence description>
Slug: <suggested-slug-without-date>
---
<Here goes the full markdown article body (you may use H2/H3, lists, paragraphs).>
"""

def parse_response(text):
    title_match = re.search(r"^Title:\s*(.+)$", text, re.MULTILINE)
    desc_match = re.search(r"^Description:\s*(.+)$", text, re.MULTILINE)
    slug_match = re.search(r"^Slug:\s*([A-Za-z0-9\-\_]+)$", text, re.MULTILINE)
    body_split = re.split(r"^\s*---\s*$", text, flags=re.MULTILINE)
    body = body_split[-1].strip() if len(body_split) > 1 else text
    title = title_match.group(1).strip() if title_match else None
    description = desc_match.group(1).strip() if desc_match else ""
    slug = slug_match.group(1).strip() if slug_match else None
    return title, description, slug, body

def generate_article():
    topic = random.choice(TOPICS)
    prompt = build_prompt(topic)
    resp = openai.ChatCompletion.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2500
    )
    text = resp["choices"][0]["message"]["content"].strip()
    title, description, slug, body = parse_response(text)

    if not title:
        first_line = text.splitlines()[0]
        title = first_line.strip("# ").strip()
    if not slug:
        slug = slugify(title)

    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    filename = f"{POSTS_DIR}/{date_str}-{slug}.md"
    frontmatter = f"---\ntitle: \"{title}\"\ndescription: \"{description}\"\ndate: \"{date_str}\"\nslug: \"{slug}\"\n---\n\n"

    os.makedirs(POSTS_DIR, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(frontmatter)
        f.write(body)
    print(f"✅ Created: {filename}")

    update_index(title, description, date_str, filename)

def update_index(title, description, date_str, filepath):
    index = []
    if os.path.exists(INDEX_FILE):
        try:
            with open(INDEX_FILE, "r", encoding="utf-8") as f:
                index = json.load(f)
        except Exception:
            index = []

    entry = {
        "title": title,
        "description": description,
        "date": date_str,
        "url": "/" + filepath.replace(" ", "%20")
    }

    index.insert(0, entry)
    index = index[:50]
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
    print(f"✅ Updated index: {INDEX_FILE}")

if __name__ == "__main__":
    generate_article()

