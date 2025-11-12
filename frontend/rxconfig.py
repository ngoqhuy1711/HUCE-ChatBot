"""
Reflex Configuration File
=========================

File này cấu hình các thiết lập cơ bản cho Reflex app.

Các tham số quan trọng:
- app_name: Tên app (dùng làm package name)
- port: Port chạy frontend (mặc định 3000, nhưng dùng 8080 để phù hợp với CORS backend)
- api_url: URL của FastAPI backend
- telemetry_enabled: Gửi anonymous usage data cho Reflex team (tùy chọn)
"""

import reflex as rx

# Cấu hình app
config = rx.Config(
    # Tên app - phải trùng với tên thư mục chứa code
    app_name="chatbot",
    
    # Port chạy frontend - backend đã config CORS cho port 3000
    port=3000,
    
    # Backend port cho Reflex (WebSocket server) - phải khác FastAPI backend
    backend_port=8001,
    
    # Môi trường (development/production)
    # Trong dev mode sẽ có hot reload, debug info
    env=rx.Env.DEV,
    
    # Telemetry - Gửi anonymous usage data cho Reflex
    # Set False nếu không muốn share
    telemetry_enabled=False,
    
    # Disable sitemap plugin warning
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
    
    # Backend URL - frontend sẽ gọi API này
    # Nếu deploy production, thay bằng URL thật
    backend_url="http://localhost:8000",
    
    # Timeout cho API calls (giây)
    timeout=30,
)

