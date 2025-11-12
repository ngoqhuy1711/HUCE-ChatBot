"""
Chatbot Main App
================

File chính (entry point) của Reflex app.

Chạy app:
    cd frontend
    reflex run

App sẽ chạy tại: http://localhost:3000
"""

import reflex as rx
from chatbot.components import chat_interface
from chatbot.state import ChatState


# ============================================================================
# GLOBAL STYLES
# ============================================================================

# CSS reset để fix layout full screen
global_style = {
    "body": {
        "margin": "0",
        "padding": "0",
        "overflow": "hidden",
        "font-family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
    },
    "#root": {
        "width": "100vw",
        "height": "100vh",
        "overflow": "hidden",
    },
}


# ============================================================================
# APP CONFIGURATION
# ============================================================================

# Metadata cho app
app_name = "Chatbot Tuyển sinh HUCE"
app_description = "Chatbot tư vấn tuyển sinh Đại học Xây dựng Hà Nội"


# ============================================================================
# PAGES - Định nghĩa các trang
# ============================================================================

def index() -> rx.Component:
    """
    Trang chính (home page).
    
    Returns:
        rx.Component - Chat interface
    """
    return chat_interface()


# ============================================================================
# APP INITIALIZATION
# ============================================================================

# Tạo Reflex app với global styles
app = rx.App(
    style=global_style,
)

# Add pages
app.add_page(
    index,
    route="/",  # Root route
    title=app_name,
    description=app_description,
    
    # Lifecycle
    on_load=ChatState.on_load,  # Gọi khi page load
)


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Note: Không nên chạy trực tiếp file này
    # Dùng: reflex run
    pass
