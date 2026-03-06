FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.deploy.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.deploy.txt

COPY . .

EXPOSE 8000 8001 8002 8004 8005 8501

CMD ["sh", "-c", "\
chroma run --path ./ma_bdd --port 8000 & \
sleep 8 && \
uvicorn Api_add_articles:app --host 0.0.0.0 --port 8001 & \
sleep 3 && \
python C2.py && \
uvicorn api_front:app --host 0.0.0.0 --port 8002 & \
uvicorn C3:app --host 0.0.0.0 --port 8004 & \
uvicorn Api_LLM:app --host 0.0.0.0 --port 8005 & \
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 \
"]