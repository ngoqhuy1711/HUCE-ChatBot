"""
Message Bubble - Modern & Clean Design
=======================================

Message bubble hiện đại với typography tốt và markdown rendering hoàn hảo.
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
    """Premium message bubble với rich colors và animations."""

    is_user = message.role == "user"

    return rx.box(
        rx.hstack(
            # Bot avatar với pulse animation
            rx.cond(
                is_user,
                rx.box(),
                rx.box(
                    rx.icon("bot", size=24, color="white"),
                    width="48px",
                    height="48px",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    background="linear-gradient(135deg, #0052CC, #3b82f6, #60a5fa)",
                    border_radius="50%",
                    flex_shrink="0",
                    box_shadow="0 8px 20px rgba(0,82,204,0.4), 0 3px 8px rgba(59,130,246,0.3)",
                    border="3px solid rgba(255,255,255,0.25)",
                    animation="pulse 3s ease-in-out infinite",
                ),
            ),

            # Message content
            rx.box(
                rx.markdown(message.content),

                padding="24px 28px",
                border_radius=rx.cond(is_user, "24px 24px 8px 24px", "24px 24px 24px 8px"),
                background=rx.cond(
                    is_user,
                    "linear-gradient(135deg, #0052CC 0%, #1e40af 50%, #3b82f6 100%)",
                    rx.cond(
                        ChatState.theme_mode == "dark",
                        "linear-gradient(145deg, #1f2937, #1a202e)",
                        "linear-gradient(145deg, #ffffff, #f8fafc)",
                    ),
                ),
                border=rx.cond(
                    is_user,
                    "none",
                    "1px solid " + rx.cond(
                        ChatState.theme_mode == "dark",
                        "rgba(59,130,246,0.2)",
                        "rgba(0,82,204,0.15)",
                    ),
                ),
                box_shadow=rx.cond(
                    is_user,
                    "0 10px 30px rgba(0,82,204,0.35), 0 4px 12px rgba(30,64,175,0.2)",
                    rx.cond(
                        ChatState.theme_mode == "dark",
                        "0 6px 20px rgba(0,0,0,0.4), 0 2px 8px rgba(59,130,246,0.1)",
                        "0 6px 20px rgba(0,0,0,0.08)",
                    ),
                ),
                max_width="80%",
                color=rx.cond(is_user, "white", rx.cond(ChatState.theme_mode == "dark", "#e5e7eb", "#1f2937")),
                font_size="1.05rem",
                line_height="1.75",
                animation="slideUp 0.4s cubic-bezier(0.34,1.56,0.64,1)",

                style={
                    "h1,h2,h3": {
                        "margin_top": "1.5em",
                        "margin_bottom": "0.7em",
                        "font_weight": "700",
                        "line_height": "1.3",
                        "letter_spacing": "-0.02em",
                    },
                    "h1": {
                        "font_size": "1.6em",
                        "color": rx.cond(
                            is_user,
                            "#ffffff",
                            rx.cond(ChatState.theme_mode == "dark", "#f1f5f9", "#0052CC")
                        )
                    },
                    "h2": {
                        "font_size": "1.35em",
                        "color": rx.cond(
                            is_user,
                            "#e0f2fe",
                            rx.cond(ChatState.theme_mode == "dark", "#bfdbfe", "#1e40af")
                        )
                    },
                    "h3": {
                        "font_size": "1.15em",
                        "color": rx.cond(
                            is_user,
                            "#bae6fd",
                            rx.cond(ChatState.theme_mode == "dark", "#93c5fd", "#2563eb")
                        )
                    },
                    "ul,ol": {"margin_left": "1.8em", "margin_bottom": "1em"},
                    "li": {"margin_bottom": "0.6em", "line_height": "1.7"},
                    "li::marker": {
                        "color": rx.cond(
                            is_user,
                            "#93c5fd",
                            rx.cond(ChatState.theme_mode == "dark", "#60a5fa", "#3b82f6")
                        ),
                        "font_weight": "700"
                    },
                    "strong": {
                        "font_weight": "700",
                        "color": rx.cond(
                            is_user,
                            "#fef3c7",
                            rx.cond(ChatState.theme_mode == "dark", "#fcd34d", "#f59e0b")
                        ),
                        "padding": "0 0.2em",
                    },
                    "a": {
                        "color": rx.cond(
                            is_user,
                            "#dbeafe",
                            rx.cond(ChatState.theme_mode == "dark", "#93c5fd", "#2563eb")
                        ),
                        "text_decoration": "underline",
                        "text_decoration_thickness": "2px",
                        "font_weight": "600",
                    },
                    "code": {
                        "background": rx.cond(
                            is_user,
                            "rgba(255,255,255,0.25)",
                            rx.cond(
                                ChatState.theme_mode == "dark",
                                "#1e293b",  # Dark slate cho dark mode
                                "#f1f5f9"   # Light gray cho light mode
                            )
                        ),
                        "color": rx.cond(
                            is_user,
                            "#ffffff",  # White cho user
                            rx.cond(
                                ChatState.theme_mode == "dark",
                                "#f1f5f9",  # Soft white cho dark - readable
                                "#1e293b"   # Dark slate cho light - contrast tốt
                            )
                        ),
                        "padding": "0.3em 0.7em",
                        "border_radius": "6px",
                        "font_size": "0.9em",
                        "font_family": "'JetBrains Mono', 'Fira Code', 'Courier New', monospace",
                        "border": "1px solid " + rx.cond(
                            is_user,
                            "rgba(255,255,255,0.35)",
                            rx.cond(
                                ChatState.theme_mode == "dark",
                                "rgba(59,130,246,0.3)",
                                "rgba(0,82,204,0.2)"
                            )
                        ),
                    },
                    "pre": {
                        "background": rx.cond(is_user, "rgba(0,0,0,0.15)", rx.cond(ChatState.theme_mode == "dark", "#0f172a", "#f8fafc")),
                        "padding": "1.5em",
                        "border_radius": "12px",
                        "margin": "1em 0",
                        "border": "1px solid " + rx.cond(is_user, "rgba(255,255,255,0.2)", "rgba(59,130,246,0.2)"),
                    },
                    "blockquote": {
                        "border_left": "5px solid " + rx.cond(is_user, "rgba(255,255,255,0.7)", "#3b82f6"),
                        "padding": "1em 1.5em",
                        "margin": "1em 0",
                        "background": rx.cond(is_user, "rgba(255,255,255,0.08)", "rgba(59,130,246,0.08)"),
                        "border_radius": "0 12px 12px 0",
                    },
                },
            ),

            # User avatar
            rx.cond(
                is_user,
                rx.box(
                    rx.icon("user", size=22, color="white"),
                    width="46px",
                    height="46px",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    background="linear-gradient(135deg, #64748b, #475569, #334155)",
                    border_radius="50%",
                    flex_shrink="0",
                    box_shadow="0 6px 16px rgba(0,0,0,0.3)",
                    border="3px solid rgba(255,255,255,0.2)",
                ),
                rx.box(),
            ),

            spacing="3",
            align_items="flex-end",
            justify_content=rx.cond(is_user, "flex-end", "flex-start"),
            width="100%",
        ),

        width="100%",
        margin_bottom="24px",

        style={
            "@keyframes slideUp": {
                "0%": {"opacity": "0", "transform": "translateY(20px) scale(0.95)"},
                "60%": {"transform": "translateY(-3px) scale(1.02)"},
                "100%": {"opacity": "1", "transform": "translateY(0) scale(1)"},
            },
            "@keyframes pulse": {
                "0%,100%": {"box-shadow": "0 8px 20px rgba(0,82,204,0.4), 0 3px 8px rgba(59,130,246,0.3)", "transform": "scale(1)"},
                "50%": {"box-shadow": "0 12px 30px rgba(0,82,204,0.6), 0 5px 12px rgba(59,130,246,0.5)", "transform": "scale(1.05)"},
            },
        },
    )