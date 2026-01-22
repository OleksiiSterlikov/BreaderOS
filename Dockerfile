FROM python:3.12-slim

# Не пишемо .pyc і логи в stdout одразу
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Системні залежності (мінімум)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python залежності
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Код застосунку
COPY . .

# Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["python", "app.py"]
