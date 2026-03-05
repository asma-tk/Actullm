from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
from defconn import connect_collection

# Les 4 terminaux :

# chroma run --path ./ma_bdd --port 8003
# uvicorn C3:app --port 8004
# uvicorn api_front:app --port 8002
# streamlit run app.py


# Le flux complet :

# FRONT → api_front (8002) → C3 (8004) → ChromaDB/Mistral/ChatGPT                                             ↓
# FRONT ← api_front (8002) ← C3 (8004) ←  réponse

from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
from defconn import connect_collection

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI()
collection = connect_collection()

class Question(BaseModel):
    question: str
    mode: str  # "rag_mistral", "rag_chatgpt", "mistral", "chatgpt"

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

def ask_mistral(prompt: str) -> str:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"]

def ask_chatgpt(prompt: str) -> str:
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        json={
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "Tu es un assistant journaliste. Réponds en français."},
                {"role": "user", "content": prompt}
            ]
        }
    )
    return response.json()["choices"][0]["message"]["content"]

@app.post("/process")
def process(body: Question):

    # MODE RAG + MISTRAL
    if body.mode == "rag_mistral":
        documents, metadatas = retrieve(body.question)
        prompt = build_prompt(body.question, documents)
        answer = ask_mistral(prompt)
        sources = [{"title": m.get("title", ""), "region": m.get("region", ""), "date": m.get("date", "")} for m in metadatas]
        return {"answer": answer, "sources": sources}

    # MODE RAG + CHATGPT
    elif body.mode == "rag_chatgpt":
        documents, metadatas = retrieve(body.question)
        prompt = build_prompt(body.question, documents)
        answer = ask_chatgpt(prompt)
        sources = [{"title": m.get("title", ""), "region": m.get("region", ""), "date": m.get("date", "")} for m in metadatas]
        return {"answer": answer, "sources": sources}

    # MODE MISTRAL DIRECT
    elif body.mode == "mistral":
        answer = ask_mistral(body.question)
        return {"answer": answer, "sources": []}

    # MODE CHATGPT DIRECT
    elif body.mode == "chatgpt":
        answer = ask_chatgpt(body.question)
        return {"answer": answer, "sources": []}

    else:
        return {"answer": "Mode inconnu.", "sources": []}