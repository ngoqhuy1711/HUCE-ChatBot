"""
Message Bubble - HUCE Style with Dark/Light Mode
=================================================

Message bubble theo phong cách HUCE với hỗ trợ dark/light mode.
"""

import reflex as rx
from chatbot.styles.theme import (
    LIGHT_COLORS,
    DARK_COLORS,
    SPACING,
    SPACING_REM,
    RADIUS,
    FONT_SIZES,
    SHADOWS,
)
from chatbot.state import Message, ChatState


def message_bubble(message: Message) -> rx.Component:
    """Message bubble HUCE style với dark/light mode."""

    return rx.box(
        rx.hstack(
            # Avatar đơn giản
            rx.cond(
                message.role == "user",
                rx.box(
                    "",
                    width="40px",
                    height="40px",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    background=rx.cond(
                        ChatState.theme_mode == "dark",
                        "#1f2937",
                        "#e5e7eb",
                    ),
                    border_radius="50%",
                    flex_shrink="0",
                ),
                rx.box(
                    "",
                    width="40px",
                    height="40px",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    background=rx.cond(
                        ChatState.theme_mode == "dark",
                        "#0b1222",
                        "#eef2ff",
                    ),
                    border_radius="50%",
                    flex_shrink="0",
                ),
            ),
            # Message content
            rx.box(
                rx.markdown(
                    message.content,
                    font_size=FONT_SIZES["md"],
                    line_height="1.6",
                    white_space="pre-wrap",
                    color=rx.cond(
                        message.role == "user",
                        "white",
                        rx.cond(
                            ChatState.theme_mode == "dark",
                            DARK_COLORS["text_bot_msg"],
                            LIGHT_COLORS["text_bot_msg"],
                        ),
                    ),
                ),
                padding=SPACING_REM["lg"],
                border_radius=rx.cond(
                    message.role == "user",
                    "14px 14px 4px 14px",
                    "14px 14px 14px 4px",
                ),
                background=rx.cond(
                    message.role == "user",
                    rx.cond(
                        ChatState.theme_mode == "dark",
                        DARK_COLORS["bg_user_msg"],
                        LIGHT_COLORS["bg_user_msg"],
                    ),
                    rx.cond(
                        ChatState.theme_mode == "dark",
                        DARK_COLORS["bg_bot_msg"],
                        LIGHT_COLORS["bg_bot_msg"],
                    ),
                ),
                border=rx.cond(
                    message.role == "user",
                    "none",
                    rx.cond(
                        ChatState.theme_mode == "dark",
                        f"1px solid {DARK_COLORS['border_bot_msg']}",
                        f"1px solid {LIGHT_COLORS['border_bot_msg']}",
                    ),
                ),
                box_shadow=rx.cond(
                    message.role == "user",
                    "none",
                    "0 1px 4px rgba(0, 0, 0, 0.06)",
                ),
                max_width="70%",
                # Animation tinh gọn
                animation="slideIn 200ms ease-out",
            ),
            spacing=SPACING["md"],
            align_items="flex-start",
            justify_content=rx.cond(
                message.role == "user",
                "flex-end",
                "flex-start",
            ),
            width="100%",
        ),
        width="100%",
        margin_bottom=SPACING_REM["md"],
        # Animation keyframes
        style={
            "@keyframes slideIn": {
                "from": {
                    "opacity": "0",
                    "transform": "translateY(6px)",
                },
                "to": {
                    "opacity": "1",
                    "transform": "translateY(0)",
                },
            },
        },
    )
