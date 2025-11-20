"""
Chatbot Main App
================

File chính (entry point) của Reflex app.

Chạy app:
    cd frontend
    reflex run

App sẽ chạy tại: http://localhost:3000
"""

import reflex as rx
from chatbot.components import chat_interface
from chatbot.state import ChatState


# ============================================================================
# GLOBAL STYLES
# ============================================================================

# Modern font stack với fallbacks
FONT_FAMILY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif"

# CSS reset với enhanced typography
global_style = {
    "body": {
        "margin": "0",
        "padding": "0",
        "overflow": "hidden",
        "font-family": FONT_FAMILY,
        "font-size": "16px",
        "-webkit-font-smoothing": "antialiased",
        "-moz-osx-font-smoothing": "grayscale",
        "text-rendering": "optimizeLegibility",
    },
    "#root": {
        "width": "100vw",
        "height": "100vh",
        "overflow": "hidden",
    },
    # Import Inter font from Google Fonts
    "@import": "url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap')",
}

# Script để auto-detect theme từ browser
THEME_DETECT_SCRIPT = """
<script>
(function() {
    // Check if browser supports prefers-color-scheme
    if (window.matchMedia) {
        const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
        
        // Set initial theme
        const initialTheme = darkModeQuery.matches ? 'dark' : 'light';
        
        // Trigger theme change in Reflex state
        if (window._update_theme) {
            window._update_theme(initialTheme);
        }
        
        // Listen for changes
        darkModeQuery.addEventListener('change', (e) => {
            const newTheme = e.matches ? 'dark' : 'light';
            if (window._update_theme) {
                window._update_theme(newTheme);
            }
        });
    }
})();
</script>
"""


# ============================================================================
# APP CONFIGURATION
# ============================================================================

# Metadata cho app
app_name = "Tra cứu thông tin tuyển sinh HUCE"
app_description = "Chatbot hỗ trợ tra cứu thông tin tuyển sinh Đại học Xây dựng Hà Nội"


# ============================================================================
# PAGES - Định nghĩa các trang
# ============================================================================

def index() -> rx.Component:
    """
    Trang chính (home page).
    
    Returns:
        rx.Component - Chat interface
    """
    return rx.fragment(
        # Script để auto-detect theme
        rx.script("""
            // Auto-detect theme từ browser preference
            (function() {
                if (window.matchMedia) {
                    const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
                    
                    // Set initial theme
                    const setTheme = (isDark) => {
                        // Trigger Reflex state update
                        const theme = isDark ? 'dark' : 'light';
                        console.log('Browser theme detected:', theme);
                        
                        // Try to update Reflex state if available
                        if (window.setTheme) {
                            window.setTheme(theme);
                        }
                        
                        // Store in localStorage as fallback
                        localStorage.setItem('theme', theme);
                    };
                    
                    // Set initial theme
                    setTheme(darkModeQuery.matches);
                    
                    // Listen for changes
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

# Tạo Reflex app với global styles
app = rx.App(
    style=global_style,
)

# Add pages
app.add_page(
    index,
    route="/",  # Root route
    title=app_name,
    description=app_description,
    
    # Lifecycle
    on_load=ChatState.on_load,  # Gọi khi page load
)


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Note: Không nên chạy trực tiếp file này
    # Dùng: reflex run
    pass
