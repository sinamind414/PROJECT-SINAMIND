ARG CACHEBUST=1
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    tesseract-ocr \
    tesseract-ocr-fra \
    tesseract-ocr-ara \
    && rm -rf /var/lib/apt/lists/*

COPY khawarizmi-backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY khawarizmi-backend/ .
RUN ls -la /app/data/ && ls -la /app/data/official/ && echo "✅ Data files verified"

EXPOSE 8000

CMD ["sh", "-c", \
     "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
