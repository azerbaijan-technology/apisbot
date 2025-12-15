"""Tests for custom services and utilities."""

from unittest.mock import MagicMock, patch

from apisbot.services.custom_aspects_utils import _min_sign_diff, get_aspect_from_two_points_with_signs
from apisbot.services.custom_chart_drawer import CustomChartDrawer


class TestCustomAspectsUtils:
    """Test custom aspects utilities."""

    def test_min_sign_diff(self):
        """Test sign difference calculation."""
        assert _min_sign_diff(1, 2) == 1
        assert _min_sign_diff(1, 12) == 1
        assert _min_sign_diff(1, 7) == 6
        assert _min_sign_diff(2, 5) == 3

    def test_get_aspect_basic(self):
        """Test basic aspect detection."""
        settings = [{"name": "conjunction", "degree": 0, "orb": 10}]

        # Conjunction at 0 diff
        result = get_aspect_from_two_points_with_signs(settings, 100, 100)
        assert result["verdict"] is True
        assert result["name"] == "conjunction"

        # No aspect
        result = get_aspect_from_two_points_with_signs(settings, 100, 150)
        assert result["verdict"] is False

    def test_get_aspect_with_signs(self):
        """Test aspect detection with sign constraints."""
        settings = [{"name": "conjunction", "degree": 0, "orb": 10}]

        # Conjunction across sign boundary (e.g. 29 deg and 1 deg of next sign)
        # Should be filtered out if we strictly check sign diff for conjunction == 0

        # Same sign conjunction (diff 0) -> OK
        result = get_aspect_from_two_points_with_signs(settings, 10, 12, p1_sign=1, p2_sign=1, check_signs=True)
        assert result["verdict"] is True

        # Should fail with check_signs=True
        result = get_aspect_from_two_points_with_signs(settings, 29, 31, p1_sign=1, p2_sign=2, check_signs=True)
        assert result["verdict"] is False

    def test_get_aspect_all_types(self):
        """Test all aspect types with sign logic."""
        settings = [
            {"name": "conjunction", "degree": 0, "orb": 10},
            {"name": "opposition", "degree": 180, "orb": 10},
            {"name": "square", "degree": 90, "orb": 10},
            {"name": "trine", "degree": 120, "orb": 10},
            {"name": "sextile", "degree": 60, "orb": 10},
        ]

        # Valid cases
        cases_ok = [
            (0, 0, "conjunction", 1, 1),
            (0, 180, "opposition", 1, 7),
            (0, 90, "square", 1, 4),
            (0, 120, "trine", 1, 5),
            (0, 60, "sextile", 1, 3),
        ]
        for p1, p2, name, s1, s2 in cases_ok:
            res = get_aspect_from_two_points_with_signs(settings, p1, p2, p1_sign=s1, p2_sign=s2, check_signs=True)
            assert res["verdict"] is True
            assert res["name"] == name

        # Invalid cases (wrong signs despite correct angle orb)
        cases_bad = [
            (0, 5, "conjunction", 1, 2),  # Orb ok, sign diff 1 (!=0)
            (0, 175, "opposition", 1, 6),  # Orb ok, sign diff 5 (!=6)
            (0, 95, "square", 1, 3),  # Orb ok, sign diff 2 (!=3)
            (0, 125, "trine", 1, 6),  # Orb ok, sign diff 5 (!=4)
            (0, 65, "sextile", 1, 2),  # Orb ok, sign diff 1 (!=2)
        ]
        for p1, p2, name, s1, s2 in cases_bad:
            res = get_aspect_from_two_points_with_signs(settings, p1, p2, p1_sign=s1, p2_sign=s2, check_signs=True)
            if res["verdict"]:
                # If verdict is True, ensure it's NOT the aspect we are checking against
                pass
            # Actually, get_aspect returns the first matching aspect.
            # If we enforce signs, it should skip the mismatched one and return verdict=False (if no other matches)

            # For these specific numbers, they match the degree+-orb.
            # So if sign check fails, it should execute 'continue' and eventually return False.
            assert res["verdict"] is False


class TestCustomChartDrawer:
    """Test CustomChartDrawer."""

    @patch("apisbot.services.custom_chart_drawer.ChartDrawer.__init__")
    def test_init_themes(self, mock_super_init):
        """Test initialization with custom and standard themes."""
        # Set return_value to None so init doesn't fail
        mock_super_init.return_value = None

        # Test valid standard theme
        mock_chart_data = MagicMock()
        with patch("apisbot.services.custom_chart_drawer.ChartDrawer.__init__", return_value=None) as mock_init_2:
            CustomChartDrawer(mock_chart_data, theme="dark")
            mock_init_2.assert_called_with(mock_chart_data, theme="dark")

        # Test custom theme
        mock_chart_data_2 = MagicMock()
        with patch("apisbot.services.custom_chart_drawer.ChartDrawer.__init__", return_value=None) as mock_init_3:
            CustomChartDrawer(mock_chart_data_2, theme="my_custom_theme")
            mock_init_3.assert_called_with(mock_chart_data_2, theme=None)

    @patch("apisbot.services.custom_chart_drawer.ChartDrawer.set_up_theme")
    @patch("apisbot.services.custom_chart_drawer.Path")
    @patch("builtins.open")
    def test_set_up_theme_custom(self, mock_open, mock_path, mock_super_setup):
        """Test loading a custom theme."""
        mock_file = MagicMock()
        mock_file.exists.return_value = True
        mock_path.return_value.parent.parent.__truediv__.return_value.__truediv__.return_value = mock_file

        mock_open.return_value.__enter__.return_value.read.return_value = "css data"

        # CustomChartDrawer instance with mocked superclass components
        # We need to manually set attributes that __init__ would set if we weren't mocking it entirely
        # OR we can let __init__ run partially.
        # Easier: Mock the class instance itself or ensure __init__ runs on a partial mock.

        # Actually, let's just instantiate it, but since __init__ calls super().__init__,
        # we need to be careful. The previous test mocked __init__, here we might need to let it run
        # but mock the super call inside it?

        with patch("apisbot.services.custom_chart_drawer.ChartDrawer.__init__", return_value=None):
            drawer = CustomChartDrawer(MagicMock(), theme="custom")
            drawer._custom_theme = "custom"  # Set manually as we mocked init

        drawer.set_up_theme()

        assert drawer.color_style_tag == "css data"
        mock_super_setup.assert_not_called()

    @patch("apisbot.services.custom_chart_drawer.ChartDrawer.set_up_theme")
    def test_set_up_theme_fallback(self, mock_super_setup):
        """Test fallback to standard theme setup."""
        with patch("apisbot.services.custom_chart_drawer.ChartDrawer.__init__", return_value=None):
            drawer = CustomChartDrawer(MagicMock(), theme="dark")
            drawer._custom_theme = "dark"  # Set manually

        drawer.set_up_theme()
        mock_super_setup.assert_called()

    @patch("apisbot.services.custom_chart_drawer.sliceToX", return_value=10)
    @patch("apisbot.services.custom_chart_drawer.sliceToY", return_value=10)
    def test_custom_draw_zodiac_slice(self, mock_y, mock_x):
        """Test custom zodiac slice drawing logic."""
        with patch("apisbot.services.custom_chart_drawer.ChartDrawer.__init__", return_value=None):
            drawer = CustomChartDrawer(MagicMock(), theme="dark")

        # Test normal chart type
        result = drawer._custom_draw_zodiac_slice(
            c1=0, chart_type="Natal", seventh_house_degree_ut=180, num=1, r=100, style="style", type="Aries"
        )
        assert "translate(-16,-16)" in result

        # Test Transit chart type (should allow 0 dropin for slice path but different for symbol)
        result_transit = drawer._custom_draw_zodiac_slice(
            c1=0, chart_type="Transit", seventh_house_degree_ut=180, num=1, r=100, style="style", type="Aries"
        )
        assert result_transit != result

    @patch("apisbot.services.custom_chart_drawer.get_args")
    def test_draw_zodiac_circle_slices(self, mock_get_args):
        """Test the loop for drawing zodiac slices."""
        mock_get_args.return_value = ("Aries", "Taurus")  # Mock 2 signs

        with patch("apisbot.services.custom_chart_drawer.ChartDrawer.__init__", return_value=None):
            drawer = CustomChartDrawer(MagicMock(), theme="dark")

        # Setup drawer attributes needed for the loop
        drawer.first_circle_radius = 100
        drawer.chart_type = "Natal"
        drawer.first_obj = MagicMock()
        drawer.first_obj.seventh_house.abs_pos = 180
        drawer.chart_colors_settings = {"zodiac_bg_0": "#000", "zodiac_bg_1": "#fff"}

        # Mock the single slice drawer to avoid complexity
        with patch.object(drawer, "_custom_draw_zodiac_slice", return_value="<path/>") as mock_single:
            output = drawer._draw_zodiac_circle_slices(r=200)

            assert output == "<path/><path/>"
            assert mock_single.call_count == 2
            mock_single.assert_any_call(
                c1=100,
                chart_type="Natal",
                seventh_house_degree_ut=180,
                num=0,
                r=200,
                style="fill:#000; fill-opacity: 0.5;",
                type="Aries",
            )
