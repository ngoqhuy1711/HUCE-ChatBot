"""Input Box - Ô nhập tin nhắn."""

import reflex as rx
from chatbot.state import ChatState
from chatbot.styles.theme import (
    LIGHT_COLORS,
    DARK_COLORS,
    PRIMARY_BLUE,
    PRIMARY_LIGHT,
)


def input_box() -> rx.Component:
    """Input box với style xanh lam."""
    return rx.box(
        rx.form(
            rx.hstack(
                rx.input(
                    value=ChatState.input_value,
                    on_change=ChatState.handle_input_change,
                    name="message",
                    disabled=ChatState.is_loading,
                    width="100%",
                    height="46px",
                    variant="surface",
                    radius="large",
                    style={
                        "border": "none !important",
                        "background": "transparent !important",
                        "font-size": "1rem",
                        "font-weight": "500",
                        "padding": "0 16px",
                        "box-shadow": "none !important",
                        "outline": "none !important",
                        "color": rx.cond(ChatState.theme_mode == "dark", "#f1f5f9", "#1e293b"),
                        "--text-field-focus-color": "transparent",
                        "--focus-8": "transparent",
                        "&:focus, &:focus-within, &:focus-visible": {
                            "box-shadow": "none !important",
                            "outline": "none !important",
                            "border": "none !important",
                        },
                        "&::placeholder": {
                            "color": rx.cond(ChatState.theme_mode == "dark", "#94a3b8", "#64748b"),
                            "font-weight": "400",
                            "opacity": "1",
                        },
                        "& input": {"outline": "none !important", "box-shadow": "none !important"},
                    },
                ),
                rx.button(
                    rx.cond(
                        ChatState.is_loading,
                        rx.spinner(size="3", color="white"),
                        rx.icon("send", size=18, color="white"),
                    ),
                    type="submit",
                    width="42px",
                    height="42px",
                    padding="0",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    background=f"linear-gradient(135deg, {PRIMARY_BLUE} 0%, {PRIMARY_LIGHT} 100%)",
                    border="none",
                    border_radius="12px",
                    cursor="pointer",
                    box_shadow="0 4px 12px rgba(37, 99, 235, 0.3)",
                    transition="all 0.2s ease",
                    flex_shrink="0",
                    _hover={"transform": "translateY(-1px)", "box_shadow": "0 6px 16px rgba(37, 99, 235, 0.4)"},
                    _active={"transform": "translateY(0)"},
                    disabled=ChatState.is_loading,
                ),
                spacing="2",
                width="100%",
                align_items="center",
                padding="4px 6px 4px 4px",
                background=rx.cond(ChatState.theme_mode == "dark", "rgba(15, 23, 42, 0.7)",
                                   "rgba(255, 255, 255, 0.98)"),
                border=rx.cond(ChatState.theme_mode == "dark", "1px solid rgba(59, 130, 246, 0.3)",
                               "1px solid rgba(37, 99, 235, 0.2)"),
                border_radius="14px",
                box_shadow=rx.cond(ChatState.theme_mode == "dark", "0 4px 20px rgba(0, 0, 0, 0.25)",
                                   "0 4px 20px rgba(37, 99, 235, 0.1)"),
            ),
            on_submit=ChatState.send_message,
            width="100%",
        ),
        rx.hstack(
            rx.text("Nhấn Enter để gửi", font_size="0.7rem",
                    color=rx.cond(ChatState.theme_mode == "dark", "#64748b", "#94a3b8")),
            rx.spacer(),
            rx.hstack(
                rx.text("Powered by", font_size="0.7rem",
                        color=rx.cond(ChatState.theme_mode == "dark", "#64748b", "#94a3b8")),
                rx.text("HUCE Bot", font_size="0.7rem", font_weight="600", color=PRIMARY_BLUE),
                spacing="1",
            ),
            width="100%",
            padding="6px 8px 2px 8px",
        ),
        width="100%",
    )
