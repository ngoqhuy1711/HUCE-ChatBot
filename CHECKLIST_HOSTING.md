# ✅ CHECKLIST TRƯỚC KHI HOSTING

## 📋 Kiểm tra trước khi deploy:

### ✅ 1. Code đã clean
- [x] Đã xóa files test
- [x] Đã xóa docs thừa
- [x] Code đã tối ưu
- [x] Không có errors

### ✅ 2. Docker đã test local
```bash
# Test local trước khi deploy
docker-compose up
# Mở http://localhost:3000
# Test chat
```

### ✅ 3. Files cần thiết đã có
- [x] `Dockerfile` - Backend Docker image
- [x] `Dockerfile.frontend` - Frontend Docker image
- [x] `docker-compose.yml` - Local testing
- [x] `render.yaml` - Render.com config
- [x] `fly.backend.toml` - Fly.io backend
- [x] `fly.frontend.toml` - Fly.io frontend
- [x] `.dockerignore` - Tối ưu build
- [x] `requirements.txt` - Python deps

### ✅ 4. Environment variables chuẩn bị
```env
# Backend
INTENT_THRESHOLD=0.25
CONTEXT_HISTORY_LIMIT=10
LOG_LEVEL=INFO
DEBUG=false
CORS_ORIGINS=https://your-frontend-url.com

# Frontend
BACKEND_URL=https://your-backend-url.com
```

### ✅ 5. Git repository sẵn sàng
```bash
git status  # Check changes
git add .
git commit -m "Ready for deployment"
git push
```

---

## 🚀 SẴN SÀNG DEPLOY!

### Chọn platform:

#### 🌟 RENDER.COM (Khuyến nghị - Dễ nhất)
- ✅ FREE
- ✅ 10 phút setup
- ✅ Tự động từ GitHub
- ⚠️ Sleep sau 15 phút (free tier)

**Làm theo:** `QUICK_START_HOSTING.md`

---

#### 💎 FLY.IO (Tốt hơn - Không sleep)
- ✅ FREE
- ✅ 15 phút setup
- ✅ Không sleep
- ✅ Performance tốt hơn

**Làm theo:** `HUONG_DAN_HOSTING.md` → Phần Fly.io

---

## 📝 SAU KHI DEPLOY

### 1. Test Frontend
```
https://your-app-frontend.onrender.com
hoặc
https://your-app-frontend.fly.dev
```

### 2. Test Backend API
```
https://your-app-backend.onrender.com/health
hoặc
https://your-app-backend.fly.dev/health
```

### 3. Test Chat
- Mở frontend
- Gửi: "Xin chào"
- Gửi: "Điểm chuẩn ngành CNTT"
- Gửi: "Học phí"

### 4. Check Logs (nếu lỗi)
**Render:** Dashboard → Logs
**Fly.io:** `fly logs -a app-name`

---

## 🎯 URLs CẦN LƯU

Sau khi deploy, lưu lại:

```
Frontend: https://___________________________
Backend:  https://___________________________
GitHub:   https://github.com/_______________
```

---

## 🔧 XỬ LÝ LỖI THƯỜNG GẶP

### Lỗi 1: Frontend không connect Backend
**Nguyên nhân:** CORS chưa config
**Sửa:** Thêm `CORS_ORIGINS` vào backend env

### Lỗi 2: Backend health check failed
**Nguyên nhân:** Port không đúng
**Sửa:** Check Dockerfile expose đúng port 8000

### Lỗi 3: Build timeout
**Nguyên nhân:** Internet chậm
**Sửa:** Thử lại, hoặc tối ưu dependencies

### Lỗi 4: Frontend WebSocket không connect
**Nguyên nhân:** Port 8001 chưa expose
**Sửa:** Check docker-compose.yml đã expose 8001

---

## 📊 TIMELINE DỰ KIẾN

| Bước | Thời gian | Ghi chú |
|------|-----------|---------|
| Push GitHub | 2 phút | Nếu đã có repo |
| Đăng ký platform | 2 phút | Render hoặc Fly |
| Deploy backend | 5 phút | Build + deploy |
| Deploy frontend | 5 phút | Build + deploy |
| Config CORS | 1 phút | Nếu cần |
| Test | 2 phút | Verify hoạt động |
| **TỔNG** | **~15 phút** | Render hoặc Fly |

---

## ✅ SAU KHI HOSTING THÀNH CÔNG

### Để trình bày:
1. ✅ URL hoạt động: `https://your-app.com`
2. ✅ Screenshot giao diện
3. ✅ Video demo chat
4. ✅ Docs deployment (file này)

### Để bảo vệ đồ án:
- ✅ Giải thích kiến trúc (3-tier: Frontend, Backend, Data)
- ✅ Demo live trên hosting
- ✅ Explain deploy process
- ✅ Show Docker containers

---

**🎉 CHÚC BẠN DEPLOY THÀNH CÔNG!**

