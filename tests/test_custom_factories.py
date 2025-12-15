"""Tests for custom chart data and aspects factories."""

from unittest.mock import MagicMock, patch

from apisbot.services.custom_aspects_factory import CustomAspectsFactory
from apisbot.services.custom_chart_data_factory import CustomChartDataFactory


class TestCustomFactories:
    """Test custom factories."""

    @patch("apisbot.services.custom_chart_data_factory.SingleChartDataModel")
    @patch("apisbot.services.custom_chart_data_factory.ChartDataFactory")
    @patch("apisbot.services.custom_chart_data_factory.CustomAspectsFactory")
    @patch("apisbot.services.custom_chart_data_factory.cast")
    def test_create_natal_chart_data_restricted(
        self, mock_cast, mock_aspects_factory, mock_base_factory, mock_single_model_class
    ):
        """Test creating natal chart data with sign restriction."""
        mock_subject = MagicMock()

        # Base data return
        mock_base_data = MagicMock()
        mock_base_factory.create_natal_chart_data.return_value = mock_base_data

        # Cast return (just return the same mock)
        mock_cast.side_effect = lambda t, x: x

        # Aspects return
        mock_custom_aspects = MagicMock()
        mock_aspects_factory.single_chart_aspects.return_value = mock_custom_aspects

        # Execute
        CustomChartDataFactory.create_natal_chart_data(subject=mock_subject, restrict_to_similar_signs=True)

        # Verify
        mock_base_factory.create_natal_chart_data.assert_called_once()
        mock_aspects_factory.single_chart_aspects.assert_called_once()
        mock_single_model_class.assert_called_once()  # Constructor called

    @patch("apisbot.services.custom_chart_data_factory.ChartDataFactory")
    def test_create_natal_chart_data_unrestricted(self, mock_base_factory):
        """Test creating natal chart data without restriction (pass-through)."""
        mock_subject = MagicMock()
        CustomChartDataFactory.create_natal_chart_data(subject=mock_subject, restrict_to_similar_signs=False)
        mock_base_factory.create_natal_chart_data.assert_called_once()

    @patch("kerykeion.schemas.kr_models.SingleChartAspectsModel")
    @patch("apisbot.services.custom_aspects_factory.AspectModel")
    @patch("apisbot.services.custom_aspects_factory.get_aspect_from_two_points_with_signs")
    @patch("apisbot.services.custom_aspects_factory.get_active_points_list")
    def test_single_chart_aspects(self, mock_get_points, mock_get_aspect, mock_aspect_model, mock_single_aspects_model):
        """Test single chart aspects generation."""
        mock_subject = MagicMock()
        mock_subject.name = "Test"

        # Setup points
        p1 = MagicMock()
        p1.name = "Sun"
        p1.abs_pos = 100.0
        p1.sign_num = 1

        p2 = MagicMock()
        p2.name = "Moon"
        p2.abs_pos = 120.0
        p2.sign_num = 2

        mock_get_points.return_value = [p1, p2]

        # Setup aspect decision
        mock_get_aspect.return_value = {
            "verdict": True,
            "name": "Conjunction",
            "orbit": 1.0,
            "aspect_degrees": 0,
            "diff": 0,
            "aid": 1,
        }

        CustomAspectsFactory.single_chart_aspects(mock_subject)

        mock_single_aspects_model.assert_called()
        mock_aspect_model.assert_called()
        mock_get_aspect.assert_called()

    @patch("kerykeion.schemas.kr_models.SingleChartAspectsModel")
    @patch("apisbot.services.custom_aspects_factory.AspectModel")
    @patch("apisbot.services.custom_aspects_factory.get_aspect_from_two_points_with_signs")
    @patch("apisbot.services.custom_aspects_factory.get_active_points_list")
    def test_single_chart_aspects_no_aspect(
        self, mock_get_points, mock_get_aspect, mock_aspect_model, mock_single_aspects_model
    ):
        """Test with no aspect found."""
        mock_subject = MagicMock()
        mock_get_points.return_value = [MagicMock(name="Sun"), MagicMock(name="Moon")]
        mock_get_aspect.return_value = {"verdict": False}

        CustomAspectsFactory.single_chart_aspects(mock_subject)

        # Should not create AspectModel
        mock_aspect_model.assert_not_called()
        mock_single_aspects_model.assert_called()
