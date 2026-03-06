from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter
import chromadb
from chromadb.config import Settings
import requests
from defconn import connect_collection


response = requests.get("http://localhost:8001/get_articles")
articles = response.json()

documents = []
for article in articles:
    doc = Document(
        page_content=str(article["content"]),
        metadata={
            "title": article["title"],
            "date": article["date"],
            "region": article["region"],
            "url": article["url"]
        }
    )
    documents.append(doc)



splitter = CharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
chunked_docs = splitter.split_documents(documents)





collection = connect_collection()



ids = []
embeddings_list = []
documents_list = []
metadatas_list = []

for i, chunk in enumerate(chunked_docs):
    #embedding = vectorstore.index.reconstruct(i).tolist()
    ids.append(str(i))
    #embeddings_list.append(embedding)
    documents_list.append(chunk.page_content)
    metadatas_list.append(chunk.metadata)

collection.upsert(
    ids=ids,
    #embeddings=embeddings_list,
    documents=documents_list,
    metadatas=metadatas_list
)
