FROM python:3.12-slim AS backend
WORKDIR /app
COPY backend /app/backend
RUN pip install --no-cache-dir -e /app/backend
COPY frontend /app/frontend
RUN apt-get update && apt-get install -y --no-install-recommends nodejs npm && rm -rf /var/lib/apt/lists/*
RUN cd /app/frontend && npm install && npm run build
RUN mkdir -p /app/static && cp -r /app/frontend/dist/* /app/static/
COPY backend/app /app/app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
