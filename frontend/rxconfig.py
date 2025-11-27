"""Reflex Configuration."""

import os

import reflex as rx

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

config = rx.Config(
    app_name="chatbot",
    port=3000,
    backend_port=8001,
    # Trong dev mode sẽ có hot reload, debug info
    env=rx.Env.DEV,

    # Telemetry - Gửi anonymous usage data cho Reflex
    # Set False nếu không muốn share
    telemetry_enabled=False,

    # Disable sitemap plugin warning
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],

    # Backend URL - frontend sẽ gọi API này
    # Nếu deploy production, thay bằng URL thật
    # Trong Docker: http://backend:8000
    # Trong dev local: http://localhost:8000
    backend_url=BACKEND_URL,

    # Timeout cho API calls (giây)
    timeout=30,
)
