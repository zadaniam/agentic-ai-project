FROM python:3.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .

# Port 7860 wajib digunakan di Hugging Face Spaces
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7860"]
