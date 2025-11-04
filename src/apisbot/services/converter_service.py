import logging

import cairosvg

logger = logging.getLogger(__name__)


class ConverterService:
    """Service for converting SVG charts to PNG format.

    Uses cairosvg for conversion. Provides error handling and
    size validation (PNG must be under 5 MB).
    """

    MAX_SIZE_MB = 5
    MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024

    @staticmethod
    async def svg_to_png(svg_data: str, dpi: int = 150) -> bytes:
        """Convert SVG chart to PNG bytes.

        Args:
            svg_data: SVG chart as string
            dpi: Resolution for PNG output (default: 150)

        Returns:
            PNG image as bytes

        Raises:
            ValueError: If conversion fails or resulting PNG is too large
        """
        try:
            logger.info("Converting SVG to PNG")

            # Convert SVG to PNG
            png_bytes = cairosvg.svg2png(
                bytestring=svg_data.encode("utf-8"),
                dpi=dpi,
            )

            if png_bytes is None:
                raise ValueError("Failed to convert SVG to PNG: conversion returned None")

            # Validate size
            size_mb = len(png_bytes) / (1024 * 1024)

            if len(png_bytes) > ConverterService.MAX_SIZE_BYTES:
                logger.error(f"PNG size {size_mb:.2f} MB exceeds limit of {ConverterService.MAX_SIZE_MB} MB")
                raise ValueError(
                    f"Generated chart is too large ({size_mb:.2f} MB). "
                    f"Maximum size is {ConverterService.MAX_SIZE_MB} MB."
                )

            logger.info(f"Conversion successful, size: {size_mb:.2f} MB")
            return png_bytes

        except Exception as e:
            if isinstance(e, ValueError):
                raise

            logger.error(f"SVG to PNG conversion failed: {type(e).__name__}: {str(e)}")
            raise ValueError(f"Failed to convert chart to PNG: {str(e)}") from e
