# MiolongVPN Dockerfile
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip openvpn curl unzip supervisor && \
    rm -rf /var/lib/apt/lists/*

# Install V2Ray
RUN mkdir -p /opt/v2ray && \
    curl -L -o /opt/v2ray/v2ray.zip https://github.com/v2fly/v2ray-core/releases/latest/download/v2ray-linux-64.zip && \
    unzip /opt/v2ray/v2ray.zip -d /opt/v2ray && \
    chmod +x /opt/v2ray/v2ray*

# Set up app directory
WORKDIR /app
COPY . /app

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose web and VPN ports
EXPOSE 8000 1194/udp 1194/tcp 10086/tcp 10086/udp

# Start OpenVPN, V2Ray, and FastAPI app
CMD ["bash", "-c", "supervisord -c /app/app/supervisord.conf && uvicorn app.main:app --host 0.0.0.0 --port 8000"] 