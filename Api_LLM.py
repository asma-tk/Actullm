"""
API LLM Gateway (FastAPI) -> Ollama

Contrat JSON (input):
{
  "model": "mistral",
  "prompt": "Ton prompt final..."
}

Contrat JSON (output):
{
  "model": "mistral",
  "response": "..."
}
"""

from __future__ import annotations

import os
import time
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


# -------------------------
# 1) Config: où est Ollama ?
# -------------------------
# Ollama expose une API HTTP locale par défaut sur http://localhost:11434
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Timeouts: évite que ton API reste bloquée si Ollama met trop de temps
HTTP_TIMEOUT_SECONDS = float(os.getenv("HTTP_TIMEOUT_SECONDS", "120"))


# -------------------------
# 2) Schémas Pydantic: contrat d'entrée/sortie
# -------------------------
class GenerateRequest(BaseModel):
    # Le modèle à utiliser côté Ollama (ex: "mistral", "llama3", etc.)
    model: str = Field(..., min_length=1, description="Nom du modèle Ollama à utiliser")
    # Le prompt FINAL (tu ne le modifies pas)
    prompt: str = Field(..., min_length=1, description="Prompt final déjà construit")


class GenerateResponse(BaseModel):
    model: str
    response: str
    latency_ms: int


# -------------------------
# 3) App FastAPI
# -------------------------
app = FastAPI(
    title="LLM Gateway API",
    version="1.0.0",
    description="Reçoit un prompt final en JSON, appelle Ollama, renvoie la réponse en JSON.",
)


# -------------------------
# 4) Endpoint principal: /generate
# -------------------------
@app.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest) -> GenerateResponse:
    """
    Ce endpoint:
    1) reçoit {model, prompt}
    2) appelle l'API Ollama /api/generate
    3) renvoie la réponse du modèle
    """

    start = time.perf_counter()

    # Payload attendu par Ollama (mode "generate" texte brut)
    # stream=False => on récupère une réponse complète (simple pour démarrer)
    ollama_payload = {
        "model": req.model,
        "prompt": req.prompt,
        "stream": False,
    }

    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_SECONDS) as client:
            r = await client.post(f"{OLLAMA_BASE_URL}/api/generate", json=ollama_payload)

    except httpx.ConnectError:
        # Ollama pas démarré / pas joignable
        raise HTTPException(
            status_code=503,
            detail="Ollama indisponible (vérifie que 'ollama serve' tourne et que l'URL est correcte).",
        )
    except httpx.ReadTimeout:
        # Ollama trop long -> timeout côté API
        raise HTTPException(
            status_code=504,
            detail="Timeout en attendant la réponse d'Ollama (réessaye ou augmente HTTP_TIMEOUT_SECONDS).",
        )
    except httpx.HTTPError as e:
        # Autres erreurs réseau
        raise HTTPException(status_code=502, detail=f"Erreur HTTP vers Ollama: {str(e)}")

    # Si Ollama renvoie une erreur HTTP
    if r.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"Ollama a renvoyé {r.status_code}: {r.text}",
        )

    data = r.json()

    # Réponse Ollama typique:
    # {
    #   "model": "...",
    #   "response": "...",
    #   "done": true,
    #   ...
    # }
    response_text: Optional[str] = data.get("response")
    if not response_text:
        raise HTTPException(
            status_code=502,
            detail=f"Réponse Ollama inattendue (champ 'response' manquant). Payload: {data}",
        )

    latency_ms = int((time.perf_counter() - start) * 1000)

    return GenerateResponse(
        model=req.model,
        response=response_text,
        latency_ms=latency_ms,
    )


# -------------------------
# 5) Endpoint santé: /health
# -------------------------
@app.get("/health")
async def health():
    """
    Permet de vérifier rapidement:
    - que TON API répond
    - que Ollama est joignable
    """
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"{OLLAMA_BASE_URL}/")
        ollama_ok = (r.status_code == 200)
    except Exception:
        ollama_ok = False

    return {
        "status": "ok",
        "ollama_url": OLLAMA_BASE_URL,
        "ollama_reachable": ollama_ok,
    }