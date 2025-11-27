"""Message Bubble - Hiển thị tin nhắn."""

import reflex as rx
from chatbot.state import Message, ChatState
from chatbot.styles.theme import LIGHT_COLORS, DARK_COLORS, PRIMARY_BLUE, PRIMARY_LIGHT, ACCENT_INDIGO


def message_bubble(message: Message) -> rx.Component:
    """Message bubble với style xanh lam."""
    is_user = message.role == "user"

    return rx.box(
        rx.hstack(
            rx.cond(
                is_user, rx.box(),
                rx.box(
                    rx.icon("bot", size=22, color="white"),
                    width="44px", height="44px", display="flex", align_items="center", justify_content="center",
                    background=f"linear-gradient(135deg, {PRIMARY_BLUE} 0%, {PRIMARY_LIGHT} 100%)",
                    border_radius="14px", flex_shrink="0", box_shadow="0 8px 20px rgba(37, 99, 235, 0.35)",
                    border="2px solid rgba(255, 255, 255, 0.2)",
                ),
            ),
            rx.box(
                rx.markdown(message.content),
                padding="20px 24px",
                border_radius=rx.cond(is_user, "20px 20px 6px 20px", "20px 20px 20px 6px"),
                background=rx.cond(is_user, f"linear-gradient(135deg, {PRIMARY_BLUE} 0%, {PRIMARY_LIGHT} 100%)",
                                   rx.cond(ChatState.theme_mode == "dark",
                                           "linear-gradient(145deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.85) 100%)",
                                           "linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)")),
                border=rx.cond(is_user, "none",
                               rx.cond(ChatState.theme_mode == "dark", "1px solid rgba(59, 130, 246, 0.2)",
                                       "1px solid rgba(37, 99, 235, 0.12)")),
                box_shadow=rx.cond(is_user, "0 10px 25px rgba(37, 99, 235, 0.3)",
                                   rx.cond(ChatState.theme_mode == "dark", "0 8px 20px rgba(0, 0, 0, 0.3)",
                                           "0 8px 20px rgba(15, 23, 42, 0.08)")),
                max_width="90%",
                color=rx.cond(is_user, "white", rx.cond(ChatState.theme_mode == "dark", "#e2e8f0", "#1e293b")),
                font_size="1rem", line_height="1.7", animation="slideUp 0.35s cubic-bezier(0.34, 1.56, 0.64, 1)",
                style={
                    "h1, h2, h3": {"margin_top": "1.25em", "margin_bottom": "0.6em", "font_weight": "700",
                                   "line_height": "1.35"},
                    "h1": {"font_size": "1.5em", "color": rx.cond(is_user, "#ffffff",
                                                                  rx.cond(ChatState.theme_mode == "dark", "#93c5fd",
                                                                          PRIMARY_BLUE))},
                    "h2": {"font_size": "1.3em", "color": rx.cond(is_user, "#dbeafe",
                                                                  rx.cond(ChatState.theme_mode == "dark", "#60a5fa",
                                                                          "#1d4ed8"))},
                    "h3": {"font_size": "1.15em", "color": rx.cond(is_user, "#bfdbfe",
                                                                   rx.cond(ChatState.theme_mode == "dark", "#3b82f6",
                                                                           "#2563eb"))},
                    "ul, ol": {"margin_left": "1.5em", "margin_bottom": "0.8em"},
                    "li": {"margin_bottom": "0.5em", "line_height": "1.65"},
                    "li::marker": {"color": rx.cond(is_user, "#93c5fd",
                                                    rx.cond(ChatState.theme_mode == "dark", "#60a5fa", PRIMARY_LIGHT)),
                                   "font_weight": "700"},
                    "strong": {"font_weight": "700", "color": rx.cond(is_user, "#fef3c7",
                                                                      rx.cond(ChatState.theme_mode == "dark", "#fbbf24",
                                                                              "#d97706"))},
                    "a": {"color": rx.cond(is_user, "#bfdbfe",
                                           rx.cond(ChatState.theme_mode == "dark", "#93c5fd", PRIMARY_LIGHT)),
                          "text_decoration": "underline", "font_weight": "600"},
                    "code": {
                        "background": rx.cond(is_user, "rgba(255, 255, 255, 0.2)",
                                              rx.cond(ChatState.theme_mode == "dark", "rgba(59, 130, 246, 0.15)",
                                                      "rgba(37, 99, 235, 0.1)")),
                        "color": rx.cond(is_user, "#ffffff",
                                         rx.cond(ChatState.theme_mode == "dark", "#93c5fd", PRIMARY_BLUE)),
                        "padding": "0.25em 0.6em", "border_radius": "6px", "font_size": "0.9em",
                        "font_family": "'JetBrains Mono', monospace",
                        "border": rx.cond(is_user, "1px solid rgba(255, 255, 255, 0.25)",
                                          rx.cond(ChatState.theme_mode == "dark", "1px solid rgba(59, 130, 246, 0.25)",
                                                  "1px solid rgba(37, 99, 235, 0.2)")),
                    },
                    "pre": {
                        "background": rx.cond(is_user, "rgba(0, 0, 0, 0.15)",
                                              rx.cond(ChatState.theme_mode == "dark", "#0f172a", "#eff6ff")),
                        "padding": "1.25em", "border_radius": "12px", "margin": "0.8em 0", "overflow_x": "auto",
                        "border": rx.cond(is_user, "1px solid rgba(255, 255, 255, 0.15)",
                                          rx.cond(ChatState.theme_mode == "dark", "1px solid rgba(59, 130, 246, 0.2)",
                                                  "1px solid rgba(37, 99, 235, 0.15)")),
                    },
                    "blockquote": {
                        "border_left": f"4px solid {PRIMARY_LIGHT}", "padding": "0.8em 1.2em", "margin": "0.8em 0",
                        "border_radius": "0 10px 10px 0",
                        "background": rx.cond(is_user, "rgba(255, 255, 255, 0.1)",
                                              rx.cond(ChatState.theme_mode == "dark", "rgba(59, 130, 246, 0.08)",
                                                      "rgba(37, 99, 235, 0.06)")),
                    },
                    "table": {"width": "100%", "border_collapse": "collapse", "margin": "1em 0"},
                    "th, td": {"border": rx.cond(ChatState.theme_mode == "dark", "1px solid rgba(59, 130, 246, 0.2)",
                                                 "1px solid rgba(37, 99, 235, 0.15)"), "padding": "0.75em 1em",
                               "text_align": "left"},
                    "th": {"background": rx.cond(ChatState.theme_mode == "dark", "rgba(59, 130, 246, 0.1)",
                                                 "rgba(37, 99, 235, 0.08)"), "font_weight": "600"},
                },
            ),
            rx.cond(
                is_user,
                rx.box(
                    rx.icon("user", size=20, color="white"),
                    width="42px", height="42px", display="flex", align_items="center", justify_content="center",
                    background=f"linear-gradient(135deg, {ACCENT_INDIGO} 0%, #a78bfa 100%)",
                    border_radius="14px", flex_shrink="0", box_shadow="0 6px 16px rgba(99, 102, 241, 0.35)",
                    border="2px solid rgba(255, 255, 255, 0.2)",
                ),
                rx.box(),
            ),
            spacing="3", align_items="flex-end", justify_content=rx.cond(is_user, "flex-end", "flex-start"),
            width="100%",
        ),
        width="100%", margin_bottom="20px",
        style={"@keyframes slideUp": {"0%": {"opacity": "0", "transform": "translateY(15px) scale(0.97)"},
                                      "100%": {"opacity": "1", "transform": "translateY(0) scale(1)"}}},
    )
