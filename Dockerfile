FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-fra \
    tesseract-ocr-ara \
    && rm -rf /var/lib/apt/lists/*

COPY khawarizmi-backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /app/khawarizmi-backend

EXPOSE 8080

CMD ["python", "main.py"]
