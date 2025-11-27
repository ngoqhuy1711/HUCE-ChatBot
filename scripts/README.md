# Scripts Directory

Thư mục này chứa các scripts hỗ trợ deploy và vận hành hệ thống.

## 📁 Files

### `deploy.sh`

Script tự động deploy ứng dụng lên production sử dụng Docker Compose.

**Sử dụng:**

```bash
chmod +x deploy.sh
./deploy.sh
```

**Script sẽ:**

1. Kiểm tra Docker và Docker Compose đã cài đặt
2. Kiểm tra `.env.production` tồn tại
3. Stop containers cũ
4. Build Docker images mới
5. Start containers
6. Verify health của services

## 🔧 Other Useful Scripts

### Manual Deployment Commands

```bash
# Build và start services
docker-compose build --no-cache
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart specific service
docker-compose restart backend
docker-compose restart frontend
```

### Backup Commands

```bash
# Backup data
tar -czf backup_data_$(date +%Y%m%d).tar.gz ../data/

# Backup logs
tar -czf backup_logs_$(date +%Y%m%d).tar.gz ../logs/

# Restore from backup
tar -xzf backup_data_20250127.tar.gz
```

### Health Check Commands

```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000/

# Check all containers status
docker-compose ps

# Check resource usage
docker stats
```

## 📝 Notes

- Đảm bảo có quyền execute cho scripts: `chmod +x script_name.sh`
- Luôn test scripts trên môi trường development trước
- Backup data trước khi chạy deployment scripts

