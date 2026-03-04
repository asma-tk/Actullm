FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install fastapi uvicorn pydantic requests feedparser langchain-community langchain-text-splitters faiss-cpu sentence-transformers chromadb

CMD ["sh", "-c", "uvicorn Api_add_articles:app --host 0.0.0.0 --port 8001 & sleep 5 && sleep 15 && python c2.py"]

RUN python rss_file.py
