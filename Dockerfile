# Stage 1: Build
FROM python:3.12-slim AS build
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Final Image
FROM python:3.12-slim
WORKDIR /app

COPY --from=build /install /usr/local
COPY . .

EXPOSE 8000
CMD ["python", "run.py"]