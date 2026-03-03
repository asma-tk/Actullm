from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import requests


# Modèle pour un article
class Article(BaseModel):
    title: str
    content: str
    date: str
    region: str
    url: str

app = FastAPI()

# Stockage des articles en mémoire
all_articles: List[Article] = []

# Endpoint GET pour récupérer les articles
@app.get("/get_articles", response_model=List[Article])
def get_articles():
    return all_articles