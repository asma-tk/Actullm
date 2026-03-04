# defconn.py — Connexion ChromaDB
# En local  : connect_collection(host="localhost")
# En Docker : connect_collection(host="chromadb")
import chromadb

def connect_collection(
    name: str = "News",
    host: str = "chromadb",   # nom du service Docker
    port: int = 8000,
):
    client = chromadb.HttpClient(host=host, port=port)
    collection = client.get_or_create_collection(name=name)
    return collection