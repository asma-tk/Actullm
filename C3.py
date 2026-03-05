from fastapi import FastAPI
from pydantic import BaseModel
import requests
from defconn import connect_collection

app = FastAPI()
collection = connect_collection()

class Question(BaseModel):
    question: str
    model: str  # model du llm

def retrieve(question: str):
    results = collection.query(
        query_texts=[question],
        n_results=3
    )
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    return documents, metadatas

def build_prompt(question: str, documents: list) -> str:
    contexte = "\n\n".join([f"Article {i+1} : {doc}" for i, doc in enumerate(documents)])
    
    prompt = f"""Tu es Kévin, un assistant journaliste expert en actualités internationales.

Ta mission :
- Répondre de manière CONCISE et PRÉCISE en 3-4 phrases maximum
- Te baser UNIQUEMENT sur les articles fournis ci-dessous
- Citer les faits importants : chiffres, dates, lieux, noms
- Si les articles ne contiennent pas la réponse, dire clairement : "Je n'ai pas d'information sur ce sujet dans mes sources."
- Ne jamais inventer ou compléter avec des connaissances extérieures

Articles disponibles :
{contexte}

Question posée : {question}

Réponds de manière directe, factuelle et résumée en français :"""
    
    return prompt

def ask_llm(model: str, prompt: str) -> str:
    response = requests.post(
        "http://localhost:8005/generate",
        json={
            "model": model,
            "prompt": prompt
        }
    )
    return response.json()["response"]

@app.post("/process")
def process(body: Question):
    documents, metadatas = retrieve(body.question)
    prompt = build_prompt(body.question, documents)
    answer = ask_llm(body.model, prompt)
    sources = [
        {
            "title": m.get("title", ""),
            "region": m.get("region", ""),
            "date": m.get("date", "")
        }
        for m in metadatas
    ]
    return {"answer": answer, "sources": sources}

