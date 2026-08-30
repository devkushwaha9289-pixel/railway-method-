FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV TZ=UTC

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server \
    sudo \
    bash \
    ca-certificates \
    curl \
    wget \
    git \
    nano \
    vim \
    tmux \
    screen \
    procps \
    iproute2 \
    iputils-ping \
    dnsutils \
    net-tools \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    unzip \
    zip \
    tar \
    gzip \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /run/sshd

COPY start.sh /usr/local/bin/start.sh

RUN chmod +x /usr/local/bin/start.sh

EXPOSE 22

CMD ["/usr/local/bin/start.sh"]
