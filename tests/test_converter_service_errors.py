"""Tests for converter_service error handling to increase coverage."""

import pytest

from apisbot.services.converter_service import ConverterService


class TestConverterServiceErrors:
    """Test ConverterService error handling paths."""

    @pytest.mark.asyncio
    async def test_svg_to_png_with_mock_large_output(self):
        """Test handling of mock large PNG output."""
        # Create a small SVG
        svg_data = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
    <rect width="100" height="100" fill="blue"/>
</svg>"""

        # Patch cairosvg to return a large file
        import unittest.mock as mock

        with mock.patch("apisbot.services.converter_service.cairosvg.svg2png") as mock_svg2png:
            # Create a fake PNG that exceeds the size limit
            fake_large_png = b"PNG_HEADER" + (b"X" * (6 * 1024 * 1024))  # 6 MB
            mock_svg2png.return_value = fake_large_png

            with pytest.raises(ValueError, match="too large"):
                await ConverterService.svg_to_png(svg_data)

    @pytest.mark.asyncio
    async def test_svg_to_png_returns_none(self):
        """Test handling when cairosvg returns None."""
        import unittest.mock as mock

        svg_data = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
    <rect width="100" height="100" fill="red"/>
</svg>"""

        with mock.patch("apisbot.services.converter_service.cairosvg.svg2png") as mock_svg2png:
            mock_svg2png.return_value = None

            with pytest.raises(ValueError, match="conversion returned None"):
                await ConverterService.svg_to_png(svg_data)

    @pytest.mark.asyncio
    async def test_svg_to_png_cairosvg_exception(self):
        """Test handling of cairosvg exceptions."""
        import unittest.mock as mock

        svg_data = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
    <circle cx="50" cy="50" r="40" fill="green"/>
</svg>"""

        with mock.patch("apisbot.services.converter_service.cairosvg.svg2png") as mock_svg2png:
            mock_svg2png.side_effect = Exception("Cairo error")

            with pytest.raises(ValueError, match="Failed to convert chart to PNG"):
                await ConverterService.svg_to_png(svg_data)
