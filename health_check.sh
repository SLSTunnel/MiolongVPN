#!/bin/bash

# MiolongVPN Advanced Health Check & Auto-Repair Script
# Checks all services and ports, restarts failed services, and outputs a summary

SERVICES=(ssh dropbear stunnel4 nginx openvpn wg-quick@wg0 strongswan xl2tpd)
PORTS=(22 53 80 81 109 143 222 443 777 1194 51820 1701 500 4500)
BADVPN_PORTS=$(seq 7100 100 7900)

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_service() {
    systemctl is-active --quiet "$1"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[OK]${NC} Service $1 is running."
    else
        echo -e "${RED}[FAIL]${NC} Service $1 is NOT running. Attempting restart..."
        sudo systemctl restart "$1"
        sleep 2
        systemctl is-active --quiet "$1"
        if [ $? -eq 0 ]; then
            echo -e "${YELLOW}[FIXED]${NC} Service $1 restarted successfully."
        else
            echo -e "${RED}[ERROR]${NC} Service $1 failed to start. Please check logs: sudo journalctl -u $1"
        fi
    fi
}

check_port() {
    nc -z -w2 127.0.0.1 "$1" >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[OPEN]${NC} Port $1 is open."
    else
        echo -e "${RED}[CLOSED]${NC} Port $1 is closed."
    fi
}

echo "--- Service Health Check ---"
for svc in "${SERVICES[@]}"; do
    check_service "$svc"
done

echo "--- Port Health Check ---"
for port in "${PORTS[@]}"; do
    check_port "$port"
done
for port in $BADVPN_PORTS; do
    check_port "$port"
done

# Check Badvpn processes
BADVPN_COUNT=$(ps aux | grep badvpn-udpgw | grep -v grep | wc -l)
if [ $BADVPN_COUNT -ge 1 ]; then
    echo -e "${GREEN}[OK]${NC} Badvpn processes running: $BADVPN_COUNT"
else
    echo -e "${RED}[FAIL]${NC} No Badvpn processes found. Attempting to start..."
    for port in $BADVPN_PORTS; do
        nohup badvpn-udpgw --listen-addr 127.0.0.1:$port &
    done
    sleep 2
    BADVPN_COUNT=$(ps aux | grep badvpn-udpgw | grep -v grep | wc -l)
    if [ $BADVPN_COUNT -ge 1 ]; then
        echo -e "${YELLOW}[FIXED]${NC} Badvpn processes started."
    else
        echo -e "${RED}[ERROR]${NC} Badvpn failed to start. Please check manually."
    fi
fi

echo "--- Health Check Complete ---" 