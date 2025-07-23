import os
import subprocess
from fastapi import FastAPI, Request, Form, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from .models import Base, User, get_db, engine
from .vpn import create_openvpn_user, create_v2ray_user, get_openvpn_config, get_v2ray_config, create_wireguard_user, get_wireguard_config, create_l2tp_user, get_l2tp_info, get_bandwidth_usage, get_v2ray_config_file, get_shadowsocks_config_file, get_trojan_config_file
import re
from datetime import datetime
import socket

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# Create DB tables
Base.metadata.create_all(bind=engine)

# --- Authentication helpers ---
def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if user_id:
        return db.query(User).filter(User.id == user_id).first()
    return None

def require_admin(user=Depends(get_current_user)):
    if not user or not user.is_admin:
        return RedirectResponse("/login", status_code=302)
    return user

# --- Routes ---
@app.get("/", response_class=HTMLResponse)
def index(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

@app.get("/register", response_class=HTMLResponse)
def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Translation dictionary
translations = {
    'en': {
        'welcome': 'Welcome to MiolongVPN',
        'login': 'Login',
        'register': 'Register',
        'dashboard': 'Dashboard',
        'admin': 'Admin',
        'logout': 'Logout',
        'account_created': 'Your VPN account has been created.',
        'account_expired': 'Your VPN account has expired.',
    },
    'es': {
        'welcome': 'Bienvenido a MiolongVPN',
        'login': 'Iniciar sesión',
        'register': 'Registrarse',
        'dashboard': 'Panel',
        'admin': 'Administrador',
        'logout': 'Cerrar sesión',
        'account_created': 'Su cuenta VPN ha sido creada.',
        'account_expired': 'Su cuenta VPN ha expirado.',
    }
}

# Update registration to pass protocol info to email
@app.post("/register")
def register_post(request: Request, username: str = Form(...), password: str = Form(...), email: str = Form(...), language: str = Form('en'), db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username already exists."})
    user = User(username=username, password_hash=bcrypt.hash(password), email=email, language=language)
    db.add(user)
    db.commit()
    return RedirectResponse("/login", status_code=302)

@app.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Send expiration email on login if expired
@app.post("/login")
def login_post(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not bcrypt.verify(password, user.password_hash):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials."})
    # Check expiration
    if user.expiration_date and user.expiration_date < datetime.utcnow():
        return templates.TemplateResponse("login.html", {"request": request, "error": "Account expired."})
    user.last_login = datetime.utcnow()
    db.commit()
    request.session["user_id"] = user.id
    return RedirectResponse("/dashboard", status_code=302)

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, user=Depends(get_current_user)):
    if not user:
        return RedirectResponse("/login", status_code=302)
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "translations": translations})

@app.post("/dashboard/set_language")
def set_language(request: Request, language: str = Form(...), db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=302)
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.language = language
        db.commit()
    return RedirectResponse("/dashboard", status_code=302)

@app.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request, user=Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(User).all()
    return templates.TemplateResponse("admin.html", {"request": request, "user": user, "users": users, "translations": translations})

@app.post("/admin/create_openvpn")
def admin_create_openvpn(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    # Sanitize username and password
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return RedirectResponse("/admin?error=InvalidUsername", status_code=302)
    if len(password) < 6:
        return RedirectResponse("/admin?error=WeakPassword", status_code=302)
    user = db.query(User).filter(User.username == username).first()
    if user:
        create_openvpn_user(username, password)
    return RedirectResponse("/admin", status_code=302)

@app.post("/admin/create_v2ray")
def admin_create_v2ray(request: Request, username: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if user:
        create_v2ray_user(username)
    return RedirectResponse("/admin", status_code=302)

@app.post("/admin/set_expiration")
def admin_set_expiration(request: Request, username: str = Form(...), expiration_date: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if user:
        from datetime import datetime
        try:
            user.expiration_date = datetime.strptime(expiration_date, "%Y-%m-%d")
            db.commit()
        except Exception:
            pass
    return RedirectResponse("/admin", status_code=302)

@app.post("/admin/create_wireguard")
def admin_create_wireguard(request: Request, username: str = Form(...), db: Session = Depends(get_db)):
    import re
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return RedirectResponse("/admin?error=InvalidUsername", status_code=302)
    user = db.query(User).filter(User.username == username).first()
    if user:
        create_wireguard_user(username)
    return RedirectResponse("/admin", status_code=302)

@app.post("/admin/create_l2tp")
def admin_create_l2tp(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    import re
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return RedirectResponse("/admin?error=InvalidUsername", status_code=302)
    if len(password) < 6:
        return RedirectResponse("/admin?error=WeakPassword", status_code=302)
    user = db.query(User).filter(User.username == username).first()
    if user:
        create_l2tp_user(username, password)
    return RedirectResponse("/admin", status_code=302)

@app.get("/download/openvpn/{username}")
def download_openvpn(username: str):
    config = get_openvpn_config(username)
    return HTMLResponse(content=f"<pre>{config}</pre>")

@app.get("/download/v2ray/{username}")
def download_v2ray(username: str):
    config = get_v2ray_config(username)
    return HTMLResponse(content=f"<pre>{config}</pre>")

@app.get("/download/wireguard/{username}")
def download_wireguard(username: str):
    config = get_wireguard_config(username)
    return HTMLResponse(content=f"<pre>{config}</pre>")

@app.get("/download/l2tp/{username}")
def download_l2tp(username: str):
    info = get_l2tp_info(username)
    return HTMLResponse(content=f"<pre>{info}</pre>")

@app.get("/download/v2ray_config/{username}")
def download_v2ray_config(username: str):
    config = get_v2ray_config_file(username)
    return HTMLResponse(content=f"<pre>{config}</pre>")

@app.get("/download/shadowsocks_config/{username}")
def download_shadowsocks_config(username: str):
    config = get_shadowsocks_config_file(username)
    return HTMLResponse(content=f"<pre>{config}</pre>")

@app.get("/download/trojan_config/{username}")
def download_trojan_config(username: str):
    config = get_trojan_config_file(username)
    return HTMLResponse(content=f"<pre>{config}</pre>")

PROTOCOLS = [
    {"name": "OpenSSH", "ports": "22"},
    {"name": "OpenSSH (JIO5G NO PAYLOAD)", "ports": "53"},
    {"name": "SSH Websocket", "ports": "80"},
    {"name": "SSH SSL Websocket", "ports": "443"},
    {"name": "Stunnel4", "ports": "222, 777"},
    {"name": "Dropbear", "ports": "109, 143"},
    {"name": "Badvpn", "ports": "7100-7900"},
    {"name": "Nginx", "ports": "81"},
    {"name": "Vmess WS TLS", "ports": "443"},
    {"name": "Vless WS TLS", "ports": "443"},
    {"name": "Trojan WS TLS", "ports": "443"},
    {"name": "Shadowsocks WS TLS", "ports": "443"},
    {"name": "Vmess WS none TLS", "ports": "80"},
    {"name": "Vless WS none TLS", "ports": "80"},
    {"name": "Trojan WS none TLS", "ports": "80"},
    {"name": "Shadowsocks WS none TLS", "ports": "80"},
    {"name": "Vmess gRPC", "ports": "443"},
    {"name": "Vless gRPC", "ports": "443"},
    {"name": "Trojan gRPC", "ports": "443"},
    {"name": "Shadowsocks gRPC", "ports": "443"},
]

def check_port(port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        s.connect(("127.0.0.1", int(port)))
        s.close()
        return True
    except Exception:
        return False

def get_protocol_status():
    status_list = []
    for entry in PROTOCOLS:
        ports = entry["ports"].split(",")
        port_status = []
        for p in ports:
            p = p.strip()
            if "-" in p:
                start, end = map(int, p.split("-"))
                for port in range(start, end+1):
                    port_status.append(f"{port}:{'up' if check_port(port) else 'down'}")
            else:
                port_status.append(f"{p}:{'up' if check_port(p) else 'down'}")
        status_list.append({"name": entry["name"], "ports": entry["ports"], "status": ', '.join(port_status)})
    return status_list

@app.get("/server_info", response_class=HTMLResponse)
def server_info(request: Request):
    protocols = get_protocol_status()
    return templates.TemplateResponse("server_info.html", {"request": request, "protocols": protocols}) 