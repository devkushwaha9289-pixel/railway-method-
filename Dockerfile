FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

RUN apt-get update && apt-get install -y --no-install-recommends \
    xfce4 \
    xfce4-goodies \
    xrdp \
    dbus-x11 \
    dbus \
    sudo \
    openssh-server \
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
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /run/sshd /run/xrdp

COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 22 3389

CMD ["/start.sh"]
