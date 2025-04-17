FROM python:3.9-slim
WORKDIR /app

# Install TA-Lib dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libta-lib-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
