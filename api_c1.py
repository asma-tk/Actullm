from fastapi import FastAPI
import requests
import uvicorn
import subprocess # Gardé pour lancer le fichier externe
import os

app = FastAPI()

# Adresse IP de ta collègue (C2)
ADRESSE_C2 = "http://127.0.0.1:8000/get_articles"
@app.post("/run-c1")
def trigger_rss():
    """Route qui lance le parser et envoie les données à C2."""
    try:
        # 1. On lance la récupération via le script externe (ton parser)
        # On utilise subprocess pour exécuter rss_file.py tel quel
        print("Lancement de rss_file.py...")
        subprocess.run(["python3", "rss_file.py"], check=True)
        
        # 2. On lit le résultat généré par ton parser (news.json)
        # pour confirmer l'envoi ou retourner les infos à l'interface
        import json
        with open("news.json", "r", encoding="utf-8") as f:
            data_articles = json.load(f)
        
        # Note: Comme ton rss_file.py fait déjà un requests.post, 
        # cette partie ci-dessous sert de double vérification ou de retour d'info.
        
        payload = {"articles": data_articles}
        
        # 3. ENVOI (déjà fait par rss_file.py, mais gardé selon ta structure)
        print(f"Envoi de {len(data_articles)} articles à C2...")
        response = requests.post(ADRESSE_C2, json=payload, timeout=20)
        
        return {
            "status": "succès",
            "articles_envoyés": len(data_articles),
            "réponse_c2": response.json()
        }
        
    except Exception as e:
        return {"status": "erreur", "message": str(e)}

if __name__ == "__main__":
    # Ton API sur le port 8001
    uvicorn.run(app, host="0.0.0.0", port=8001)