"""Chatbot Main App - HUCE Chatbot."""

import reflex as rx
from chatbot.components import chat_interface
from chatbot.state import ChatState

# Global styles
FONT_FAMILY = "'Plus Jakarta Sans', 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif"
MONO_FONT = "'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'Consolas', monospace"

global_style = {
    "@import": [
        "url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap')",
        "url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap')",
    ],

    "*, *::before, *::after": {
        "box-sizing": "border-box",
    },

    "body": {
        "margin": "0",
        "padding": "0",
        "overflow": "hidden",
        "font-family": FONT_FAMILY,
        "font-size": "16px",
        "-webkit-font-smoothing": "antialiased",
        "-moz-osx-font-smoothing": "grayscale",
        "text-rendering": "optimizeLegibility",
        "font-feature-settings": "'cv02', 'cv03', 'cv04', 'cv11'",
    },

    "#root": {
        "width": "100vw",
        "height": "100vh",
        "overflow": "hidden",
    },

    # Custom scrollbar styling
    "::-webkit-scrollbar": {
        "width": "6px",
        "height": "6px",
    },
    "::-webkit-scrollbar-track": {
        "background": "transparent",
    },
    "::-webkit-scrollbar-thumb": {
        "background": "rgba(6, 182, 212, 0.3)",
        "border-radius": "999px",
    },
    "::-webkit-scrollbar-thumb:hover": {
        "background": "rgba(6, 182, 212, 0.5)",
    },

    # Selection styling
    "::selection": {
        "background": "rgba(6, 182, 212, 0.25)",
        "color": "inherit",
    },

    # Focus outline
    ":focus-visible": {
        "outline": "2px solid #06b6d4",
        "outline-offset": "2px",
    },

    # Button reset
    "button": {
        "font-family": "inherit",
    },

    # Input reset
    "input, textarea": {
        "font-family": "inherit",
    },

    # Code styling
    "code, pre": {
        "font-family": MONO_FONT,
    },
}

# ============================================================================
# APP METADATA
# ============================================================================

app_name = "HUCE Bot - Tra cứu tuyển sinh"
app_description = "Chatbot hỗ trợ tra cứu thông tin tuyển sinh Đại học Xây dựng Hà Nội (HUCE) 2025"


# ============================================================================
# PAGES
# ============================================================================

def index() -> rx.Component:
    """Trang chính (home page)."""
    return rx.fragment(
        # Theme detection script
        rx.script("""
            (function() {
                if (window.matchMedia) {
                    const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
                    
                    const setTheme = (isDark) => {
                        const theme = isDark ? 'dark' : 'light';
                        console.log('Theme detected:', theme);
                        localStorage.setItem('theme', theme);
                    };
                    
                    setTheme(darkModeQuery.matches);
                    
                    darkModeQuery.addEventListener('change', (e) => {
                        setTheme(e.matches);
                    });
                }
            })();
        """),
        chat_interface(),
    )


# ============================================================================
# APP INITIALIZATION
# ============================================================================

app = rx.App(
    style=global_style,
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap",
        "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap",
    ],
)

# Add pages
app.add_page(
    index,
    route="/",
    title=app_name,
    description=app_description,
    on_load=ChatState.on_load,
)

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    pass
