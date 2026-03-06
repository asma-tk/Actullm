from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

class Question(BaseModel):
    question: str
    model: str

@app.post("/ask")
def ask(body: Question):
    response = requests.post(
        "http://localhost:8004/process",
        json={
            "question": body.question,
            "model": body.model
        }
    )
    return response.json()