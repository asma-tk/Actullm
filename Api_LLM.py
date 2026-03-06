from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

# --- App FastAPI ---
app = FastAPI()

# --- Contrat d'entrée ---
class GenerateRequest(BaseModel):
    model: str
    prompt: str

# --- Endpoint principal ---
@app.post("/generate")
async def generate(req: GenerateRequest):
    """
    Reçoit un JSON {model, prompt}
    -> envoie à Ollama
    -> renvoie {response}
    """
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": req.model,            #transforme en objet mais j'ai pas compris pk demandé a maxime plus tard 
                    "prompt": req.prompt,
                    "stream": False,  # réponse complète en une fois
                },
            )
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Ollama est down (localhost:11434).")
    except httpx.ReadTimeout:
        raise HTTPException(status_code=504, detail="Ollama timeout.")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Erreur HTTP vers Ollama: {e}")

    if r.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Ollama error {r.status_code}: {r.text}")

    data = r.json()
    return {"response": data.get("response", "")}