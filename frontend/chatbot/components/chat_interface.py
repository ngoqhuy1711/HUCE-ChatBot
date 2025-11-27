"""Chat Interface - Giao diện chatbot chính."""

import reflex as rx
from chatbot.components.input_box import input_box
from chatbot.components.message_bubble import message_bubble
from chatbot.state import ChatState
from chatbot.styles.theme import (
    LIGHT_COLORS,
    DARK_COLORS,
    PRIMARY_BLUE,
    PRIMARY_LIGHT,
)

# Static Data
NAV_LINKS = [
    {"label": "AI Chat Helper", "icon": "message-circle", "active": True},
]

CONTACT_INFO = [
    {"label": "Fanpage", "value": "Tuyển sinh HUCE", "icon": "facebook", "href": "https://www.facebook.com/tsdhxdhn"},
    {"label": "Hotline", "value": "024 2240 4010", "icon": "phone", "href": "tel:02422404010"},
    {"label": "Website", "value": "tuyensinh.huce.edu.vn", "icon": "globe", "href": "https://tuyensinh.huce.edu.vn/"},
    {"label": "Email", "value": "tuyensinhdh@huce.edu.vn", "icon": "mail", "href": "mailto:tuyensinhdh@huce.edu.vn"},
]


def _nav_item(link: dict) -> rx.Component:
    """Navigation item trong sidebar."""
    is_active = link.get("active", False)
    return rx.hstack(
        rx.box(
            rx.icon(link["icon"], size=18, color="white" if is_active else "#94a3b8"),
            width="36px",
            height="36px",
            display="flex",
            align_items="center",
            justify_content="center",
            border_radius="10px",
            background=f"linear-gradient(135deg, {PRIMARY_BLUE}, {PRIMARY_LIGHT})" if is_active else "transparent",
        ),
        rx.text(
            link["label"],
            font_weight="600" if is_active else "500",
            font_size="0.95rem",
            color="white" if is_active else "#94a3b8",
        ),
        spacing="3",
        padding="10px 14px",
        border_radius="14px",
        width="100%",
        cursor="pointer",
        background="rgba(59, 130, 246, 0.15)" if is_active else "transparent",
        _hover={"background": "rgba(59, 130, 246, 0.2)", "& p": {"color": "white"}},
        transition="all 0.2s ease",
    )


def _contact_info_card() -> rx.Component:
    """Card thông tin liên hệ."""
    return rx.box(
        rx.vstack(
            rx.text("Kênh liên hệ", color="white", font_weight="700", font_size="0.95rem"),
            *[
                rx.link(
                    rx.hstack(
                        rx.box(
                            rx.icon(item["icon"], size=14, color="#93c5fd"),
                            width="28px",
                            height="28px",
                            display="flex",
                            align_items="center",
                            justify_content="center",
                            border_radius="6px",
                            background="rgba(59, 130, 246, 0.15)",
                        ),
                        rx.vstack(
                            rx.text(item["label"], color="#94a3b8", font_size="0.75rem"),
                            rx.text(item["value"], color="white", font_weight="500", font_size="0.8rem",
                                    style={"word_break": "break-all"}),
                            spacing="0",
                            align_items="flex-start",
                        ),
                        spacing="2",
                        align_items="center",
                        width="100%",
                        padding="6px",
                        border_radius="8px",
                        _hover={"background": "rgba(59, 130, 246, 0.1)"},
                        transition="all 0.2s ease",
                    ),
                    href=item["href"],
                    is_external=True,
                    style={"text_decoration": "none"},
                )
                for item in CONTACT_INFO
            ],
            spacing="2",
            width="100%",
        ),
        width="100%",
        padding="16px",
        border_radius="16px",
        background="rgba(15, 23, 42, 0.7)",
        border="1px solid rgba(59, 130, 246, 0.2)",
    )


def app_sidebar() -> rx.Component:
    """Sidebar chính."""
    return rx.box(
        rx.vstack(
            # Logo
            rx.hstack(
                rx.box(
                    rx.text("HU", font_weight="800", font_size="1rem", color="white"),
                    width="44px",
                    height="44px",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    border_radius="14px",
                    background=f"linear-gradient(135deg, {PRIMARY_BLUE}, {PRIMARY_LIGHT})",
                    box_shadow="0 8px 20px rgba(37, 99, 235, 0.4)",
                ),
                rx.vstack(
                    rx.text("HUCE Bot", color="white", font_weight="700", font_size="1.1rem"),
                    rx.text("Tư vấn tuyển sinh", color="#64748b", font_size="0.8rem"),
                    spacing="0",
                    align_items="flex-start",
                ),
                spacing="3",
                width="100%",
                padding_bottom="24px",
                border_bottom="1px solid rgba(148, 163, 184, 0.1)",
            ),
            # Navigation
            rx.vstack(*[_nav_item(link) for link in NAV_LINKS], spacing="1", width="100%", padding_top="16px"),
            # Reset button
            rx.button(
                rx.hstack(
                    rx.icon("refresh-cw", size=16),
                    rx.text("Làm mới hội thoại", font_weight="600", font_size="0.9rem"),
                    spacing="2",
                ),
                on_click=ChatState.reset_conversation,
                width="100%",
                padding="12px",
                border_radius="12px",
                background="rgba(15, 23, 42, 0.4)",
                border="1px solid rgba(59, 130, 246, 0.3)",
                color="white",
                justify_content="center",
                _hover={"background": "rgba(59, 130, 246, 0.2)"},
                margin_top="12px",
            ),
            rx.spacer(),
            _contact_info_card(),
            spacing="4",
            height="100%",
            align_items="stretch",
        ),
        width="280px",
        padding="20px 16px",
        height="100%",
        border_radius="24px",
        overflow_y="auto",
        background=rx.cond(ChatState.theme_mode == "dark", DARK_COLORS["bg_sidebar"], LIGHT_COLORS["bg_sidebar"]),
        box_shadow="0 25px 50px rgba(0, 0, 0, 0.25)",
        flex_shrink="0",
    )


def _header_toolbar() -> rx.Component:
    """Header với title và theme toggle."""
    return rx.hstack(
        rx.vstack(
            rx.text(
                "AI CHAT HELPER",
                font_size="0.75rem",
                font_weight="600",
                letter_spacing="0.15em",
                color=rx.cond(ChatState.theme_mode == "dark", "#93c5fd", PRIMARY_BLUE),
            ),
            rx.text(
                "Hỗ trợ tuyển sinh HUCE 2025",
                font_size="1.5rem",
                font_weight="700",
                color=rx.cond(ChatState.theme_mode == "dark", DARK_COLORS["text_primary"],
                              LIGHT_COLORS["text_primary"]),
            ),
            spacing="1",
            align_items="flex-start",
        ),
        rx.spacer(),
        rx.button(
            rx.icon(rx.cond(ChatState.theme_mode == "dark", "sun", "moon"), size=18),
            on_click=ChatState.toggle_theme,
            padding="10px",
            border_radius="12px",
            background=rx.cond(ChatState.theme_mode == "dark", "rgba(30, 41, 59, 0.8)", "rgba(255, 255, 255, 0.9)"),
            border=rx.cond(ChatState.theme_mode == "dark", "1px solid rgba(59, 130, 246, 0.2)",
                           "1px solid rgba(15, 23, 42, 0.08)"),
            color=rx.cond(ChatState.theme_mode == "dark", "#fbbf24", "#64748b"),
            _hover={"background": rx.cond(ChatState.theme_mode == "dark", "rgba(59, 130, 246, 0.2)",
                                          "rgba(37, 99, 235, 0.1)")},
        ),
        width="100%",
        align_items="center",
        flex_shrink="0",
    )


def _messages_container() -> rx.Component:
    """Container hiển thị tin nhắn."""
    return rx.box(
        rx.cond(
            ChatState.messages.length() == 0,
            # Empty state
            rx.box(
                rx.vstack(
                    rx.box(
                        rx.icon("message-circle", size=48, color=PRIMARY_LIGHT),
                        width="100px",
                        height="100px",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        border_radius="50%",
                        background=rx.cond(ChatState.theme_mode == "dark", "rgba(59, 130, 246, 0.1)",
                                           "rgba(37, 99, 235, 0.08)"),
                    ),
                    rx.text(
                        "Bắt đầu trò chuyện",
                        font_size="1.25rem",
                        font_weight="600",
                        color=rx.cond(ChatState.theme_mode == "dark", DARK_COLORS["text_primary"],
                                      LIGHT_COLORS["text_primary"]),
                    ),
                    spacing="3",
                    align_items="center",
                    justify_content="center",
                    height="100%",
                ),
                width="100%",
                height="100%",
                display="flex",
                align_items="center",
                justify_content="center",
            ),
            # Messages list
            rx.box(
                rx.vstack(
                    rx.foreach(ChatState.messages, message_bubble),
                    rx.cond(
                        ChatState.is_loading,
                        rx.hstack(
                            rx.spinner(size="3", color=PRIMARY_LIGHT),
                            rx.text(
                                "Đang xử lý...",
                                color=rx.cond(ChatState.theme_mode == "dark", "#93c5fd", PRIMARY_BLUE),
                                font_weight="500",
                            ),
                            spacing="3",
                            padding="16px 24px",
                            border_radius="16px",
                            background=rx.cond(ChatState.theme_mode == "dark", "rgba(59, 130, 246, 0.1)",
                                               "rgba(37, 99, 235, 0.08)"),
                        ),
                        rx.box(),
                    ),
                    spacing="4",
                    width="100%",
                    align_items="stretch",
                ),
                width="100%",
                min_height="100%",
                display="flex",
                flex_direction="column",
                justify_content="flex-end",
            ),
        ),
        id="messages-box",
        flex="1",
        width="100%",
        padding="20px",
        border_radius="20px",
        background=rx.cond(ChatState.theme_mode == "dark", DARK_COLORS["glass_bg"], LIGHT_COLORS["glass_bg"]),
        border=rx.cond(ChatState.theme_mode == "dark", f"1px solid {DARK_COLORS['glass_border']}",
                       f"1px solid {LIGHT_COLORS['glass_border']}"),
        overflow_y="auto",
        overflow_x="hidden",
        min_height="0",
        style={
            "scrollbar-width": "thin",
            "scrollbar-color": f"{PRIMARY_LIGHT}40 transparent",
            "&::-webkit-scrollbar": {"width": "6px"},
            "&::-webkit-scrollbar-thumb": {"background": f"{PRIMARY_LIGHT}50", "border-radius": "999px"},
        },
    )


def chat_interface() -> rx.Component:
    """Layout chính của chatbot."""
    return rx.box(
        rx.hstack(
            app_sidebar(),
            rx.vstack(
                _header_toolbar(),
                _messages_container(),
                rx.box(input_box(), width="100%", flex_shrink="0"),
                spacing="4",
                width="100%",
                height="100%",
                min_height="0",
            ),
            spacing="6",
            width="100%",
            height="100%",
            align_items="stretch",
        ),
        padding="24px",
        background=rx.cond(ChatState.theme_mode == "dark", DARK_COLORS["bg_app"], LIGHT_COLORS["bg_app"]),
        height="100vh",
        overflow="hidden",
    )
