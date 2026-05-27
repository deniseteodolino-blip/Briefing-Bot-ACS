# Usa a imagem oficial do Python 3.11
FROM python:3.11-slim

# Define o diretório de trabalho no container
WORKDIR /app

# Instala as dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copia apenas o requirements primeiro (aproveita cache do Docker)
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código para dentro do container
COPY . .

# Expõe a porta padrão do Streamlit
EXPOSE 8501

# Cria diretório de cache
RUN mkdir -p /root/.briefing-bot-cache

# Comando para iniciar a aplicação
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]