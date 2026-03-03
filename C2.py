from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
import requests

embeddings = OpenAIEmbeddings()

# Appeler l'API pour récupérer tous les articles
response = requests.get("http://localhost:8000/get_articles")
articles = response.json()  # liste de dicts

#reccuperation des données 

documents = []

for article in articles:
    doc = Document(
        page_content=article["content"],
        metadata={
            "title": article["title"],
            "date": article["date"],
            "region": article["region"],
            "url": article["url"]
        }
    )
    documents.append(doc)

# Chunk (découpage)
splitter = CharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunked_docs = splitter.split_documents(documents)


#vectorisation => embeddings 
vectorstore = FAISS.from_documents(
    chunked_docs,
    embeddings
)

#retrieval
retriever = vectorstore.as_retriever()

retriever = vectorstore.as_retriever(
    search_kwargs={"k": 3} #récupérer les 3 chunks les plus pertinents.
)