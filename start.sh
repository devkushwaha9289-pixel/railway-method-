#!/usr/bin/env bash
set -Eeuo pipefail

# ==========================================
# RAILWAY VPS - ROOT SSH
# ==========================================

SSH_PASSWORD="VILLAGEE@121"

if [[ -z "$SSH_PASSWORD" ]]; then
    echo "ERROR: SSH_PASSWORD Railway variable is not set."
    exit 1
fi

mkdir -p /run/sshd
mkdir -p /etc/ssh/sshd_config.d

# Generate SSH host keys
ssh-keygen -A

# Set root password
echo "root:${SSH_PASSWORD}" | chpasswd

# ==========================================
# SSH CONFIG
# ==========================================

cat > /etc/ssh/sshd_config.d/railway.conf <<EOF
Port 22
ListenAddress 0.0.0.0

PermitRootLogin yes
PasswordAuthentication yes
PubkeyAuthentication yes
KbdInteractiveAuthentication no

UsePAM no

X11Forwarding no
PrintMotd no

ClientAliveInterval 60
ClientAliveCountMax 3
TCPKeepAlive yes
EOF

# Remove conflicting settings from main config
sed -i \
    -e 's/^#\?PermitRootLogin.*/# PermitRootLogin/' \
    -e 's/^#\?PasswordAuthentication.*/# PasswordAuthentication/' \
    /etc/ssh/sshd_config

# Validate SSH configuration
echo "Checking SSH configuration..."
/usr/sbin/sshd -t

if [[ $? -ne 0 ]]; then
    echo "ERROR: SSH configuration test failed."
    exit 1
fi

echo ""
echo "=========================================="
echo "       RAILWAY VPS READY"
echo "=========================================="
echo "SSH User : root"
echo "SSH Port : 22"
echo "Root     : ENABLED"
echo "=========================================="
echo ""

# Keep SSH as PID 1 / foreground process.
# Railway will keep the container alive while this runs.
exec /usr/sbin/sshd -D -e
