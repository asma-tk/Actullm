import chromadb

# lancer dans dans le terminal avant de lancé le code --> chroma run --path ./ma_bdd --port 8000
import chromadb

def connect_collection():
    client = chromadb.HttpClient(
        host="localhost",
        port=8000
    )
    collection = client.get_or_create_collection(name="News")
    return collection 