"""
Chat Interface - HUCE Style with Dark/Light Mode
=================================================

Giao diện theo phong cách Đại học Xây dựng Hà Nội với hỗ trợ dark/light mode.
"""

import reflex as rx
from chatbot.styles.theme import (
    LIGHT_COLORS, DARK_COLORS, SPACING, SPACING_REM, RADIUS, FONT_SIZES, SHADOWS,
    HUCE_PRIMARY, HUCE_SECONDARY
)
from chatbot.state import ChatState
from chatbot.components.message_bubble import message_bubble
from chatbot.components.input_box import input_box
from chatbot.components.suggested_questions import suggested_questions


def get_colors(is_dark: bool = False):
    """Helper function để get colors dựa trên theme."""
    return rx.cond(
        ChatState.theme_mode == "dark",
        DARK_COLORS,
        LIGHT_COLORS,
    )


def sidebar() -> rx.Component:
    """Sidebar bên trái - tối giản, phẳng."""
    return rx.box(
        rx.vstack(
            # Logo + Title tối giản
            rx.vstack(
                rx.text(
                    "HUCE",
                    font_size="1.4rem",
                    font_weight="700",
                    color=rx.cond(
                        ChatState.theme_mode == "dark",
                        DARK_COLORS["text_primary"],
                        LIGHT_COLORS["text_primary"],
                    ),
                    text_align="center",
                ),
                rx.text(
                    "Chatbot tư vấn tuyển sinh",
                    font_size="0.85rem",
                    color=rx.cond(
                        ChatState.theme_mode == "dark",
                        DARK_COLORS["text_secondary"],
                        LIGHT_COLORS["text_secondary"],
                    ),
                    text_align="center",
                ),
                spacing=SPACING["sm"],
                align_items="center",
                padding_bottom=SPACING_REM["xl"],
            ),
            
            # New conversation button tinh gọn
            rx.button(
                rx.text("Cuộc hội thoại mới", font_weight="600"),
                on_click=ChatState.reset_conversation,
                width="100%",
                padding=SPACING_REM["sm"],
                background=rx.cond(
                    ChatState.theme_mode == "dark",
                    DARK_COLORS["bg_feature_card"],
                    LIGHT_COLORS["bg_feature_card"],
                ),
                border=rx.cond(
                    ChatState.theme_mode == "dark",
                    f"1px solid {DARK_COLORS['border_feature_card']}",
                    f"1px solid {LIGHT_COLORS['border_feature_card']}",
                ),
                border_radius=RADIUS["md"],
                cursor="pointer",
                _hover={
                    "transform": "translateY(-1px)",
                },
                disabled=ChatState.is_loading,
            ),
            
            # Spacer
            rx.box(flex="1"),
            
            # Links section
            rx.vstack(
                rx.text(
                    "🔗 Liên kết hữu ích",
                    font_size="0.9rem",
                    font_weight="600",
                    color=rx.cond(
                        ChatState.theme_mode == "dark",
                        DARK_COLORS["text_secondary"],
                        LIGHT_COLORS["text_secondary"],
                    ),
                    margin_bottom=SPACING_REM["sm"],
                ),
                
                # Trang tuyển sinh
                rx.link(
                    rx.hstack(
                        rx.text(
                            "Trang tuyển sinh",
                            font_size="0.95rem",
                            color=rx.cond(
                                ChatState.theme_mode == "dark",
                                DARK_COLORS["text_primary"],
                                LIGHT_COLORS["text_primary"],
                            ),
                        ),
                        spacing=SPACING["sm"],
                    ),
                    href="https://tuyensinh.huce.edu.vn/",
                    is_external=True,
                    width="100%",
                    padding=SPACING_REM["xs"],
                    border_radius=RADIUS["sm"],
                    _hover={
                        "opacity": "0.8",
                    },
                ),
                
                # Fanpage
                rx.link(
                    rx.hstack(
                        rx.text(
                            "Fanpage",
                            font_size="0.95rem",
                            color=rx.cond(
                                ChatState.theme_mode == "dark",
                                DARK_COLORS["text_primary"],
                                LIGHT_COLORS["text_primary"],
                            ),
                        ),
                        spacing=SPACING["sm"],
                    ),
                    href="https://www.facebook.com/tsdhxdhn",
                    is_external=True,
                    width="100%",
                    padding=SPACING_REM["xs"],
                    border_radius=RADIUS["sm"],
                    _hover={
                        "opacity": "0.8",
                    },
                ),
                
                # Số điện thoại
                rx.link(
                    rx.hstack(
                        rx.text(
                            "024 2240 4010",
                            font_size="0.95rem",
                            color=rx.cond(
                                ChatState.theme_mode == "dark",
                                DARK_COLORS["text_primary"],
                                LIGHT_COLORS["text_primary"],
                            ),
                        ),
                        spacing=SPACING["sm"],
                    ),
                    href="tel:02422404010",
                    width="100%",
                    padding=SPACING_REM["xs"],
                    border_radius=RADIUS["sm"],
                    _hover={
                        "opacity": "0.8",
                    },
                ),
                
                # Email
                rx.link(
                    rx.hstack(
                        rx.text(
                            "tuyensinhdh@huce.edu.vn",
                            font_size="0.9rem",
                            color=rx.cond(
                                ChatState.theme_mode == "dark",
                                DARK_COLORS["text_primary"],
                                LIGHT_COLORS["text_primary"],
                            ),
                        ),
                        spacing=SPACING["sm"],
                    ),
                    href="mailto:tuyensinhdh@huce.edu.vn",
                    width="100%",
                    padding=SPACING_REM["xs"],
                    border_radius=RADIUS["sm"],
                    _hover={
                        "opacity": "0.8",
                    },
                ),
                
                spacing=SPACING["xs"],
                width="100%",
            ),
            
            spacing=SPACING["lg"],
            height="100%",
            padding=SPACING_REM["xl"],
        ),
        
        width="260px",
        height="100vh",
        background=rx.cond(
            ChatState.theme_mode == "dark",
            DARK_COLORS["bg_sidebar"],
            LIGHT_COLORS["bg_sidebar"],
        ),
        border_right=rx.cond(
            ChatState.theme_mode == "dark",
            f"1px solid {DARK_COLORS['border_header']}",
            f"1px solid {LIGHT_COLORS['border_header']}",
        ),
        flex_shrink="0",
    )


def header() -> rx.Component:
    """Header tối giản với title và theme toggle."""
    return rx.box(
        rx.hstack(
            # Title
            rx.vstack(
                rx.text(
                    "Trợ lý tuyển sinh HUCE",
                    font_size="1.25rem",
                    font_weight="600",
                    color=rx.cond(
                        ChatState.theme_mode == "dark",
                        DARK_COLORS["text_primary"],
                        LIGHT_COLORS["text_primary"],
                    ),
                ),
                rx.text(
                    "Hỏi về ngành, điểm, điều kiện, học phí,…",
                    font_size="0.95rem",
                    color=rx.cond(
                        ChatState.theme_mode == "dark",
                        DARK_COLORS["text_secondary"],
                        LIGHT_COLORS["text_secondary"],
                    ),
                ),
                spacing="0",
                align_items="flex-start",
            ),
            
            # Spacer
            rx.box(flex="1"),
            
            # Theme toggle button
            rx.button(
                rx.cond(
                    ChatState.theme_mode == "dark",
                    rx.icon("sun", size=18),
                    rx.icon("moon", size=18),
                ),
                on_click=ChatState.toggle_theme,
                
                width="40px",
                height="40px",
                padding="0",
                background=rx.cond(
                    ChatState.theme_mode == "dark",
                    "rgba(255,255,255,0.06)",
                    "rgba(0,0,0,0.04)",
                ),
                border_radius="10px",
                cursor="pointer",
                transition="all 0.3s",
                
                _hover={
                    "background": rx.cond(
                        ChatState.theme_mode == "dark",
                        "rgba(255,255,255,0.12)",
                        "rgba(0,0,0,0.08)",
                    ),
                },
            ),
            
            spacing=SPACING["md"],
            align_items="center",
        ),
        
        padding=f"{SPACING_REM['lg']} {SPACING_REM['xl']}",
        border_bottom=rx.cond(
            ChatState.theme_mode == "dark",
            f"1px solid {DARK_COLORS['border_header']}",
            f"1px solid {LIGHT_COLORS['border_header']}",
        ),
        background=rx.cond(
            ChatState.theme_mode == "dark",
            DARK_COLORS["bg_header"],
            LIGHT_COLORS["bg_header"],
        ),
    )


def messages_area() -> rx.Component:
    """Messages area - đơn giản, rộng rãi."""
    return rx.box(
        rx.vstack(
            # Hero hoặc Messages
            rx.cond(
                ChatState.messages.length() == 0,
                # Hero section tinh gọn
                rx.vstack(
                    # Title lớn
                    rx.text(
                        "Chào mừng đến với Trợ lý tuyển sinh HUCE",
                        font_size="1.6rem",
                        font_weight="600",
                        color=rx.cond(
                            ChatState.theme_mode == "dark",
                            DARK_COLORS["text_primary"],
                            LIGHT_COLORS["text_primary"],
                        ),
                        text_align="center",
                        line_height="1.3",
                        max_width="720px",
                    ),
                    
                    # Subtitle
                    rx.text(
                        "Hỏi về ngành học, tổ hợp, điểm chuẩn, lịch tuyển sinh, học phí và học bổng.",
                        font_size="1rem",
                        color=rx.cond(
                            ChatState.theme_mode == "dark",
                            DARK_COLORS["text_secondary"],
                            LIGHT_COLORS["text_secondary"],
                        ),
                        text_align="center",
                        line_height="1.6",
                        max_width="640px",
                    ),
                    
                    spacing=SPACING["lg"],
                    align_items="center",
                    padding=SPACING_REM["2xl"],
                ),
                
                # Messages list
                rx.vstack(
                    rx.foreach(
                        ChatState.messages,
                        message_bubble,
                    ),
                    # Loading
                    rx.cond(
                        ChatState.is_loading,
                        rx.hstack(
                            rx.spinner(
                                size="3",
                                color=rx.cond(
                                    ChatState.theme_mode == "dark",
                                    DARK_COLORS["primary"],
                                    LIGHT_COLORS["primary"],
                                ),
                            ),
                            rx.text(
                                "Đang xử lý...",
                                font_size=FONT_SIZES["sm"],
                                color=rx.cond(
                                    ChatState.theme_mode == "dark",
                                    DARK_COLORS["text_secondary"],
                                    LIGHT_COLORS["text_secondary"],
                                ),
                                font_style="italic",
                            ),
                            spacing=SPACING["sm"],
                            padding=SPACING_REM["lg"],
                        ),
                        rx.box(),
                    ),
                    spacing="0",
                    width="100%",
                    max_width="900px",
                    padding=SPACING_REM["xl"],
                ),
            ),
            
            # Suggested questions - LUÔN HIỂN THỊ
            suggested_questions(),
            
            spacing="0",
            width="100%",
            max_width="900px",
            margin="0 auto",
        ),
        
        flex="1",
        width="100%",
        overflow_y="auto",
        background=rx.cond(
            ChatState.theme_mode == "dark",
            DARK_COLORS["bg_chat"],
            LIGHT_COLORS["bg_chat"],
        ),
        
        # Scrollbar tinh gọn
        style={
            "&::-webkit-scrollbar": {"width": "8px"},
            "&::-webkit-scrollbar-track": {
                "background": rx.cond(
                    ChatState.theme_mode == "dark",
                    "#1e293b",
                    "#f1f5f9",
                )
            },
            "&::-webkit-scrollbar-thumb": {
                "background": rx.cond(
                    ChatState.theme_mode == "dark",
                    "#475569",
                    HUCE_PRIMARY,
                ),
                "border-radius": "4px",
            },
        },
    )


def chat_interface() -> rx.Component:
    """Main interface - tối giản, responsive với sidebar và dark/light mode."""
    return rx.hstack(
        # Sidebar bên trái
        sidebar(),
        
        # Main content
        rx.vstack(
            header(),
            messages_area(),
            input_box(),
            
            spacing="0",
            width="100%",
            height="100vh",
            overflow="hidden",
            background=rx.cond(
                ChatState.theme_mode == "dark",
                DARK_COLORS["bg_header"],
                LIGHT_COLORS["bg_header"],
            ),
        ),
        
        spacing="0",
        width="100vw",
        height="100vh",
        overflow="hidden",
    )
