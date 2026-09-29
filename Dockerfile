FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    curl \
    wget \
    git \
    ca-certificates \
    unzip \
    zip \
    procps \
    iproute2 \
    dnsutils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY server.py .

EXPOSE 8080

CMD ["python3", "server.py"]
