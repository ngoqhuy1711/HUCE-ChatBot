"""
Suggested Questions - Modern Card Design
=========================================

Suggested questions với card style hiện đại và interactive.
"""

import reflex as rx
from chatbot.styles.theme import (
    LIGHT_COLORS, DARK_COLORS, SPACING, SPACING_REM, RADIUS, FONT_SIZES
)
from chatbot.state import ChatState


# Danh sách câu hỏi gợi ý với icons - Updated cho dữ liệu 2025
SUGGESTIONS = [
    {"text": "Phương thức xét tuyển 2025?", "icon": "graduation-cap", "color": "#0052CC"},
    {"text": "Điểm chuẩn ngành Kiến trúc?", "icon": "building", "color": "#dc2626"},
    {"text": "Học phí và học bổng?", "icon": "wallet", "color": "#7c3aed"},
    {"text": "Ngành Công nghệ thông tin?", "icon": "code", "color": "#2563eb"},
    {"text": "Ngành Xây dựng dân dụng?", "icon": "hammer", "color": "#ea580c"},
    {"text": "Lịch tuyển sinh 2025?", "icon": "calendar", "color": "#059669"},
]


def suggested_questions() -> rx.Component:
    """Hiển thị câu hỏi gợi ý với modern card design."""

    return rx.box(
        rx.vstack(
            # Title
            rx.hstack(
                rx.icon("sparkles", size=18, color=rx.cond(
                    ChatState.theme_mode == "dark",
                    "#fbbf24",
                    "#ea580c",
                )),
                rx.text(
                    "Câu hỏi gợi ý",
                    font_size="0.95rem",
                    font_weight="600",
                    color=rx.cond(
                        ChatState.theme_mode == "dark",
                        DARK_COLORS["text_primary"],
                        LIGHT_COLORS["text_primary"],
                    ),
                ),
                spacing="2",
                margin_bottom="16px",
            ),

            # Grid of suggestion cards
            rx.box(
                *[
                    rx.button(
                        rx.hstack(
                            rx.icon(
                                item["icon"],
                                size=18,
                                color=item["color"],
                            ),
                            rx.text(
                                item["text"],
                                font_size="0.9rem",
                                font_weight="500",
                                color=rx.cond(
                                    ChatState.theme_mode == "dark",
                                    DARK_COLORS["text_primary"],
                                    LIGHT_COLORS["text_primary"],
                                ),
                            ),
                            spacing="3",
                            align_items="center",
                        ),

                        on_click=ChatState.use_suggested_question(item["text"]),

                        width="100%",
                        padding="14px 18px",
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
                        border_radius="12px",
                        cursor="pointer",
                        box_shadow="0 2px 6px rgba(0, 0, 0, 0.06)",
                        transition="all 0.25s cubic-bezier(0.4, 0, 0.2, 1)",

                        _hover={
                            "border_color": item["color"],
                            "transform": "translateY(-3px) scale(1.02)",
                            "box_shadow": f"0 12px 24px rgba({int(item['color'][1:3], 16)}, {int(item['color'][3:5], 16)}, {int(item['color'][5:7], 16)}, 0.2), 0 4px 8px rgba(0,0,0,0.1)",
                            "background": rx.cond(
                                ChatState.theme_mode == "dark",
                                f"linear-gradient(135deg, rgba({int(item['color'][1:3], 16)}, {int(item['color'][3:5], 16)}, {int(item['color'][5:7], 16)}, 0.1), rgba({int(item['color'][1:3], 16)}, {int(item['color'][3:5], 16)}, {int(item['color'][5:7], 16)}, 0.05))",
                                f"linear-gradient(135deg, rgba({int(item['color'][1:3], 16)}, {int(item['color'][3:5], 16)}, {int(item['color'][5:7], 16)}, 0.08), rgba({int(item['color'][1:3], 16)}, {int(item['color'][3:5], 16)}, {int(item['color'][5:7], 16)}, 0.03))",
                            ),
                        },

                        disabled=ChatState.is_loading,
                    )
                    for item in SUGGESTIONS
                ],

                display="grid",
                grid_template_columns="repeat(auto-fit, minmax(280px, 1fr))",
                gap="12px",
                width="100%",
            ),

            spacing="2",
            width="100%",
            max_width="1000px",
            padding="24px",
            margin="0 auto",
        ),

        width="100%",
    )

