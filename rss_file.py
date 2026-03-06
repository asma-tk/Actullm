import feedparser  #rss_file.py
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

articles = []  #Liste pour stocker les articles extraits de tous les flux RSS

# --- ÉTAPE C1 : RÉCUPÉRATION ---
for region, url in feeds.items():                         # Parcourir chaque région et son URL de flux RSS
    print(f"Récupération : {region}...")   # Afficher la région en cours de traitement
    feed = feedparser.parse(url)          # Récupérer et parser le flux RSS de la région actuelle
    
    
    for entry in feed.entries:     # Parcourir chaque article (entry) dans le flux RSS
        articles.append({
            "region": region,
            "title": entry.get("title"),
            "date": entry.get("published"),
            "content": clean(entry.get("summary")),
            "url": entry.get("link"),
        })

print(f"Total articles récupérés : {len(articles)}")

with open("news.json", "w", encoding="utf-8") as f: 
    json.dump(articles, f, ensure_ascii=False, indent=2)
print("news.json créé avec succès !")

print("Envoi des données à l'API de vectorisation...")

