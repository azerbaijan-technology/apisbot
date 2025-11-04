"""Tests for converter_service."""

import pytest

from apisbot.services.converter_service import ConverterService


class TestConverterService:
    """Test ConverterService SVG to PNG conversion."""

    @pytest.mark.asyncio
    async def test_svg_to_png_success(self):
        """Test successful SVG to PNG conversion."""
        # Simple valid SVG
        svg_data = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
    <circle cx="50" cy="50" r="40" fill="blue"/>
</svg>"""

        png_bytes = await ConverterService.svg_to_png(svg_data)

        assert isinstance(png_bytes, bytes)
        assert len(png_bytes) > 0
        # PNG files start with specific magic bytes
        assert png_bytes[:8] == b"\x89PNG\r\n\x1a\n"

    @pytest.mark.asyncio
    async def test_svg_to_png_custom_dpi(self):
        """Test SVG to PNG conversion with custom DPI."""
        svg_data = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
    <rect width="100" height="100" fill="red"/>
</svg>"""

        # Lower DPI should result in smaller file
        png_low_dpi = await ConverterService.svg_to_png(svg_data, dpi=72)
        png_high_dpi = await ConverterService.svg_to_png(svg_data, dpi=300)

        assert isinstance(png_low_dpi, bytes)
        assert isinstance(png_high_dpi, bytes)
        # Both should be valid PNGs
        assert png_low_dpi[:8] == b"\x89PNG\r\n\x1a\n"
        assert png_high_dpi[:8] == b"\x89PNG\r\n\x1a\n"

    @pytest.mark.asyncio
    async def test_svg_to_png_size_validation(self):
        """Test that size limit constant is properly configured."""
        # Verify the size limit constants
        assert ConverterService.MAX_SIZE_MB == 5
        assert ConverterService.MAX_SIZE_BYTES == 5 * 1024 * 1024

        # Note: Actual size validation depends on cairosvg output which is hard to predict
        # The converter will check size and raise ValueError if > 5MB

    @pytest.mark.asyncio
    async def test_svg_to_png_invalid_svg(self):
        """Test handling of invalid SVG input."""
        invalid_svg = "This is not SVG"

        with pytest.raises(ValueError, match="Failed to convert"):
            await ConverterService.svg_to_png(invalid_svg)

    @pytest.mark.asyncio
    async def test_svg_to_png_empty_svg(self):
        """Test handling of empty SVG."""
        with pytest.raises(ValueError):
            await ConverterService.svg_to_png("")

    @pytest.mark.asyncio
    async def test_svg_to_png_complex_chart(self):
        """Test conversion of a more complex SVG similar to natal charts."""
        # More complex SVG with paths and text
        svg_data = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800" viewBox="0 0 800 800">
    <circle cx="400" cy="400" r="350" fill="none" stroke="black" stroke-width="2"/>
    <line x1="400" y1="50" x2="400" y2="750" stroke="black" stroke-width="1"/>
    <line x1="50" y1="400" x2="750" y2="400" stroke="black" stroke-width="1"/>
    <text x="400" y="30" text-anchor="middle" font-size="20">Test Chart</text>
    <path d="M 400 400 L 600 200 A 200 200 0 0 1 600 600 Z" fill="lightblue" opacity="0.5"/>
</svg>"""

        png_bytes = await ConverterService.svg_to_png(svg_data)

        assert isinstance(png_bytes, bytes)
        assert len(png_bytes) > 1000  # Should be substantial
        assert png_bytes[:8] == b"\x89PNG\r\n\x1a\n"

    @pytest.mark.asyncio
    async def test_max_size_constants(self):
        """Test that MAX_SIZE constants are set correctly."""
        assert ConverterService.MAX_SIZE_MB == 5
        assert ConverterService.MAX_SIZE_BYTES == 5 * 1024 * 1024
