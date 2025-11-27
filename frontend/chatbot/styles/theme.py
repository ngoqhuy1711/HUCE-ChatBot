"""Theme & Styling Constants - Blue Theme."""

# Primary palette
PRIMARY_BLUE = "#2563eb"
PRIMARY_LIGHT = "#3b82f6"
PRIMARY_DARK = "#1d4ed8"

# Secondary accents
ACCENT_INDIGO = "#6366f1"
ACCENT_VIOLET = "#8b5cf6"
ACCENT_SKY = "#0ea5e9"

# Highlight colors
HIGHLIGHT_GREEN = "#22c55e"
HIGHLIGHT_AMBER = "#f59e0b"
HIGHLIGHT_ROSE = "#f43f5e"

# Light mode
LIGHT_COLORS = {
    "primary": PRIMARY_BLUE, "secondary": ACCENT_INDIGO, "accent": ACCENT_SKY,
    "bg_app": "linear-gradient(135deg, #eff6ff 0%, #f0f9ff 50%, #f8fafc 100%)",
    "bg_sidebar": "linear-gradient(180deg, #1e3a5f 0%, #1e293b 100%)",
    "bg_header": "rgba(255, 255, 255, 0.95)", "bg_chat": "rgba(255, 255, 255, 0.92)",
    "bg_input_container": "rgba(255, 255, 255, 0.95)", "bg_input": "#f8fafc", "bg_input_focus": "#ffffff",
    "bg_user_msg": f"linear-gradient(135deg, {PRIMARY_BLUE} 0%, {PRIMARY_LIGHT} 100%)",
    "bg_bot_msg": "#ffffff", "bg_feature_card": "rgba(255, 255, 255, 0.9)",
    "bg_suggestion": "linear-gradient(135deg, #eff6ff 0%, #f0f9ff 100%)",
    "text_primary": "#0f172a", "text_secondary": "#64748b", "text_sidebar": "#f1f5f9",
    "text_user_msg": "#ffffff", "text_bot_msg": "#1e293b", "text_input": "#1e293b", "text_placeholder": "#94a3b8",
    "border_header": "rgba(15, 23, 42, 0.08)", "border_input": "rgba(37, 99, 235, 0.2)",
    "border_input_focus": PRIMARY_BLUE, "border_bot_msg": "rgba(37, 99, 235, 0.15)",
    "border_feature_card": "rgba(15, 23, 42, 0.08)", "border_suggestion": "rgba(37, 99, 235, 0.2)",
    "glass_bg": "rgba(255, 255, 255, 0.85)", "glass_border": "rgba(255, 255, 255, 0.5)",
    "glow_primary": "0 25px 60px rgba(37, 99, 235, 0.12)",
    "icon_sidebar": "#94a3b8", "icon_active": PRIMARY_LIGHT,
}

# Dark mode
DARK_COLORS = {
    "primary": PRIMARY_LIGHT, "secondary": ACCENT_INDIGO, "accent": ACCENT_SKY,
    "bg_app": "radial-gradient(ellipse at 20% 0%, #1e3a5f 0%, #0f172a 40%, #020617 100%)",
    "bg_sidebar": "linear-gradient(180deg, rgba(2, 6, 23, 0.98) 0%, rgba(15, 23, 42, 0.95) 100%)",
    "bg_header": "rgba(15, 23, 42, 0.9)", "bg_chat": "rgba(15, 23, 42, 0.8)",
    "bg_input_container": "rgba(15, 23, 42, 0.85)", "bg_input": "rgba(30, 41, 59, 0.8)",
    "bg_input_focus": "rgba(30, 41, 59, 0.95)",
    "bg_user_msg": f"linear-gradient(135deg, {PRIMARY_BLUE} 0%, {PRIMARY_LIGHT} 100%)",
    "bg_bot_msg": "linear-gradient(145deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.9) 100%)",
    "bg_feature_card": "rgba(30, 41, 59, 0.8)", "bg_suggestion": "rgba(30, 41, 59, 0.7)",
    "text_primary": "#f1f5f9", "text_secondary": "#94a3b8", "text_sidebar": "#e2e8f0",
    "text_user_msg": "#ffffff", "text_bot_msg": "#e2e8f0", "text_input": "#f1f5f9", "text_placeholder": "#64748b",
    "border_header": "rgba(59, 130, 246, 0.2)", "border_input": "rgba(59, 130, 246, 0.25)",
    "border_input_focus": PRIMARY_LIGHT, "border_bot_msg": "rgba(59, 130, 246, 0.25)",
    "border_feature_card": "rgba(59, 130, 246, 0.2)", "border_suggestion": "rgba(59, 130, 246, 0.25)",
    "glass_bg": "rgba(15, 23, 42, 0.85)", "glass_border": "rgba(59, 130, 246, 0.2)",
    "glow_primary": "0 30px 70px rgba(59, 130, 246, 0.15)",
    "icon_sidebar": "#93c5fd", "icon_active": "#60a5fa",
}

COLORS = LIGHT_COLORS

# Gradients
GRADIENTS = {
    "primary": f"linear-gradient(135deg, {PRIMARY_BLUE} 0%, {PRIMARY_LIGHT} 100%)",
    "secondary": f"linear-gradient(135deg, {ACCENT_INDIGO} 0%, {ACCENT_VIOLET} 100%)",
    "sidebar": "linear-gradient(180deg, #1e3a5f 0%, #1e293b 100%)",
}

# Spacing
SPACING = {"xs": "1", "sm": "2", "md": "4", "lg": "6", "xl": "8", "2xl": "9"}
SPACING_REM = {"xs": "0.25rem", "sm": "0.5rem", "md": "1rem", "lg": "1.5rem", "xl": "2rem", "2xl": "3rem"}

# Font sizes
FONT_SIZES = {"xs": "0.75rem", "sm": "0.875rem", "md": "1rem", "lg": "1.125rem", "xl": "1.25rem", "2xl": "1.5rem",
              "3xl": "1.875rem"}

# Border radius
RADIUS = {"sm": "0.375rem", "md": "0.5rem", "lg": "0.75rem", "xl": "1rem", "2xl": "1.25rem", "3xl": "1.5rem",
          "full": "9999px"}

# Shadows
SHADOWS = {
    "sm": "0 1px 2px rgba(0, 0, 0, 0.05)", "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
    "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1)", "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1)",
    "2xl": "0 25px 50px -12px rgba(0, 0, 0, 0.25)", "glow_blue": "0 20px 40px rgba(37, 99, 235, 0.25)",
}

# Breakpoints
BREAKPOINTS = {"mobile": "640px", "tablet": "768px", "desktop": "1024px", "wide": "1280px"}

# Transitions
TRANSITIONS = {"fast": "150ms ease-out", "normal": "250ms ease-out", "slow": "400ms ease-out",
               "bounce": "400ms cubic-bezier(0.34, 1.56, 0.64, 1)"}

# Dimensions
DIMENSIONS = {
    "chat_max_width": "1400px", "chat_height": "600px", "header_height": "64px",
    "sidebar_width": "280px", "history_width": "260px", "input_min_height": "52px",
    "input_max_height": "120px", "bubble_max_width": "75%",
}

# Z-index
Z_INDEX = {"base": 0, "dropdown": 10, "sticky": 20, "modal_backdrop": 30, "modal": 40, "popover": 50, "tooltip": 60}
