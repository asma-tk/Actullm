from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import uvicorn

class Article(BaseModel):
    title: str
    content: str
    date: str
    region: str
    url: str

app = FastAPI()

all_articles: List[Article] = []

@app.post("/get_articles")
def add_articles(articles: List[Article]):
    all_articles.clear()
    all_articles.extend(articles)
    return {"status": "succès", "articles_reçus": len(articles)}

@app.get("/get_articles", response_model=List[Article])
def get_articles():
    return all_articles

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
    