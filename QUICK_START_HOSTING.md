# 🚀 QUICK START - DEPLOY NGAY

## ⚡ 3 BƯỚC DEPLOY LÊN RENDER.COM (10 PHÚT)

### Bước 1: Push lên GitHub (2 phút)

```bash
# Nếu chưa có repo
git init
git add .
git commit -m "Ready for hosting"

# Tạo repo trên GitHub: https://github.com/new
# Đặt tên: huce-chatbot

# Push
git remote add origin https://github.com/YOUR_USERNAME/huce-chatbot.git
git branch -M main
git push -u origin main
```

---

### Bước 2: Vào Render.com (2 phút)

1. **Truy cập:** https://render.com
2. **Sign up** với GitHub
3. **Authorize** Render

---

### Bước 3: Deploy (5 phút)

1. Click **"New +"** → **"Blueprint"**
2. Connect repository: **huce-chatbot**
3. Render detect file `render.yaml`
4. Click **"Apply"**
5. Đợi deploy xong (~5 phút)

**✅ XONG!**

URLs của bạn:
- Frontend: `https://huce-chatbot-frontend.onrender.com`
- Backend: `https://huce-chatbot-backend.onrender.com`

---

## 🔧 SỬA CORS (NẾU LỖI)

Nếu frontend không connect backend:

1. Vào Backend service trong Render
2. **Environment** tab
3. Add variable:
   ```
   Key: CORS_ORIGINS
   Value: https://huce-chatbot-frontend.onrender.com
   ```
4. Save → Service tự restart

---

## 🧪 TEST

Mở: `https://huce-chatbot-frontend.onrender.com`

Test chat:
- "Xin chào"
- "Điểm chuẩn ngành Công nghệ thông tin"
- "Học phí là bao nhiêu?"

---

## ⚠️ LƯU Ý

**Free tier Render:**
- Sleep sau 15 phút không hoạt động
- Lần đầu truy cập sẽ mất ~30 giây (cold start)
- **OK cho demo và bảo vệ đồ án**

**Để không sleep:**
- Nâng cấp paid ($7/tháng)
- Hoặc dùng Fly.io (free, không sleep)

---

## 🎯 NẾU DÙNG FLY.IO

```powershell
# Cài Fly CLI
iwr https://fly.io/install.ps1 -useb | iex

# Restart terminal

# Login
fly auth login

# Deploy backend
fly launch --config fly.backend.toml --name huce-chatbot-backend
fly deploy --config fly.backend.toml -a huce-chatbot-backend

# Deploy frontend
fly launch --config fly.frontend.toml --name huce-chatbot-frontend
fly deploy --config fly.frontend.toml -a huce-chatbot-frontend

# Mở app
fly open -a huce-chatbot-frontend
```

---

## 📞 CẦN TRỢ GIÚP?

**Xem hướng dẫn chi tiết:**
- `HUONG_DAN_HOSTING.md` - Hướng dẫn đầy đủ
- `HOSTING_OPTIONS.md` - So sánh các platform

**Lỗi thường gặp:**
1. Frontend không connect backend → Check CORS_ORIGINS
2. Build timeout → Internet chậm, thử lại
3. Health check failed → Check Dockerfile

---

**Chúc bạn deploy thành công!** 🎉

