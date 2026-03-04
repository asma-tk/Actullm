from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import uvicorn
import json

class Article(BaseModel):
    title: str
    content: str
    date: str
    region: str
    url: str

app = FastAPI()

all_articles: List[Article] = []
# va chercher les données dans le json et tu les mets dans all_articles


with open("news.json", "r", encoding="utf-8") as f:
    data_articles = json.load(f)
    all_articles = [Article(**article) for article in data_articles]

@app.post("/get_articles")
def add_articles(articles: List[Article]):
    global all_articles # Ensure we are targeting the global list
    all_articles.extend(articles)
    print(f"DEBUG: Received {len(articles)} articles. Total now: {len(all_articles)}")
    return {"status": "succès", "articles_reçus": len(articles)}

@app.get("/get_articles", response_model=List[Article])
def get_articles():
    return all_articles

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
    