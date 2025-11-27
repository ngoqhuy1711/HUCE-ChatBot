# Hướng Dẫn Triển Khai - HUCE Chatbot

**Phiên bản:** 1.0.0  
**Cập nhật:** 2025-11-25

---

## 📚 Mục Lục

1. [Yêu Cầu](#yêu-cầu)
2. [Development Local](#development-local)
3. [Triển Khai Production](#triển-khai-production)
4. [Triển Khai Docker](#triển-khai-docker)
5. [Cấu Hình Environment](#cấu-hình-environment)
6. [Monitoring](#monitoring)
7. [Troubleshooting](#troubleshooting)

---

## ✅ Yêu Cầu

### Yêu Cầu Hệ Thống

**Tối thiểu:**

- CPU: 2 cores
- RAM: 2GB
- Disk: 5GB
- OS: Windows 10+, Ubuntu 20.04+, macOS 11+

**Khuyến nghị:**

- CPU: 4 cores
- RAM: 4GB
- Disk: 10GB
- OS: Ubuntu 22.04 LTS

### Yêu Cầu Phần Mềm

- Python 3.13+
- pip hoặc uv package manager
- Git
- (Tùy chọn) Docker & Docker Compose

---

## 💻 Development Local

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/your-org/huce-chatbot.git
cd huce-chatbot

# 2. Cài đặt dependencies
pip install uv
uv sync

# 3. Cấu hình environment
cp env.example .env
# Chỉnh sửa .env với settings của bạn

# 4. Chạy tests
pytest

# 5. Chạy backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 6. Chạy frontend (terminal riêng)
cd frontend
reflex run
```

### Điểm Truy Cập

- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Frontend:** http://localhost:3000

---

## 🚀 Triển Khai Production

### Tùy Chọn 1: Triển Khai Trực Tiếp (VPS/Cloud)

#### Bước 1: Setup Server

```bash
# Cập nhật hệ thống
sudo apt update && sudo apt upgrade -y

# Cài đặt Python 3.13
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.13 python3.13-venv python3.13-dev

# Cài đặt system dependencies
sudo apt install git nginx supervisor
```

#### Bước 2: Setup Ứng Dụng

```bash
# Tạo application user
sudo useradd -m -s /bin/bash chatbot
sudo su - chatbot

# Clone repository
git clone https://github.com/your-org/huce-chatbot.git
cd huce-chatbot

# Setup virtual environment
python3.13 -m venv .venv
source .venv/bin/activate

# Cài đặt dependencies
pip install uv
uv sync --no-dev

# Cấu hình environment
cp env.example .env
nano .env  # Chỉnh sửa cấu hình
```

#### Bước 3: Cấu Hình Supervisor

```bash
# Tạo supervisor config
sudo nano /etc/supervisor/conf.d/chatbot.conf
```

```ini
[program:chatbot-backend]
command=/home/chatbot/huce-chatbot/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
directory=/home/chatbot/huce-chatbot
user=chatbot
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/chatbot/backend.log
environment=LOG_LEVEL="INFO"

[program:chatbot-frontend]
command=/home/chatbot/huce-chatbot/.venv/bin/reflex run --env prod
directory=/home/chatbot/huce-chatbot/frontend
user=chatbot
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/chatbot/frontend.log
```

```bash
# Tạo log directory
sudo mkdir -p /var/log/chatbot
sudo chown chatbot:chatbot /var/log/chatbot

# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
```

#### Bước 4: Cấu Hình Nginx

```bash
sudo nano /etc/nginx/sites-available/chatbot
```

```nginx
# Backend API
server {
    listen 80;
    server_name api.huce-chatbot.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Frontend
server {
    listen 80;
    server_name chatbot.huce-chatbot.com;
    
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
# Bật site
sudo ln -s /etc/nginx/sites-available/chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### Bước 5: SSL với Let's Encrypt

```bash
# Cài đặt certbot
sudo apt install certbot python3-certbot-nginx

# Lấy certificates
sudo certbot --nginx -d api.huce-chatbot.com -d chatbot.huce-chatbot.com

# Auto-renewal được cấu hình tự động
```

---

## 🐳 Triển Khai Docker

### Dockerfile (Backend)

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Cài đặt system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Tạo non-root user
RUN useradd -m -u 1000 chatbot && chown -R chatbot:chatbot /app
USER chatbot

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
    CMD python -c "import requests; requests.get('http://localhost:8000/')"

# Chạy application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=INFO
      - INTENT_THRESHOLD=0.35
      - CORS_ORIGINS=http://frontend:3000
    volumes:
      - ./data:/app/data:ro
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 3s
      retries: 3
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - BACKEND_URL=http://backend:8000
    depends_on:
      - backend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend
    restart: unless-stopped
```

### Deploy với Docker

```bash
# Build và start
docker-compose up -d

# Xem logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild sau khi thay đổi
docker-compose up -d --build
```

---

## ⚙️ Cấu Hình Environment

### Environment Variables

```bash
# .env file

# Cài Đặt NLP
INTENT_THRESHOLD=0.35
CONTEXT_HISTORY_LIMIT=10

# Cài Đặt Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=http://localhost:3000,https://chatbot.huce-chatbot.com
CORS_ALLOW_CREDENTIALS=true

# Data Paths
DATA_DIR=./data
LOGS_DIR=./logs

# Hiệu Năng
WORKERS=4
TIMEOUT=30
```

### Cài Đặt Production

```bash
# .env.production

# Bảo mật
LOG_LEVEL=WARNING
DEBUG=false

# Hiệu năng
WORKERS=8
TIMEOUT=60
KEEPALIVE=65

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
```

---

## 📊 Monitoring

### Logging

**Vị trí logs:**

```bash
# Application logs
logs/chatbot.log

# Supervisor logs
/var/log/chatbot/backend.log
/var/log/chatbot/frontend.log

# Nginx logs
/var/log/nginx/access.log
/var/log/nginx/error.log
```

### Health Checks

```bash
# Kiểm tra backend
curl http://localhost:8000/

# Kiểm tra processes
supervisorctl status

# Xem logs
tail -f logs/chatbot.log
```

---

## 🔧 Troubleshooting

### Vấn Đề Thường Gặp

#### 1. Port Đã Được Sử Dụng

```bash
# Tìm process đang dùng port
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>
```

#### 2. Permission Denied

```bash
# Sửa file permissions
sudo chown -R chatbot:chatbot /home/chatbot/huce-chatbot
chmod +x /home/chatbot/huce-chatbot
```

#### 3. Module Not Found

```bash
# Cài lại dependencies
cd /home/chatbot/huce-chatbot
source .venv/bin/activate
uv sync
```

#### 4. Memory Cao

```bash
# Kiểm tra memory
free -h

# Restart services
sudo supervisorctl restart all

# Thêm swap nếu cần
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 5. Response Chậm

**Kiểm tra:**

1. Server resources: `htop`
2. Network latency: `ping api.huce-chatbot.com`
3. Application logs: `tail -f logs/chatbot.log`

**Giải pháp:**

- Tăng workers: `WORKERS=8`
- Bật caching
- Tối ưu data queries
- Scale horizontally

---

## 🔐 Security Checklist

### Pre-deployment

- [ ] Cập nhật tất cả dependencies
- [ ] Xóa debug settings
- [ ] Cấu hình CORS đúng
- [ ] Set secure environment variables
- [ ] Bật HTTPS
- [ ] Cấu hình firewall
- [ ] Setup log rotation
- [ ] Cấu hình backup strategy

### Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

---

## 📋 Deployment Checklist

### Pre-deployment

- [ ] Tất cả tests pass (132/132)
- [ ] Code đã review
- [ ] Documentation updated
- [ ] Environment configured
- [ ] SSL certificates obtained
- [ ] Backup strategy in place

### Deployment

- [ ] Deploy to staging
- [ ] Chạy smoke tests
- [ ] Deploy to production
- [ ] Verify health checks
- [ ] Monitor logs (1 giờ đầu)
- [ ] Test tất cả endpoints

### Post-deployment

- [ ] Verify functionality
- [ ] Kiểm tra response times
- [ ] Monitor error rates
- [ ] Notify stakeholders

---

## 🧹 Chuẩn Bị Trước Deploy

1. **Cập nhật dependencies sản xuất**
   ```bash
   uv sync --no-dev
   ```
2. **Kiểm tra chất lượng mã nguồn**
   ```bash
   # Lint + lỗi runtime phổ biến
   ruff check

   # Kiểm tra kiểu tĩnh
   mypy .

   # Test tự động
   pytest -q
   ```
3. **Smoke backend**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --log-level info
   curl http://localhost:8000/
   curl -X POST http://localhost:8000/chat/advanced -H "Content-Type: application/json" -d '{"message":"Điểm chuẩn CNTT?","session_id":"deploy_test"}'
   ```
4. **Smoke frontend**
   ```bash
   cd frontend
   reflex run --env prod
   ```
   Gửi ít nhất 3 câu hỏi thuộc các chủ đề khác nhau để xác nhận context reset hoạt động.
5. **Kiểm tra logs**
    - `logs/chatbot.log` dùng UTF-8 (đã cấu hình trong `main.py`).
    - Đảm bảo không có traceback mới và dung lượng < 5MB trước khi đóng gói.

---

## 🔄 Quy Trình Rollback

```bash
# 1. Stop phiên bản hiện tại
sudo supervisorctl stop all

# 2. Checkout phiên bản trước
cd /home/chatbot/huce-chatbot
git checkout <previous-tag>

# 3. Cài lại dependencies (nếu cần)
source .venv/bin/activate
uv sync

# 4. Restart services
sudo supervisorctl start all

# 5. Verify
curl http://localhost:8000/
```

---

## 📞 Hỗ Trợ

### Liên Hệ

- **Vấn đề kỹ thuật:** tech@huce-chatbot.com
- **Vấn đề deployment:** ops@huce-chatbot.com
- **Khẩn cấp:** +84-xxx-xxx-xxx

### Tài Nguyên

- **Documentation:** Thư mục /docs
- **Monitoring:** http://monitoring.huce-chatbot.com
- **Logs:** http://logs.huce-chatbot.com

---

**Cập nhật lần cuối:** 2025-11-25  
**Phiên bản:** 1.0.0
