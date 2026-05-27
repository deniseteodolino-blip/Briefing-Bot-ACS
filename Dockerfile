FROM python:3.11-slim

WORKDIR /app

# Copia os arquivos de dependencia primeiro para otimizar o cache
COPY requirements.txt .

# Instala as dependencias do Python diretamente sem usar o apt-get
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia todo o projeto para o container
COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]