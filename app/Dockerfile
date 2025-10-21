# app/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Streamlit
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_HEADLESS=true
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
EXPOSE 8501

# Setup an app user so the container doesn't run as the root user
RUN useradd app
USER app

# Démarrage (Render injecte $PORT)
# CMD streamlit run app.py --server.port 8501 --server.address 0.0.0.0
CMD streamlit run app.py --server.port 8501 --server.address 0.0.0.0