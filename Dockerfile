FROM python:3.11-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Streamlit port
EXPOSE 8501

CMD ["streamlit", "run", "streamlit_main.py", "--server.port=8501", "--server.address=0.0.0.0"]
