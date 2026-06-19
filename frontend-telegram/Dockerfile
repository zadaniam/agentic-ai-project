FROM python:3.10-slim

WORKDIR /app

# Salin file requirements khusus telegram bot
COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Salin seluruh kode di dalam folder frontend_telegram ke kontainer
COPY . .

# Jalankan skrip bot utama (tidak perlu uvicorn karena ini background worker)
CMD ["python", "bot.py"]
