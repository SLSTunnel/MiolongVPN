# MiolongVPN

A full-featured VPN management web application with support for OpenVPN, V2Ray, WireGuard, L2TP/IPsec, SSH, Shadowsocks, Trojan, and more. Includes user and admin panels, account management, downloadable VPN configuration files, and real-time server/port status.

---

## Features
- User registration and login (with email and language selection)
- Admin panel for user and VPN account management
- Automated OpenVPN, V2Ray, WireGuard, L2TP/IPsec, Shadowsocks, and Trojan account creation
- Downloadable config files for all major protocols
- Real-time port/service status page
- Multi-language support (English, Spanish)
- Dockerized for easy deployment
- Uninstall and setup scripts for full automation
- **Server banner:** By [Emperor]DevSupport

---

## Requirements
- Ubuntu 20.04+ (recommended for VPN server compatibility)
- Python 3.8+
- Docker (optional, for containerized deployment)
- Root access (for VPN protocol management)

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/MiolongVPN.git
cd MiolongVPN
```

### 2. Run the Service Setup Script
```bash
sudo bash setup_services.sh
```
- Installs and configures all major VPN/proxy services on the correct ports
- Prompts before overwriting existing configs
- Opens all required firewall ports

### 3. (Optional) Run with Docker
```bash
docker build -t miolongvpn .
docker run -d -p 80:8000 --cap-add=NET_ADMIN --name miolongvpn miolongvpn
```

### 4. Or Run Natively
```bash
sudo apt update
sudo apt install python3 python3-pip openvpn curl unzip -y
pip3 install -r requirements.txt
cd app
sudo python3 main.py
```

---

## Usage
- Access the web UI at `http://your-vps-ip/`
- Register a user or login as admin (default admin: `admin` / password: `admin123`)
- Admins can create VPN accounts for users, manage users, and download config files
- Users can view/download their VPN configs for OpenVPN, V2Ray, Shadowsocks, Trojan, WireGuard, and L2TP/IPsec
- Check real-time port/service status on the Server Info page (`/server_info`)
- All pages display a server banner: **By [Emperor]DevSupport**

---

## VPN Protocols Supported & Ports

| Protocol                  | Port(s)         |
|---------------------------|-----------------|
| OpenSSH                   | 22              |
| OpenSSH (JIO5G NO PAYLOAD)| 53              |
| SSH Websocket             | 80              |
| SSH SSL Websocket         | 443             |
| Stunnel4                  | 222, 777        |
| Dropbear                  | 109, 143        |
| Badvpn                    | 7100-7900, 7300 |
| Nginx                     | 81              |
| Vmess WS TLS              | 443             |
| Vless WS TLS              | 443             |
| Trojan WS TLS             | 443             |
| Shadowsocks WS TLS        | 443             |
| Vmess WS none TLS         | 80              |
| Vless WS none TLS         | 80              |
| Trojan WS none TLS        | 80              |
| Shadowsocks WS none TLS   | 80              |
| Vmess gRPC                | 443             |
| Vless gRPC                | 443             |
| Trojan gRPC               | 443             |
| Shadowsocks gRPC          | 443             |
| OpenVPN                   | 1194            |
| WireGuard                 | 51820           |
| L2TP/IPsec                | 1701, 500, 4500 |

---

## Installation Notes
- Dropbear is fully installed, enabled, and configured for ports 109 and 143, with banner support.
- Badvpn is running on ports 7100-7900 and 7300.
- All required ports are opened in the firewall.

---

## Config File Downloads
- Users can download ready-to-use config files for:
  - OpenVPN
  - V2Ray (VMess)
  - Shadowsocks
  - Trojan
  - WireGuard
- Download links are available in the user dashboard.

---

## Server Info Page
- Visit `/server_info` to see all supported protocols, ports, and real-time status (up/down) for each port.

---

## Uninstall
To remove the app and all VPN users/configs:
```bash
sudo bash uninstall.sh
```

---

## Health Check & Auto-Repair

A script `health_check.sh` is included to help you monitor and maintain your VPN server.

### Usage
```bash
sudo bash health_check.sh
```
- Checks the status of all major VPN/proxy services and their ports
- Attempts to auto-repair (restart) any failed services
- Restarts Badvpn processes if not running
- Outputs a summary with color-coded status
- Suggests manual intervention if a service cannot be auto-repaired

---

## Troubleshooting
- If a user cannot connect, run the health check script:
  ```bash
  sudo bash health_check.sh
  ```
- Check the `/server_info` page for real-time port status
- Ensure your VPS provider/firewall is not blocking required ports
- For persistent issues, check service logs (e.g., `sudo journalctl -u openvpn`)

---

## File Structure
```
MiolongVPN/
│
├── app/
│   ├── main.py
│   ├── models.py
│   ├── vpn.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── dashboard.html
│   │   ├── admin.html
│   │   ├── server_info.html
│   └── static/
│       └── style.css
│
├── requirements.txt
├── Dockerfile
├── uninstall.sh
├── setup_services.sh
└── README.md
```

---

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## License
MIT 

---

## VPN Banner Message

To display a banner message when users connect via SSH or Dropbear:

1. Edit `/etc/issue.net` and add:
   ```
   Powered By [Emperor]DevSupport
   ```
2. In `/etc/ssh/sshd_config`, ensure you have:
   ```
   Banner /etc/issue.net
   ```
   Then restart SSH:
   ```bash
   sudo systemctl restart ssh
   ```
3. For Dropbear, add to `/etc/default/dropbear`:
   ```
   DROPBEAR_BANNER="/etc/issue.net"
   ```
   Then restart Dropbear:
   ```bash
   sudo systemctl restart dropbear
   ```

For OpenVPN, WireGuard, V2Ray, Trojan, and Shadowsocks, a banner comment is included at the top of each generated config file:
```
# Powered By [Emperor]DevSupport
```

Note: Most VPN/proxy protocols do not support runtime banners, but the message will be visible in config files and SSH logins. 