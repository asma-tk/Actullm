uvicorn api_front:app --port 8002 --reload & \
uvicorn C3:app --port 8004 --reload & \
uvicorn Api_LLM:app --port 8005 --reload