"""
Suggested Questions - HUCE Style with Dark/Light Mode
=====================================================

Suggested questions theo phong cách HUCE với hỗ trợ dark/light mode.
"""

import reflex as rx
from chatbot.styles.theme import (
    LIGHT_COLORS, DARK_COLORS, SPACING, SPACING_REM, RADIUS, FONT_SIZES
)
from chatbot.state import ChatState


# Danh sách câu hỏi gợi ý
SUGGESTIONS = [
    {
        "icon": "📚",
        "text": "Điều kiện tuyển sinh năm 2025?",
        "color": "#0052CC",
    },
    {
        "icon": "🎯",
        "text": "Điểm chuẩn các ngành?",
        "color": "#2563EB",
    },
    {
        "icon": "💰",
        "text": "Học phí và học bổng?",
        "color": "#7C3AED",
    },
    {
        "icon": "📅",
        "text": "Lịch tuyển sinh?",
        "color": "#059669",
    },
    {
        "icon": "🏗️",
        "text": "Ngành Kỹ thuật Xây dựng?",
        "color": "#DC2626",
    },
    {
        "icon": "🌉",
        "text": "Ngành Kỹ thuật Cầu đường?",
        "color": "#EA580C",
    },
]


def suggested_questions() -> rx.Component:
    """Hiển thị các câu hỏi gợi ý với dark/light mode."""
    
    return rx.vstack(
        rx.text(
            "Câu hỏi phổ biến",
            font_size="1rem",
            font_weight="600",
            color=rx.cond(
                ChatState.theme_mode == "dark",
                DARK_COLORS["text_primary"],
                LIGHT_COLORS["text_primary"],
            ),
            margin_bottom=SPACING_REM["sm"],
        ),
        
        # Grid of suggestion buttons
        rx.box(
            *[
                rx.button(
                    rx.hstack(
                        rx.text(item["icon"], font_size="1.25rem"),
                        rx.text(
                            item["text"],
                            font_size="0.95rem",
                            font_weight="500",
                            color=rx.cond(
                                ChatState.theme_mode == "dark",
                                DARK_COLORS["text_primary"],
                                LIGHT_COLORS["text_primary"],
                            ),
                        ),
                        spacing=SPACING["sm"],
                        align_items="center",
                    ),
                    
                    on_click=ChatState.use_suggested_question(item["text"]),
                    
                    width="100%",
                    padding=SPACING_REM["md"],
                    background=rx.cond(
                        ChatState.theme_mode == "dark",
                        DARK_COLORS["bg_suggestion"],
                        LIGHT_COLORS["bg_suggestion"],
                    ),
                    border=rx.cond(
                        ChatState.theme_mode == "dark",
                        f"1px solid {DARK_COLORS['border_suggestion']}",
                        f"1px solid {LIGHT_COLORS['border_suggestion']}",
                    ),
                    border_radius=RADIUS["md"],
                    cursor="pointer",
                    box_shadow="0 1px 4px rgba(0, 0, 0, 0.04)",
                    transition="transform 0.15s ease, box-shadow 0.2s ease, border-color 0.2s ease",
                    
                    _hover={
                        "border-color": item["color"],
                        "transform": "translateY(-1px)",
                        "box-shadow": "0 6px 12px rgba(0,0,0,0.08)",
                    },
                    
                    _active={
                        "transform": "translateY(0)",
                    },
                    
                    disabled=ChatState.is_loading,
                )
                for item in SUGGESTIONS
            ],
            
            display="grid",
            grid_template_columns="repeat(auto-fit, minmax(260px, 1fr))",
            gap=SPACING_REM["md"],
            width="100%",
            max_width="900px",
        ),
        
        spacing=SPACING["md"],
        width="100%",
        padding=SPACING_REM["xl"],
        align_items="center",
    )
