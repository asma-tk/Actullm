import requests #api_c1.py
import subprocess
import json

ADRESSE_C2 = "http://127.0.0.1:8001/get_articles"

def trigger_rss():
    try:
        print("Lancement de rss_file.py...")
        subprocess.run(["python3", "rss_file.py"], check=True)

        with open("news.json", "r", encoding="utf-8") as f:
            data_articles = json.load(f)

        print(f"Envoi de {len(data_articles)} articles à C2...")
        response = requests.post(ADRESSE_C2, json=data_articles, timeout=20)

        return {
            "status": "succès",
            "articles_envoyés": len(data_articles),
            "réponse_c2": response.json()
        }

    except Exception as e:
        return {"status": "erreur", "message": str(e)}

if __name__ == "__main__":
    print(trigger_rss())