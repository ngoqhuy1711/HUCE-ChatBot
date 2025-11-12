"""
Input Box - HUCE Style with Dark/Light Mode
============================================

Input box theo phong cách HUCE với hỗ trợ dark/light mode.
"""

import reflex as rx
from chatbot.styles.theme import (
    LIGHT_COLORS, DARK_COLORS, SPACING, SPACING_REM, RADIUS, FONT_SIZES
)
from chatbot.state import ChatState


def input_box() -> rx.Component:
    """Input box HUCE style với dark/light mode."""
    return rx.box(
        rx.box(
            rx.form(
                rx.hstack(
                    # Input field - tối giản
                    rx.input(
                        value=ChatState.input_value,
                        on_change=ChatState.handle_input_change,
                        placeholder="💬 Nhập câu hỏi về tuyển sinh của bạn...",
                        name="message",
                        size="2",
                        width="100%",
                        disabled=ChatState.is_loading,
                        style={
                            # Border và background phẳng
                            "border": rx.cond(
                                ChatState.theme_mode == "dark",
                                f"1px solid {DARK_COLORS['border_input']}",
                                f"1px solid {LIGHT_COLORS['border_input']}",
                            ),
                            "background": rx.cond(
                                ChatState.theme_mode == "dark",
                                DARK_COLORS["bg_input"],
                                LIGHT_COLORS["bg_input"],
                            ),
                            "border-radius": "12px",
                            
                            # Font tối giản, dễ đọc
                            "font-size": "1rem",
                            "padding": "0.85rem 1rem",
                            "height": "52px",
                            
                            # Color
                            "color": rx.cond(
                                ChatState.theme_mode == "dark",
                                DARK_COLORS["text_input"],
                                LIGHT_COLORS["text_input"],
                            ),
                            
                            # Animation nhẹ
                            "transition": "border-color 0.2s, box-shadow 0.2s, background 0.2s",
                            
                            # Placeholder
                            "&::placeholder": {
                                "color": rx.cond(
                                    ChatState.theme_mode == "dark",
                                    DARK_COLORS["text_placeholder"],
                                    LIGHT_COLORS["text_placeholder"],
                                ),
                                "font-size": "0.95rem",
                            },
                            
                            # Focus state tinh gọn
                            "&:focus": {
                                "border-color": rx.cond(
                                    ChatState.theme_mode == "dark",
                                    DARK_COLORS["border_input_focus"],
                                    LIGHT_COLORS["border_input_focus"],
                                ),
                                "background": rx.cond(
                                    ChatState.theme_mode == "dark",
                                    DARK_COLORS["bg_input_focus"],
                                    LIGHT_COLORS["bg_input_focus"],
                                ),
                                "box-shadow": rx.cond(
                                    ChatState.theme_mode == "dark",
                                    "0 0 0 3px rgba(79,141,246,0.15)",
                                    "0 0 0 3px rgba(0,82,204,0.15)",
                                ),
                                "outline": "none",
                            },
                            
                            # Hover state tinh gọn
                            "&:hover": {
                                "border-color": rx.cond(
                                    ChatState.theme_mode == "dark",
                                    DARK_COLORS["border_input_focus"],
                                    LIGHT_COLORS["border_input_focus"],
                                ),
                                "background": rx.cond(
                                    ChatState.theme_mode == "dark",
                                    DARK_COLORS["bg_input_focus"],
                                    LIGHT_COLORS["bg_input_focus"],
                                ),
                            },
                        },
                    ),
                    
                    # Send button - tối giản
                    rx.button(
                        rx.cond(
                            ChatState.is_loading,
                            rx.spinner(size="3", color="white"),
                            rx.icon("send", size=20, color="white"),
                        ),
                        
                        type="submit",
                        
                        width="52px",
                        height="52px",
                        padding="0",
                        background=rx.cond(
                            ChatState.theme_mode == "dark",
                            DARK_COLORS["primary"],
                            LIGHT_COLORS["primary"],
                        ),
                        border="none",
                        border_radius="12px",
                        cursor="pointer",
                        box_shadow="0 2px 8px rgba(0,0,0,0.08)",
                        transition="transform 0.15s ease, box-shadow 0.2s ease",
                        
                        _hover={
                            "transform": "translateY(-1px)",
                            "box_shadow": "0 6px 16px rgba(0,0,0,0.12)",
                        },
                        
                        _active={
                            "transform": "translateY(0)",
                        },
                        
                        disabled=ChatState.is_loading,
                    ),
                    
                    spacing=SPACING["md"],
                    width="100%",
                    max_width="900px",
                    align_items="center",
                ),
                
                on_submit=ChatState.send_message,
                width="100%",
                display="flex",
                justify_content="center",
            ),
            
            # Footer text - tối giản
            rx.text(
                "Nhấn Enter để gửi",
                font_size="0.9rem",
                font_weight="500",
                color=rx.cond(
                    ChatState.theme_mode == "dark",
                    DARK_COLORS["text_secondary"],
                    LIGHT_COLORS["text_secondary"],
                ),
                text_align="center",
                margin_top=SPACING_REM["md"],
            ),
            
            width="100%",
            padding=f"{SPACING_REM['xl']} {SPACING_REM['xl']}",
        ),
        
        width="100%",
        background=rx.cond(
            ChatState.theme_mode == "dark",
            DARK_COLORS["bg_input_container"],
            LIGHT_COLORS["bg_input_container"],
        ),
        border_top=rx.cond(
            ChatState.theme_mode == "dark",
            f"1px solid {DARK_COLORS['border_header']}",
            f"1px solid {LIGHT_COLORS['border_header']}",
        ),
        box_shadow="0 -2px 12px rgba(0, 0, 0, 0.04)",
    )
