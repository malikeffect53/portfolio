FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV DATA_DIR=/data HTTPS=1
EXPOSE 8080
# One worker on purpose: the site uses a small SQLite database and a background backup scheduler.
CMD ["sh", "-c", "gunicorn -w 1 --threads 8 -b 0.0.0.0:${PORT:-8080} app:app"]
