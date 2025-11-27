# 🚀 HƯỚNG DẪN HOSTING CHI TIẾT

## 🎯 PHƯƠNG ÁN ĐƠN GIẢN NHẤT: RENDER.COM (FREE)

### ✅ Bước 1: Chuẩn bị GitHub Repository

```bash
# Nếu chưa có Git repository
git init
git add .
git commit -m "Ready for deployment"

# Tạo repository trên GitHub
# Vào https://github.com/new
# Tạo repo mới: huce-chatbot

# Push code
git remote add origin https://github.com/YOUR_USERNAME/huce-chatbot.git
git branch -M main
git push -u origin main
```

---

### ✅ Bước 2: Đăng ký Render.com

1. Truy cập: **https://render.com**
2. Click **"Get Started"** hoặc **"Sign Up"**
3. Chọn **"Sign up with GitHub"**
4. Authorize Render to access your repositories

---

### ✅ Bước 3: Deploy từ Blueprint

#### Cách 1: Deploy tự động (Blueprint)

1. Trong Render Dashboard, click **"New +"**
2. Chọn **"Blueprint"**
3. Connect repository **huce-chatbot**
4. Render sẽ tự động detect file `render.yaml`
5. Click **"Apply"**
6. Đợi 5-10 phút để deploy

#### Cách 2: Deploy thủ công

**Deploy Backend:**
1. New + → Web Service
2. Connect repository
3. Name: `huce-chatbot-backend`
4. Runtime: Docker
5. Dockerfile path: `./Dockerfile`
6. Environment variables:
   - `INTENT_THRESHOLD` = `0.25`
   - `LOG_LEVEL` = `INFO`
7. Create Web Service

**Deploy Frontend:**
1. New + → Web Service
2. Name: `huce-chatbot-frontend`
3. Runtime: Docker
4. Dockerfile path: `./Dockerfile.frontend`
5. Environment variables:
   - `BACKEND_URL` = `https://huce-chatbot-backend.onrender.com`
6. Create Web Service

---

### ✅ Bước 4: Cấu hình CORS

Sau khi có URL của frontend, cập nhật backend:

1. Vào Backend service settings
2. Environment → Add Environment Variable
3. Thêm:
   ```
   CORS_ORIGINS=https://huce-chatbot-frontend.onrender.com
   ```
4. Save Changes
5. Service sẽ tự động restart

---

### ✅ Bước 5: Test

1. Mở URL frontend: `https://huce-chatbot-frontend.onrender.com`
2. Test chat với câu hỏi: "Xin chào"
3. Test một số câu hỏi khác:
   - "Điểm chuẩn ngành Công nghệ thông tin"
   - "Học phí là bao nhiêu?"
   - "Thông tin liên hệ"

---

## 🔥 PHƯƠNG ÁN NHANH HƠN: FLY.IO

### ✅ Bước 1: Cài đặt Fly CLI

**Windows (PowerShell):**
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

**Restart terminal sau khi cài**

---

### ✅ Bước 2: Login

```bash
fly auth login
```

Browser sẽ mở, login bằng GitHub.

---

### ✅ Bước 3: Deploy Backend

```bash
cd C:\Users\ngoqh\DATN

# Deploy backend
fly launch --config fly.backend.toml --name huce-chatbot-backend --no-deploy

# Set secrets (nếu cần)
fly secrets set INTENT_THRESHOLD=0.25 -a huce-chatbot-backend

# Deploy
fly deploy --config fly.backend.toml -a huce-chatbot-backend
```

---

### ✅ Bước 4: Deploy Frontend

```bash
# Cập nhật BACKEND_URL trong fly.frontend.toml
# Thay "https://huce-chatbot-backend.fly.dev" bằng URL backend thực tế

# Deploy frontend
fly launch --config fly.frontend.toml --name huce-chatbot-frontend --no-deploy

# Set backend URL
fly secrets set BACKEND_URL=https://huce-chatbot-backend.fly.dev -a huce-chatbot-frontend

# Deploy
fly deploy --config fly.frontend.toml -a huce-chatbot-frontend
```

---

### ✅ Bước 5: Mở app

```bash
fly open -a huce-chatbot-frontend
```

---

## 🐳 PHƯƠNG ÁN VPS (UBUNTU)

Nếu bạn có VPS (Contabo, Vultr, DigitalOcean):

### Bước 1: Cài đặt Docker

```bash
ssh root@YOUR_VPS_IP

# Cài Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Cài Docker Compose
apt install docker-compose -y
```

### Bước 2: Clone code

```bash
git clone https://github.com/YOUR_USERNAME/huce-chatbot.git
cd huce-chatbot
```

### Bước 3: Cấu hình

```bash
# Tạo file .env.production
cp env.example .env.production

# Edit .env.production
nano .env.production
```

### Bước 4: Deploy

```bash
docker-compose up -d
```

### Bước 5: Setup Nginx (Optional - cho domain)

```bash
apt install nginx -y

# Tạo config
nano /etc/nginx/sites-available/chatbot
```

Nội dung:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
    }

    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

```bash
ln -s /etc/nginx/sites-available/chatbot /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

---

## 📊 SO SÁNH

| Method | Difficulty | Time | Cost | Best For |
|--------|-----------|------|------|----------|
| Render.com | ⭐ Easy | 10 min | FREE | Đồ án, Demo |
| Fly.io | ⭐⭐ Medium | 15 min | FREE | Production |
| VPS | ⭐⭐⭐ Hard | 60 min | $5/mo | Full control |

---

## 🎯 KHUYẾN NGHỊ

**Cho đồ án:**
- ✅ **Render.com** (đơn giản nhất, free)
- ✅ **Fly.io** (nếu muốn không sleep)

**Cho production thực tế:**
- ✅ **Fly.io** hoặc **Google Cloud Run**
- ✅ **VPS** nếu cần full control

---

## ⚠️ LƯU Ý

### Render.com (Free tier):
- Sleep sau 15 phút không hoạt động
- Cold start ~30 giây
- Giải pháp: Dùng UptimeRobot để ping mỗi 5 phút

### Fly.io:
- Không sleep
- Free tier: 3GB RAM
- Tốt hơn cho production

---

## 🔧 TROUBLESHOOTING

### Lỗi: Frontend không kết nối Backend

**Kiểm tra:**
1. BACKEND_URL có đúng không?
2. CORS_ORIGINS đã thêm frontend URL chưa?
3. Backend có healthy không? (check /health)

**Sửa:**
```bash
# Render: Settings → Environment → Add Variable
CORS_ORIGINS=https://your-frontend.onrender.com

# Fly.io
fly secrets set CORS_ORIGINS=https://your-frontend.fly.dev -a huce-chatbot-backend
```

### Lỗi: Build timeout

**Sửa:**
- Giảm dependencies trong requirements.txt
- Tối ưu Dockerfile
- Dùng build cache

---

## 📞 HỖ TRỢ

Nếu gặp vấn đề:
1. Check logs: `fly logs -a app-name` (Fly.io)
2. Check logs trong Render Dashboard
3. Test local: `docker-compose up`

---

**Chúc bạn deploy thành công!** 🚀

