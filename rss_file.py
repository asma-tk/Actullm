import feedparser
import json
import re

feeds = {
    "europe": "https://www.france24.com/fr/europe/rss",
    "afrique": "https://www.france24.com/fr/afrique/rss",
    "ameriques": "https://www.france24.com/fr/am%C3%A9riques/rss",
    "asie": "https://www.france24.com/fr/asie-pacifique/rss",
    "moyen_orient": "https://www.france24.com/fr/moyen-orient/rss",
}

def clean(text):
    return re.sub(r"<.*?>", "", text or "").strip()

articles = []

for region, url in feeds.items():
    feed = feedparser.parse(url)

    for entry in feed.entries:
        articles.append({
            "region": region,
            "title": entry.get("title"),
            "date": entry.get("published"),
            "content": clean(entry.get("summary")),
            "url": entry.get("link"),
        })

print("Total articles :", len(articles))

# Sauvegarde JSON
with open("news.json", "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print("news.json créé ✅")