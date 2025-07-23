#!/bin/bash

# MiolongVPN Service Setup Script
# Installs and configures all VPN/proxy services on specified ports
# Prompts before overwriting existing configs

set -e

# Function to prompt before overwriting
prompt_overwrite() {
    if [ -f "$1" ]; then
        read -p "Config $1 exists. Overwrite? (y/n): " yn
        case $yn in
            [Yy]*) return 0;;
            *) echo "Skipping $1"; return 1;;
        esac
    fi
    return 0
}

# Update and install base packages
echo "[+] Updating system and installing base packages..."
sudo apt update && sudo apt install -y openssh-server dropbear stunnel4 badvpn nginx openvpn easy-rsa wireguard strongswan xl2tpd python3-pip curl unzip socat

# OpenSSH (22, 53)
echo "[+] Configuring OpenSSH..."
sudo sed -i '/^Port /d' /etc/ssh/sshd_config
sudo bash -c 'echo "Port 22\nPort 53" >> /etc/ssh/sshd_config'
sudo systemctl restart ssh

# Dropbear (109, 143)
echo "[+] Configuring Dropbear..."
sudo apt install -y dropbear
sudo sed -i 's/^NO_START=1/NO_START=0/' /etc/default/dropbear
sudo sed -i 's/^DROPBEAR_PORT=.*/DROPBEAR_PORT=109/' /etc/default/dropbear
sudo sed -i '/DROPBEAR_EXTRA_ARGS/d' /etc/default/dropbear
sudo bash -c 'echo "DROPBEAR_EXTRA_ARGS=\"-p 109 -p 143\"" >> /etc/default/dropbear'
sudo bash -c 'echo "DROPBEAR_BANNER=\"/etc/issue.net\"" >> /etc/default/dropbear'
sudo systemctl enable dropbear
sudo systemctl restart dropbear

# Stunnel4 (222, 777)
echo "[+] Configuring Stunnel4..."
if prompt_overwrite "/etc/stunnel/stunnel.conf"; then
sudo bash -c 'cat > /etc/stunnel/stunnel.conf <<EOF
[ssh]
accept = 222
connect = 127.0.0.1:22
[ssh2]
accept = 777
connect = 127.0.0.1:22
EOF'
fi
sudo systemctl restart stunnel4

# Badvpn (7100-7900, 7300)
echo "[+] Starting Badvpn UDPGW on ports 7100-7900 and 7300..."
for port in $(seq 7100 100 7900); do
    nohup badvpn-udpgw --listen-addr 127.0.0.1:$port &
done
nohup badvpn-udpgw --listen-addr 127.0.0.1:7300 &

# Nginx (81)
echo "[+] Configuring Nginx on port 81..."
if prompt_overwrite "/etc/nginx/sites-available/miolongvpn"; then
sudo bash -c 'cat > /etc/nginx/sites-available/miolongvpn <<EOF
server {
    listen 81 default_server;
    server_name _;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF'
fi
sudo ln -sf /etc/nginx/sites-available/miolongvpn /etc/nginx/sites-enabled/miolongvpn
sudo systemctl reload nginx

# V2Ray/XRay, Trojan, Shadowsocks (443, 80)
echo "[+] Downloading and configuring V2Ray/XRay, Trojan, Shadowsocks..."
# (You may want to use official install scripts for these, or use xrayr for all-in-one)
# Placeholders for user to fill in with their preferred method

# OpenVPN (1194), WireGuard (51820), L2TP/IPsec (1701, 500, 4500)
echo "[+] Ensuring OpenVPN, WireGuard, and L2TP/IPsec are installed..."
# (Assume configs are managed by the app or manually)

# Firewall rules
echo "[+] Opening firewall ports..."
for port in 22 53 80 81 109 143 222 443 777 1194 51820 1701 500 4500 7300; do
    sudo ufw allow $port
    sudo ufw allow $port/udp
    sudo ufw allow $port/tcp
    echo "[+] Allowed port $port (TCP/UDP)"
done
for port in $(seq 7100 100 7900); do
    sudo ufw allow $port
    sudo ufw allow $port/udp
    sudo ufw allow $port/tcp
    echo "[+] Allowed port $port (TCP/UDP)"
done

sudo ufw reload

echo "[+] All services installed/configured. Please check each service's config for custom settings."
echo "[!] For V2Ray/XRay, Trojan, Shadowsocks, please use their official scripts or xrayr for full automation."
echo "[!] For SSL certificates, use certbot or your preferred method." 