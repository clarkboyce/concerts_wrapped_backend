FROM python:3.12

WORKDIR /app

COPY requirements.txt .
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python", "run.py"]