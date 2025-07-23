#!/bin/bash

# MiolongVPN Uninstall Script

set -e

# Stop Docker container if running
docker stop miolongvpn 2>/dev/null || true
docker rm miolongvpn 2>/dev/null || true
docker rmi miolongvpn 2>/dev/null || true

# Stop OpenVPN and V2Ray services if running
systemctl stop openvpn 2>/dev/null || true
systemctl stop v2ray 2>/dev/null || true

# Remove OpenVPN configs and users
rm -rf /etc/openvpn/server/*

# Remove V2Ray configs and users
rm -rf /opt/v2ray/*

# Remove project files (run from project root)
cd "$(dirname "$0")"
cd ..
rm -rf MiolongVPN

# Remove Python packages (optional)
pip3 uninstall -y fastapi uvicorn jinja2 sqlalchemy passlib python-multipart aiofiles 2>/dev/null || true

# Remove Docker image
if command -v docker &> /dev/null; then
    docker rmi miolongvpn 2>/dev/null || true
fi

echo "MiolongVPN and all related files have been removed." 