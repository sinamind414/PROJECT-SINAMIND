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

# Copie explicite du fallback programme vital.
# Si ce COPY échoue, Railway n'utilise pas le bon contexte ou pas le bon commit.
COPY khawarizmi-backend/data/programmes/ ./data/programmes/

RUN echo "BUILD_MARKER=programme-json-copy-v2" && \
    python -c "import json, pathlib; p = pathlib.Path('/app/data/programmes/svt_sciences_experimentales.json'); assert p.exists(), f'MISSING_PROGRAMME_JSON: {p}'; data = json.loads(p.read_text(encoding='utf-8')); assert len(data.get('domains', [])) > 0, 'PROGRAMME_JSON_HAS_NO_DOMAINS'; print('PROGRAMME_JSON_OK', data.get('matiere'), data.get('filiere'), len(data.get('domains', [])))"

EXPOSE 8000

CMD ["sh", "-c", \
     "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
