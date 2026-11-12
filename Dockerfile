FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONPATH=/app/src:/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY configs ./configs
COPY src ./src
COPY backend ./backend
COPY scripts ./scripts
# Data/artifacts are generated at start if missing (small, synthetic, no credentials needed).
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=5s --retries=10 CMD python -c "import urllib.request as u; u.urlopen('http://localhost:8000/api/v1/health')"
ENTRYPOINT ["./docker-entrypoint.sh"]
