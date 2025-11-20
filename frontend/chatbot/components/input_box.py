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
                        placeholder="Nhập câu hỏi về tuyển sinh của bạn...",
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
                            "border-radius": "16px",

                            # Font size lớn hơn
                            "font-size": "1.05rem",
                            "padding": "1rem 1.25rem",
                            "height": "56px",

                            # Color
                            "color": rx.cond(
                                ChatState.theme_mode == "dark",
                                DARK_COLORS["text_input"],
                                LIGHT_COLORS["text_input"],
                            ),
                            
                            # Animation nhẹ
                            "transition": "border-color 0.2s, box-shadow 0.2s, background 0.2s",
                            
                            # Placeholder với contrast tốt hơn
                            "&::placeholder": {
                                "color": rx.cond(
                                    ChatState.theme_mode == "dark",
                                    "#cbd5e1",  # Light slate - sáng hơn cho dark mode
                                    "#475569",  # Dark slate - tối hơn cho light mode
                                ),
                                "font-size": "0.95rem",
                                "opacity": "0.8",  # Thêm opacity để softer
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
                    
                    # Send button với vibrant gradient
                    rx.button(
                        rx.cond(
                            ChatState.is_loading,
                            rx.spinner(size="3", color="white"),
                            rx.icon("send", size=22, color="white"),
                        ),
                        
                        type="submit",
                        
                        width="56px",
                        height="56px",
                        padding="0",
                        background="linear-gradient(135deg, #0052CC 0%, #2563eb 100%)",
                        border="none",
                        border_radius="16px",
                        cursor="pointer",
                        box_shadow="0 4px 12px rgba(0, 82, 204, 0.3)",
                        transition="all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1)",

                        _hover={
                            "transform": "translateY(-2px) scale(1.05)",
                            "box_shadow": "0 8px 20px rgba(0, 82, 204, 0.4)",
                            "background": "linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)",
                        },
                        
                        _active={
                            "transform": "translateY(0) scale(0.98)",
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
            
            # Footer text với better typography
            rx.text(
                "Nhấn Enter để gửi • Powered by HUCE AI",
                font_size="0.875rem",
                font_weight="500",
                color=rx.cond(
                    ChatState.theme_mode == "dark",
                    "#64748b",
                    "#94a3b8",
                ),
                text_align="center",
                margin_top=SPACING_REM["md"],
                letter_spacing="-0.01em",
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
