from fastapi import FastAPI
from pydantic import BaseModel
import requests
from defconn import connect_collection

app = FastAPI()
collection = connect_collection()

class Question(BaseModel):
    question: str
    model: str  # "mistral" ou "gpt-3.5-turbo"

def retrieve(question: str):
    results = collection.query(
        query_texts=[question],
        n_results=3
    )
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    return documents, metadatas

def build_prompt(question: str, documents: list) -> str:
    contexte = "\n- ".join(documents)
    prompt = f"""Tu es un assistant journaliste. Réponds en français
en te basant UNIQUEMENT sur le contexte fourni.

Contexte :
- {contexte}

Question : {question}
Réponse :"""
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

