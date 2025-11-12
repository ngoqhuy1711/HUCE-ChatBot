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

# Light Mode Colors
LIGHT_COLORS = {
    # Primary HUCE colors
    "primary": HUCE_PRIMARY,
    "secondary": HUCE_SECONDARY,
    
    # Background colors (flat, neutral)
    "bg_app": "#f6f7fb",
    "bg_sidebar": "#ffffff",
    "bg_header": "#ffffff",
    "bg_chat": "#f6f7fb",
    "bg_input_container": "#ffffff",
    "bg_input": "#f8fafc",
    "bg_input_focus": "#ffffff",
    "bg_user_msg": "#0b63e6",  # solid primary for user bubble
    "bg_bot_msg": "#ffffff",
    "bg_feature_card": "#ffffff",
    "bg_suggestion": "#ffffff",
    
    # Text colors
    "text_primary": "#111827",
    "text_secondary": "#6b7280",
    "text_sidebar": "#111827",
    "text_user_msg": "#ffffff",
    "text_bot_msg": "#111827",
    "text_input": "#111827",
    "text_placeholder": "#9ca3af",
    
    # Border colors (subtle)
    "border_header": "#e5e7eb",
    "border_input": "#d1d5db",
    "border_input_focus": HUCE_PRIMARY,
    "border_bot_msg": "#e5e7eb",
    "border_feature_card": "#e5e7eb",
    "border_suggestion": "#e5e7eb",
    
    # Icon colors
    "icon_sidebar": "#374151",
}

# Dark Mode Colors
DARK_COLORS = {
    # Primary HUCE colors (slightly brighter for contrast)
    "primary": "#4f8df6",
    "secondary": "#7aa8ff",
    
    # Background colors (flat)
    "bg_app": "#0f172a",
    "bg_sidebar": "#0f172a",
    "bg_header": "#111827",
    "bg_chat": "#0f172a",
    "bg_input_container": "#111827",
    "bg_input": "#0b1222",
    "bg_input_focus": "#111827",
    "bg_user_msg": "#1e3a8a",  # deep solid for user bubble
    "bg_bot_msg": "#1f2937",
    "bg_feature_card": "#111827",
    "bg_suggestion": "#111827",
    
    # Text colors
    "text_primary": "#f3f4f6",
    "text_secondary": "#9ca3af",
    "text_sidebar": "#f3f4f6",
    "text_user_msg": "#ffffff",
    "text_bot_msg": "#f3f4f6",
    "text_input": "#f3f4f6",
    "text_placeholder": "#6b7280",
    
    # Border colors (subtle)
    "border_header": "#1f2937",
    "border_input": "#293241",
    "border_input_focus": "#4f8df6",
    "border_bot_msg": "#293241",
    "border_feature_card": "#1f2937",
    "border_suggestion": "#1f2937",
    
    # Icon colors
    "icon_sidebar": "#f3f4f6",
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

