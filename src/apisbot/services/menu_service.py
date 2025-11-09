"""Menu service for command hints and help documentation.

Framework-agnostic service with no aiogram dependencies.
Provides user-friendly command hints at each conversation step.
"""

from typing import List

from ..models.chart_selection import ChartSelection


class MenuService:
    """Service for generating menu hints and help documentation.

    Implements FR-003: Help button shows comprehensive documentation.
    Implements US1: Users see menu hints at each step with command descriptions.

    No aiogram dependencies: Fully testable without bot infrastructure.
    """

    @staticmethod
    def get_start_menu_text() -> str:
        """Get welcome text and chart selection menu for /start command.

        Returns:
            Formatted menu text with chart type descriptions
        """
        return (
            "🌟 Welcome to Natal Chart Bot!\n\n"
            "I can generate astrological charts for you. Choose what you'd like to create:\n\n"
            f"🔮 **{ChartSelection.NATAL.display_name}**\n"
            f"   {ChartSelection.NATAL.description}\n\n"
            f"💑 **{ChartSelection.COMPOSITE.display_name}**\n"
            f"   {ChartSelection.COMPOSITE.description}\n\n"
            "💡 Tap /help anytime for detailed instructions."
        )

    @staticmethod
    def get_state_hints(state: str) -> List[str]:
        """Get available commands and hints for current conversation state.

        Args:
            state: Current FSM state (e.g., 'chart_selection', 'date_entry', 'time_entry')

        Returns:
            List of command hints for display
        """
        hints_map = {
            "chart_selection": [
                "Choose chart type from the menu above",
                "/help - Learn about chart types",
                "/cancel - Cancel and start over",
            ],
            "name_entry": [
                "Enter the person's name (1-100 characters)",
                "Example: John Doe",
                "/cancel - Cancel chart generation",
            ],
            "date_entry": [
                "Enter birth date in one of these formats:",
                "  • DD.MM.YYYY (e.g., 15.05.1990)",
                "  • YYYY-MM-DD (e.g., 1990-05-15)",
                "  • Month DD, YYYY (e.g., May 15, 1990)",
                "/cancel - Cancel chart generation",
            ],
            "time_entry": [
                "Enter birth time in 24-hour format:",
                "  • HH:MM (e.g., 14:30 for 2:30 PM)",
                "  • HH:MM AM/PM (e.g., 2:30 PM)",
                "/cancel - Cancel chart generation",
            ],
            "location_entry": [
                "Enter birth location (city name):",
                "  • Include country for accuracy (e.g., London, UK)",
                "  • Use major cities if your town is small",
                "Example: New York, USA",
                "/cancel - Cancel chart generation",
            ],
            "generating": [
                "⏳ Generating your chart...",
                "This may take a few moments.",
            ],
        }

        return hints_map.get(state, ["/help - Get help", "/cancel - Cancel"])

    @staticmethod
    def get_help_documentation() -> str:
        """Get comprehensive help documentation for bot usage.

        Returns:
            Detailed help text with chart explanations and usage guide
        """
        return (
            "📚 **Natal Chart Bot - Help Documentation**\n\n"
            "**What is a Natal Chart?**\n"
            "A natal chart (birth chart) is a map of planetary positions at the exact moment "
            "and location of your birth. "
            "It's used in astrology to understand personality traits, life path, and potential.\n\n"
            "**What is a Composite Chart?**\n"
            "A composite chart combines two people's birth data to analyze relationship compatibility and dynamics. "
            "It shows how two individuals interact and what their relationship represents.\n\n"
            "**How to Use This Bot:**\n\n"
            "1️⃣ **Start**: Type /start and choose your chart type\n"
            "2️⃣ **Natal Chart**: Provide your birth information\n"
            "   • Name (any name for the chart)\n"
            "   • Birth date (e.g., 15.05.1990)\n"
            "   • Birth time (e.g., 14:30 or 2:30 PM)\n"
            "   • Birth location (e.g., New York, USA)\n\n"
            "3️⃣ **Composite Chart**: Provide birth data for two people\n"
            "   • Follow the same steps for both individuals\n\n"
            "4️⃣ **Receive Chart**: You'll get an SVG image of the chart\n\n"
            "**Supported Date Formats:**\n"
            "• DD.MM.YYYY (15.05.1990)\n"
            "• YYYY-MM-DD (1990-05-15)\n"
            "• Month DD, YYYY (May 15, 1990)\n\n"
            "**Supported Time Formats:**\n"
            "• 24-hour: HH:MM (14:30)\n"
            "• 12-hour: HH:MM AM/PM (2:30 PM)\n\n"
            "**Location Tips:**\n"
            "• Include country for best results (London, UK)\n"
            "• Use major cities if your town is small\n"
            "• Try nearby city if your location isn't found\n\n"
            "**Privacy & Data:**\n"
            "• Your data is only used for chart generation\n"
            "• No information is stored permanently\n"
            "• Sessions expire after 30 minutes of inactivity\n\n"
            "**Commands:**\n"
            "/start - Start chart generation\n"
            "/help - Show this help message\n"
            "/cancel - Cancel current chart generation\n\n"
            "Need assistance? Just type /help at any time!"
        )

    @staticmethod
    def get_chart_type_description(chart_type: ChartSelection) -> str:
        """Get detailed description for a specific chart type.

        Args:
            chart_type: Chart type to describe

        Returns:
            Detailed description of the chart type
        """
        descriptions = {
            ChartSelection.NATAL: (
                "**Natal Chart (Birth Chart)**\n\n"
                "Your natal chart is a snapshot of the sky at the exact "
                "moment you were born. It includes:\n"
                "• Sun, Moon, and Rising signs\n"
                "• Planetary positions in zodiac signs\n"
                "• House placements\n"
                "• Aspects between planets\n\n"
                "This chart is used to understand your personality, strengths, challenges, and life path."
            ),
            ChartSelection.COMPOSITE: (
                "**Composite Chart**\n\n"
                "A composite chart blends two people's birth charts into one, showing the relationship itself. "
                "It reveals:\n"
                "• How you interact as a couple\n"
                "• Relationship strengths and challenges\n"
                "• Purpose and dynamics of the relationship\n\n"
                "This chart is commonly used for romantic relationships, but works for any partnership "
                "(friendships, business partners, family members)."
            ),
        }

        return descriptions.get(chart_type, "Chart type description not available.")

    @staticmethod
    def get_error_recovery_hints() -> str:
        """Get hints for recovering from common errors.

        Returns:
            Error recovery guidance text
        """
        return (
            "⚠️ **Having trouble?**\n\n"
            "Common issues and solutions:\n\n"
            "❌ **Invalid date format**\n"
            "✅ Try: DD.MM.YYYY (15.05.1990) or YYYY-MM-DD (1990-05-15)\n\n"
            "❌ **Location not found**\n"
            "✅ Include country (London, UK) or try a major nearby city\n\n"
            "❌ **Invalid time**\n"
            "✅ Use 24-hour format (14:30) or 12-hour (2:30 PM)\n\n"
            "Need help? Type /help for detailed instructions.\n"
            "Want to start over? Type /cancel and then /start"
        )
