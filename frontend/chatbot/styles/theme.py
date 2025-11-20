"""
Theme & Styling Constants
==========================

File này định nghĩa tất cả màu sắc, font, spacing, shadows để giữ UI nhất quán.

Sử dụng:
    from chatbot.styles.theme import COLORS, SPACING, SPACING_REM, SHADOWS
    
    # SPACING: Dùng cho HStack/VStack spacing (string '0'-'9')
    rx.hstack(..., spacing=SPACING["md"])
    
    # SPACING_REM: Dùng cho padding, margin, gap (rem units)
    rx.box(
        background=COLORS["primary"],
        padding=SPACING_REM["md"],
        box_shadow=SHADOWS["md"]
    )
"""

# ============================================================================
# COLORS - Bảng màu chính (Light & Dark Mode)
# ============================================================================
# HUCE Colors
HUCE_PRIMARY = "#0052CC"
HUCE_SECONDARY = "#2563EB"

# ============================================================================
# COLORS - Modern Vibrant Palette (Light & Dark Mode)
# ============================================================================
# HUCE Colors - Enhanced
HUCE_PRIMARY = "#0052CC"
HUCE_SECONDARY = "#2563EB"
HUCE_ACCENT = "#3b82f6"

# Light Mode Colors - Fresh & Vibrant
LIGHT_COLORS = {
    # Primary colors
    "primary": HUCE_PRIMARY,
    "secondary": HUCE_SECONDARY,
    "accent": HUCE_ACCENT,

    # Background colors - Clean & Bright
    "bg_app": "#f8fafc",
    "bg_sidebar": "#ffffff",
    "bg_header": "rgba(255, 255, 255, 0.98)",
    "bg_chat": "#f8fafc",
    "bg_input_container": "rgba(255, 255, 255, 0.98)",
    "bg_input": "#ffffff",
    "bg_input_focus": "#ffffff",
    "bg_user_msg": "linear-gradient(135deg, #0052CC 0%, #1e40af 50%, #3b82f6 100%)",
    "bg_bot_msg": "linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)",
    "bg_feature_card": "#ffffff",
    "bg_suggestion": "#ffffff",
    
    # Text colors - High Contrast
    "text_primary": "#0f172a",
    "text_secondary": "#64748b",
    "text_sidebar": "#1e293b",
    "text_user_msg": "#ffffff",
    "text_bot_msg": "#1e293b",
    "text_input": "#1e293b",
    "text_placeholder": "#94a3b8",

    # Border colors - Subtle with Accent
    "border_header": "rgba(226, 232, 240, 0.8)",
    "border_input": "#cbd5e1",
    "border_input_focus": HUCE_PRIMARY,
    "border_bot_msg": "rgba(0, 82, 204, 0.15)",
    "border_feature_card": "rgba(0, 82, 204, 0.1)",
    "border_suggestion": "#e2e8f0",

    # Icon colors
    "icon_sidebar": "#475569",
}

# Dark Mode Colors - Rich & Comfortable
DARK_COLORS = {
    # Primary colors (brighter for contrast)
    "primary": "#3b82f6",
    "secondary": "#60a5fa",
    "accent": "#93c5fd",

    # Background colors - Deep & Rich
    "bg_app": "#0a0f1e",
    "bg_sidebar": "#0f172a",
    "bg_header": "rgba(15, 23, 42, 0.98)",
    "bg_chat": "#0a0f1e",
    "bg_input_container": "rgba(15, 23, 42, 0.98)",
    "bg_input": "#1e293b",
    "bg_input_focus": "#1e293b",
    "bg_user_msg": "linear-gradient(135deg, #1e40af 0%, #2563eb 50%, #3b82f6 100%)",
    "bg_bot_msg": "linear-gradient(145deg, #1f2937 0%, #1a202e 100%)",
    "bg_feature_card": "#1e293b",
    "bg_suggestion": "#1e293b",

    # Text colors - Soft & Readable
    "text_primary": "#f1f5f9",
    "text_secondary": "#cbd5e1",  # Sáng hơn từ #94a3b8 - dễ nhìn hơn
    "text_sidebar": "#e2e8f0",
    "text_user_msg": "#ffffff",
    "text_bot_msg": "#e5e7eb",
    "text_input": "#f1f5f9",
    "text_placeholder": "#94a3b8",  # Sáng hơn từ #64748b - rõ ràng hơn

    # Border colors - Visible with Glow
    "border_header": "rgba(30, 41, 59, 0.8)",
    "border_input": "#334155",
    "border_input_focus": "#3b82f6",
    "border_bot_msg": "rgba(59, 130, 246, 0.2)",
    "border_feature_card": "rgba(59, 130, 246, 0.15)",
    "border_suggestion": "#334155",

    # Icon colors
    "icon_sidebar": "#94a3b8",
}

# Legacy COLORS (deprecated - keep for compatibility)
COLORS = LIGHT_COLORS

# ============================================================================
# SPACING - Khoảng cách chuẩn
# ============================================================================
# Sử dụng hệ thống 4px base (giống Tailwind)
# 
# NOTE: Reflex components (HStack, VStack) chỉ nhận spacing là string '0'-'9'
# không nhận rem units. Dùng SPACING_REM cho các prop khác (padding, margin...)

SPACING = {
    "xs": "1",    # Nhỏ
    "sm": "2",    # Small
    "md": "4",    # Medium (mặc định)
    "lg": "6",    # Large
    "xl": "8",    # Extra large
    "2xl": "9",   # 2X Large
}

# Spacing với đơn vị rem (cho padding, margin, gap...)
SPACING_REM = {
    "xs": "0.25rem",   # 4px
    "sm": "0.5rem",    # 8px
    "md": "1rem",      # 16px
    "lg": "1.5rem",    # 24px
    "xl": "2rem",      # 32px
    "2xl": "3rem",     # 48px
}

# ============================================================================
# FONT SIZES - Kích thước chữ
# ============================================================================

FONT_SIZES = {
    "xs": "0.75rem",   # 12px
    "sm": "0.875rem",  # 14px
    "md": "1rem",      # 16px
    "lg": "1.125rem",  # 18px
    "xl": "1.25rem",   # 20px
    "2xl": "1.5rem",   # 24px
    "3xl": "1.875rem", # 30px
}

# ============================================================================
# BORDER RADIUS - Bo góc
# ============================================================================

RADIUS = {
    "sm": "0.25rem",   # 4px
    "md": "0.5rem",    # 8px
    "lg": "0.75rem",   # 12px
    "xl": "1rem",      # 16px
    "full": "9999px",  # Tròn hoàn toàn
}

# ============================================================================
# SHADOWS - Đổ bóng
# ============================================================================

SHADOWS = {
    "sm": "0 1px 2px rgb(0 0 0 / 0.04)",
    "md": "0 2px 6px rgb(0 0 0 / 0.06)",
    "lg": "0 8px 20px rgb(0 0 0 / 0.08)",
    "xl": "0 12px 28px rgb(0 0 0 / 0.10)",
}

# ============================================================================
# BREAKPOINTS - Responsive design
# ============================================================================
# Điểm chuyển đổi cho mobile, tablet, desktop

BREAKPOINTS = {
    "mobile": "640px",   # sm
    "tablet": "768px",   # md
    "desktop": "1024px", # lg
}

# ============================================================================
# TRANSITIONS - Animation timing
# ============================================================================

TRANSITIONS = {
    "fast": "150ms ease-in-out",
    "normal": "300ms ease-in-out",
    "slow": "500ms ease-in-out",
}

# ============================================================================
# DIMENSIONS - Kích thước cố định
# ============================================================================

DIMENSIONS = {
    # Chat container
    "chat_max_width": "1200px",
    "chat_height": "600px",
    
    # Sidebar/Header
    "header_height": "64px",
    
    # Input box
    "input_min_height": "48px",
    "input_max_height": "120px",
    
    # Message bubble
    "bubble_max_width": "70%",
}

# ============================================================================
# Z-INDEX - Thứ tự chồng lớp
# ============================================================================

Z_INDEX = {
    "base": 0,
    "dropdown": 10,
    "sticky": 20,
    "modal_backdrop": 30,
    "modal": 40,
    "popover": 50,
    "tooltip": 60,
}

