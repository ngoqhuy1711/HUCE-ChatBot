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
                    "Tra cứu thông tin tuyển sinh",
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
                rx.text(
                    "Cuộc hội thoại mới",
                    font_weight="600",
                    color=rx.cond(
                        ChatState.theme_mode == "dark",
                        DARK_COLORS["text_primary"],
                        LIGHT_COLORS["text_primary"],
                    ),
                ),
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
    """Header compact với title và theme toggle."""
    return rx.box(
        rx.hstack(
            # Title - compact hơn
            rx.vstack(
                rx.text(
                    "Chatbot Tuyển sinh HUCE 2025",
                    font_size="1.15rem",
                    font_weight="600",
                    color=rx.cond(
                        ChatState.theme_mode == "dark",
                        DARK_COLORS["text_primary"],
                        LIGHT_COLORS["text_primary"],
                    ),
                ),
                rx.text(
                    "Hệ thống tra cứu thông tin tuyển sinh 24/7",
                    font_size="0.875rem",
                    color=rx.cond(
                        ChatState.theme_mode == "dark",
                        DARK_COLORS["text_secondary"],
                        LIGHT_COLORS["text_secondary"],
                    ),
                ),
                spacing="1",
                align_items="flex-start",
            ),
            
            # Spacer
            rx.box(flex="1"),
            
            # Theme toggle button
            rx.button(
                rx.cond(
                    ChatState.theme_mode == "dark",
                    rx.icon("sun", size=16),
                    rx.icon("moon", size=16),
                ),
                on_click=ChatState.toggle_theme,
                
                width="36px",
                height="36px",
                padding="0",
                background=rx.cond(
                    ChatState.theme_mode == "dark",
                    "rgba(255,255,255,0.08)",
                    "rgba(0,0,0,0.05)",
                ),
                border_radius="8px",
                cursor="pointer",
                transition="all 0.2s",
                
                _hover={
                    "background": rx.cond(
                        ChatState.theme_mode == "dark",
                        "rgba(255,255,255,0.15)",
                        "rgba(0,0,0,0.10)",
                    ),
                },
            ),
            
            spacing=SPACING["md"],
            align_items="center",
        ),
        
        padding=f"{SPACING_REM['md']} {SPACING_REM['xl']}",
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
    """Messages area với hero section hiện đại."""
    return rx.box(
        rx.vstack(
            # Hero hoặc Messages
            rx.cond(
                ChatState.messages.length() == 0,
                # Hero section với gradient và animation
                rx.vstack(
                    # Icon lớn với animation
                    rx.box(
                        rx.icon(
                            "sparkles",
                            size=48,
                            color=rx.cond(
                                ChatState.theme_mode == "dark",
                                "#60a5fa",
                                HUCE_PRIMARY,
                            ),
                        ),
                        margin_bottom="24px",
                        animation="bounce 2s ease-in-out infinite",
                    ),

                    # Title với gradient text
                    rx.heading(
                        "Xin chào! Tôi có thể giúp gì cho bạn?",
                        size="8",
                        font_weight="700",
                        text_align="center",
                        line_height="1.2",
                        max_width="800px",
                        background=rx.cond(
                            ChatState.theme_mode == "dark",
                            "linear-gradient(135deg, #f1f5f9 0%, #94a3b8 100%)",
                            "linear-gradient(135deg, #0052CC 0%, #1e40af 100%)",
                        ),
                        background_clip="text",
                        style={
                            "-webkit-background-clip": "text",
                            "-webkit-text-fill-color": "transparent",
                        },
                    ),
                    
                    # Subtitle
                    rx.text(
                        "Hỏi tôi về ngành học, điểm chuẩn, học phí, học bổng, lịch tuyển sinh và nhiều hơn nữa...",
                        font_size="1.125rem",
                        color=rx.cond(
                            ChatState.theme_mode == "dark",
                            DARK_COLORS["text_secondary"],
                            LIGHT_COLORS["text_secondary"],
                        ),
                        text_align="center",
                        line_height="1.7",
                        max_width="700px",
                        margin_top="16px",
                    ),
                    
                    # Feature cards
                    rx.hstack(
                        rx.box(
                            rx.vstack(
                                rx.icon("book-open", size=24),
                                rx.text("Ngành học", font_weight="500", font_size="0.9rem"),
                                spacing="2",
                                align_items="center",
                            ),
                            padding="20px",
                            background=rx.cond(
                                ChatState.theme_mode == "dark",
                                "rgba(59, 130, 246, 0.1)",
                                "rgba(0, 82, 204, 0.05)",
                            ),
                            border_radius="16px",
                            border=rx.cond(
                                ChatState.theme_mode == "dark",
                                "1px solid rgba(59, 130, 246, 0.2)",
                                "1px solid rgba(0, 82, 204, 0.1)",
                            ),
                        ),
                        rx.box(
                            rx.vstack(
                                rx.icon("trophy", size=24),
                                rx.text("Điểm chuẩn", font_weight="500", font_size="0.9rem"),
                                spacing="2",
                                align_items="center",
                            ),
                            padding="20px",
                            background=rx.cond(
                                ChatState.theme_mode == "dark",
                                "rgba(59, 130, 246, 0.1)",
                                "rgba(0, 82, 204, 0.05)",
                            ),
                            border_radius="16px",
                            border=rx.cond(
                                ChatState.theme_mode == "dark",
                                "1px solid rgba(59, 130, 246, 0.2)",
                                "1px solid rgba(0, 82, 204, 0.1)",
                            ),
                        ),
                        rx.box(
                            rx.vstack(
                                rx.icon("wallet", size=24),
                                rx.text("Học phí", font_weight="500", font_size="0.9rem"),
                                spacing="2",
                                align_items="center",
                            ),
                            padding="20px",
                            background=rx.cond(
                                ChatState.theme_mode == "dark",
                                "rgba(59, 130, 246, 0.1)",
                                "rgba(0, 82, 204, 0.05)",
                            ),
                            border_radius="16px",
                            border=rx.cond(
                                ChatState.theme_mode == "dark",
                                "1px solid rgba(59, 130, 246, 0.2)",
                                "1px solid rgba(0, 82, 204, 0.1)",
                            ),
                        ),
                        spacing="4",
                        margin_top="32px",
                    ),

                    spacing="3",
                    align_items="center",
                    padding="64px 32px",
                ),
                
                # Messages list
                rx.vstack(
                    rx.foreach(
                        ChatState.messages,
                        message_bubble,
                    ),
                    # Loading indicator với animation
                    rx.cond(
                        ChatState.is_loading,
                        rx.hstack(
                            rx.spinner(
                                size="3",
                                color=rx.cond(
                                    ChatState.theme_mode == "dark",
                                    "#60a5fa",
                                    HUCE_PRIMARY,
                                ),
                            ),
                            rx.text(
                                "Đang suy nghĩ...",
                                font_size="0.95rem",
                                color=rx.cond(
                                    ChatState.theme_mode == "dark",
                                    DARK_COLORS["text_secondary"],
                                    LIGHT_COLORS["text_secondary"],
                                ),
                            ),
                            spacing="3",
                            padding="16px 24px",
                            background=rx.cond(
                                ChatState.theme_mode == "dark",
                                "rgba(59, 130, 246, 0.05)",
                                "rgba(0, 82, 204, 0.03)",
                            ),
                            border_radius="12px",
                        ),
                        rx.box(),
                    ),
                    spacing="3",
                    width="100%",
                    max_width="1000px",
                    padding="32px 24px",
                ),
            ),
            
            # Suggested questions
            suggested_questions(),
            
            spacing="4",
            width="100%",
            max_width="1000px",
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
        
        # Custom scrollbar
        style={
            "&::-webkit-scrollbar": {"width": "8px"},
            "&::-webkit-scrollbar-track": {
                "background": "transparent",
            },
            "&::-webkit-scrollbar-thumb": {
                "background": rx.cond(
                    ChatState.theme_mode == "dark",
                    "rgba(255,255,255,0.2)",
                    "rgba(0,0,0,0.2)",
                ),
                "border-radius": "4px",
            },
            "&::-webkit-scrollbar-thumb:hover": {
                "background": rx.cond(
                    ChatState.theme_mode == "dark",
                    "rgba(255,255,255,0.3)",
                    "rgba(0,0,0,0.3)",
                ),
            },
            "@keyframes bounce": {
                "0%, 100%": {"transform": "translateY(0)"},
                "50%": {"transform": "translateY(-10px)"},
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
