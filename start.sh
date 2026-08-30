#!/usr/bin/env bash
set -Eeuo pipefail

# =========================================
# CHANGE THESE TWO PASSWORDS
# =========================================

ROOT_PASSWORD="6698156001"
RDP_PASSWORD="6698156001"

RDP_USER="villagee"

# =========================================
# SSH
# =========================================

mkdir -p /run/sshd /run/xrdp
ssh-keygen -A

# =========================================
# RDP USER
# =========================================

if ! id "$RDP_USER" >/dev/null 2>&1; then
    useradd -m -s /bin/bash "$RDP_USER"
fi

echo "${RDP_USER}:${RDP_PASSWORD}" | chpasswd

# Full administrative/root privileges
usermod -aG sudo "$RDP_USER"

cat > "/etc/sudoers.d/${RDP_USER}" <<EOF
${RDP_USER} ALL=(ALL) NOPASSWD:ALL
EOF

chmod 440 "/etc/sudoers.d/${RDP_USER}"

# =========================================
# ROOT SSH PASSWORD
# =========================================

echo "root:${ROOT_PASSWORD}" | chpasswd

# =========================================
# XFCE
# =========================================

cat > "/home/${RDP_USER}/.xsession" <<'EOF'
#!/bin/sh

export LANG=C.UTF-8
export LC_ALL=C.UTF-8

unset DBUS_SESSION_BUS_ADDRESS
unset XDG_RUNTIME_DIR

exec startxfce4
EOF

chmod +x "/home/${RDP_USER}/.xsession"
chown "${RDP_USER}:${RDP_USER}" "/home/${RDP_USER}/.xsession"

# =========================================
# XRDP
# =========================================

cat > /etc/xrdp/startwm.sh <<'EOF'
#!/bin/sh

export LANG=C.UTF-8
export LC_ALL=C.UTF-8

unset DBUS_SESSION_BUS_ADDRESS
unset XDG_RUNTIME_DIR

exec startxfce4
EOF

chmod +x /etc/xrdp/startwm.sh

# =========================================
# SSH CONFIG
# =========================================

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

/usr/sbin/sshd -t

# =========================================
# DBUS
# =========================================

dbus-daemon --system --fork || true

# =========================================
# START XRDP
# =========================================

/usr/sbin/xrdp-sesman --nodaemon &
XRDP_SESMAN_PID=$!

sleep 1

/usr/sbin/xrdp --nodaemon &
XRDP_PID=$!

# =========================================
# START SSH
# =========================================

/usr/sbin/sshd

echo ""
echo "=========================================="
echo "       RAILWAY VPS + RDP READY"
echo "=========================================="
echo ""
echo "SSH:"
echo "  User: root"
echo "  Port: 22"
echo ""
echo "RDP:"
echo "  User: ${RDP_USER}"
echo "  Port: 3389"
echo ""
echo "RDP user has FULL sudo/root privileges."
echo "Inside RDP terminal run: sudo -i"
echo "=========================================="

# =========================================
# KEEP SERVICES ALIVE
# =========================================

while true; do

    if ! kill -0 "$XRDP_SESMAN_PID" 2>/dev/null; then
        /usr/sbin/xrdp-sesman --nodaemon &
        XRDP_SESMAN_PID=$!
    fi

    if ! kill -0 "$XRDP_PID" 2>/dev/null; then
        /usr/sbin/xrdp --nodaemon &
        XRDP_PID=$!
    fi

    if ! pgrep -x sshd >/dev/null 2>&1; then
        /usr/sbin/sshd
    fi

    sleep 10
done
