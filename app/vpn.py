import subprocess
import os
import re

# --- OpenVPN Integration ---
def create_openvpn_user(username, password):
    # Sanitize input
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        raise ValueError("Invalid username")
    if len(password) < 6:
        raise ValueError("Password too short")
    # Create system user for PAM auth
    try:
        subprocess.run(["sudo", "useradd", "-m", username], check=True)
    except subprocess.CalledProcessError:
        pass  # User may already exist
    subprocess.run(["sudo", "chpasswd"], input=f"{username}:{password}".encode(), check=True)
    # Optionally, add to a VPN group or set shell to /usr/sbin/nologin
    # subprocess.run(["sudo", "usermod", "-s", "/usr/sbin/nologin", username], check=True)
    # Use Easy-RSA to generate client certs
    cmd = f"cd /etc/openvpn/easy-rsa && ./easyrsa build-client-full {username} nopass"
    subprocess.run(cmd, shell=True, check=True)
    # Generate .ovpn config
    ovpn_path = f"/etc/openvpn/client-configs/{username}.ovpn"
    gen_cmd = f"/etc/openvpn/gen_ovpn.sh {username} > {ovpn_path}"
    subprocess.run(gen_cmd, shell=True, check=True)
    return ovpn_path

def get_openvpn_config(username):
    ovpn_path = f"/etc/openvpn/client-configs/{username}.ovpn"
    if os.path.exists(ovpn_path):
        with open(ovpn_path) as f:
            config = f.read()
        banner = '# Powered By [Emperor]DevSupport\n'
        return banner + config
    return "Config not found."

# --- V2Ray Integration ---
def create_v2ray_user(username):
    # Add user to V2Ray config (UUID generation and config update)
    import uuid, json
    v2ray_config = "/opt/v2ray/config.json"
    user_uuid = str(uuid.uuid4())
    if os.path.exists(v2ray_config):
        with open(v2ray_config, "r+") as f:
            config = json.load(f)
            config["inbounds"][0]["settings"]["clients"].append({"id": user_uuid, "email": username})
            f.seek(0)
            json.dump(config, f, indent=2)
            f.truncate()
        # Reload V2Ray
        subprocess.run("systemctl restart v2ray", shell=True)
    return user_uuid

def get_v2ray_config(username):
    # Find user's UUID in config
    import json
    v2ray_config = "/opt/v2ray/config.json"
    if os.path.exists(v2ray_config):
        with open(v2ray_config) as f:
            config = json.load(f)
            for client in config["inbounds"][0]["settings"]["clients"]:
                if client["email"] == username:
                    return f"V2Ray UUID: {client['id']}\nServer: your-vps-ip\nPort: 10086\nProtocol: vmess"
    return "Config not found."

def get_v2ray_config_file(username):
    banner = '# Powered By [Emperor]DevSupport\n'
    return banner + f'''{{
  "v": "2",
  "ps": "{username}-vmess",
  "add": "your-vps-ip",
  "port": "443",
  "id": "<UUID>",
  "aid": "0",
  "net": "ws",
  "type": "none",
  "host": "",
  "path": "/",
  "tls": "tls"
}}'''

def get_shadowsocks_config_file(username):
    banner = '# Powered By [Emperor]DevSupport\n'
    return banner + f'''{{
  "server": "your-vps-ip",
  "server_port": 443,
  "password": "<password>",
  "method": "aes-256-gcm",
  "plugin": "v2ray-plugin",
  "plugin_opts": "server;tls;host=your-vps-ip"
}}'''

def get_trojan_config_file(username):
    banner = '# Powered By [Emperor]DevSupport\n'
    return banner + f'''{{
  "run_type": "client",
  "local_addr": "127.0.0.1",
  "local_port": 1080,
  "remote_addr": "your-vps-ip",
  "remote_port": 443,
  "password": ["<password>"],
  "ssl": {{"verify": false, "sni": "your-vps-ip"}}
}}'''

def create_wireguard_user(username):
    import re, os, subprocess
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        raise ValueError("Invalid username")
    wg_dir = "/etc/wireguard/miolongvpn-users"
    os.makedirs(wg_dir, exist_ok=True)
    user_dir = os.path.join(wg_dir, username)
    os.makedirs(user_dir, exist_ok=True)
    private_key = subprocess.check_output(["wg", "genkey"]).decode().strip()
    public_key = subprocess.check_output(["wg", "pubkey"], input=private_key.encode()).decode().strip()
    with open(os.path.join(user_dir, "privatekey"), "w") as f:
        f.write(private_key)
    with open(os.path.join(user_dir, "publickey"), "w") as f:
        f.write(public_key)
    # Generate config
    config = f"""[Interface]\nPrivateKey = {private_key}\nAddress = 10.66.66.2/24\nDNS = 1.1.1.1\n\n[Peer]\nPublicKey = <SERVER_PUBLIC_KEY>\nEndpoint = your-vps-ip:51820\nAllowedIPs = 0.0.0.0/0\n"""
    with open(os.path.join(user_dir, "wg0.conf"), "w") as f:
        f.write(config)
    return os.path.join(user_dir, "wg0.conf")

def get_wireguard_config(username):
    user_dir = f"/etc/wireguard/miolongvpn-users/{username}"
    config_path = os.path.join(user_dir, "wg0.conf")
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = f.read()
        banner = '# Powered By [Emperor]DevSupport\n'
        return banner + config
    return "Config not found."

def create_l2tp_user(username, password):
    import re, subprocess
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        raise ValueError("Invalid username")
    if len(password) < 6:
        raise ValueError("Password too short")
    try:
        subprocess.run(["sudo", "useradd", "-m", username], check=True)
    except subprocess.CalledProcessError:
        pass  # User may already exist
    subprocess.run(["sudo", "chpasswd"], input=f"{username}:{password}".encode(), check=True)
    # Optionally, add to a VPN group or set shell to /usr/sbin/nologin
    # subprocess.run(["sudo", "usermod", "-s", "/usr/sbin/nologin", username], check=True)

def get_l2tp_info(username):
    # Replace with your actual server IP and PSK
    server_ip = "your-vps-ip"
    psk = "your-pre-shared-key"
    return f"Server: {server_ip}\nUsername: {username}\nPassword: (set by admin)\nPSK: {psk}\n"  # Password not stored for security

def get_vpn_interface_bandwidth(interface):
    import subprocess, re
    try:
        output = subprocess.check_output(["vnstat", "-i", interface], text=True)
        # Parse total RX/TX from output
        m = re.search(r"rx:\s*([0-9.]+)\s*(\w+)\s+tx:\s*([0-9.]+)\s*(\w+)", output)
        if m:
            rx, rx_unit, tx, tx_unit = m.groups()
            return f"RX: {rx} {rx_unit}, TX: {tx} {tx_unit}"
    except Exception:
        pass
    return "N/A"

def get_bandwidth_usage(username):
    # For demo: use tun0 for OpenVPN, wg0 for WireGuard, ppp0 for L2TP
    # In production, map user to IP/interface for per-user stats
    return get_vpn_interface_bandwidth("tun0") 