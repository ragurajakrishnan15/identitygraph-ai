FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONPATH=/app/src:/app
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*  # needed by xgboost/lightgbm
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY configs ./configs
COPY src ./src
COPY backend ./backend
COPY alembic ./alembic
COPY alembic.ini .
COPY scripts ./scripts
# Synthetic data + model are built into the image so the container starts in seconds (no credentials/downloads).
RUN python scripts/generate_data.py && python scripts/validate_data.py && python scripts/train.py && python scripts/evaluate.py
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=5s --retries=10 CMD python -c "import os, urllib.request as u; u.urlopen('http://localhost:%s/api/v1/health' % os.getenv('PORT', '8000'))"
ENTRYPOINT ["./docker-entrypoint.sh"]
