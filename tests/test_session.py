"""Tests for UserSession model."""

from datetime import datetime, timedelta

from apisbot.models.birth_data import BirthData
from apisbot.models.chart_selection import ChartSelection
from apisbot.models.session import UserSession


class TestUserSession:
    """Test UserSession model."""

    def test_user_session_creation(self):
        """Test basic UserSession instantiation."""
        session = UserSession(user_id=12345)

        assert session.user_id == 12345
        assert session.chart_type is None
        assert session.person1_data is None
        assert session.person2_data is None
        assert session.timeout_seconds == 1800
        assert isinstance(session.created_at, datetime)
        assert isinstance(session.last_updated, datetime)

    def test_user_session_with_custom_timeout(self):
        """Test UserSession with custom timeout."""
        session = UserSession(user_id=12345, timeout_seconds=3600)

        assert session.timeout_seconds == 3600

    def test_update_activity(self):
        """Test updating last activity timestamp."""
        session = UserSession(user_id=12345)
        original_time = session.last_updated

        # Wait a tiny bit and update
        import time

        time.sleep(0.01)
        session.update_activity()

        assert session.last_updated > original_time

    def test_is_expired_not_expired(self):
        """Test is_expired returns False for recent session."""
        session = UserSession(user_id=12345)
        session.last_updated = datetime.now()

        assert not session.is_expired()

    def test_is_expired_expired(self):
        """Test is_expired returns True for old session."""
        session = UserSession(user_id=12345)
        # Set last_updated to 31 minutes ago (exceeds 30-minute default)
        session.last_updated = datetime.now() - timedelta(seconds=1860)

        assert session.is_expired()

    def test_is_expired_at_boundary(self):
        """Test is_expired at exact timeout boundary."""
        session = UserSession(user_id=12345)
        # Set last_updated to exactly 1800 seconds ago
        session.last_updated = datetime.now() - timedelta(seconds=1800)

        # At exact boundary (1800 seconds), code uses > so it IS expired
        assert session.is_expired()

    def test_is_expired_just_under_boundary(self):
        """Test is_expired just under timeout boundary."""
        session = UserSession(user_id=12345)
        # Set last_updated to 1799 seconds ago (just under)
        session.last_updated = datetime.now() - timedelta(seconds=1799)

        assert not session.is_expired()

    def test_is_complete_no_chart_type(self):
        """Test is_complete returns False when chart type not selected."""
        session = UserSession(user_id=12345)

        assert not session.is_complete()

    def test_is_complete_no_person1_data(self):
        """Test is_complete returns False when person1_data is missing."""
        session = UserSession(user_id=12345)
        session.chart_type = ChartSelection.NATAL

        assert not session.is_complete()

    def test_is_complete_natal_chart_incomplete_data(self):
        """Test is_complete returns False for natal chart with incomplete data."""
        from datetime import date, time

        session = UserSession(user_id=12345)
        session.chart_type = ChartSelection.NATAL
        session.person1_data = BirthData(
            name="John Doe",
            birth_date=date(1990, 5, 15),
            birth_time=time(14, 30),
            location="New York",
            # Missing geocoding data
        )

        assert not session.is_complete()

    def test_is_complete_natal_chart_complete_data(self):
        """Test is_complete returns True for natal chart with complete data."""
        from datetime import date, time

        session = UserSession(user_id=12345)
        session.chart_type = ChartSelection.NATAL
        session.person1_data = BirthData(
            name="John Doe",
            birth_date=date(1990, 5, 15),
            birth_time=time(14, 30),
            location="New York",
            latitude=40.7128,
            longitude=-74.0060,
            timezone="America/New_York",
        )

        assert session.is_complete()

    def test_is_complete_composite_chart_no_person2(self):
        """Test is_complete returns False for composite chart without person2_data."""
        from datetime import date, time

        session = UserSession(user_id=12345)
        session.chart_type = ChartSelection.COMPOSITE
        session.person1_data = BirthData(
            name="Person One",
            birth_date=date(1990, 5, 15),
            birth_time=time(14, 30),
            location="New York",
            latitude=40.7128,
            longitude=-74.0060,
            timezone="America/New_York",
        )

        assert not session.is_complete()

    def test_is_complete_composite_chart_incomplete_person2(self):
        """Test is_complete returns False for composite chart with incomplete person2_data."""
        from datetime import date, time

        session = UserSession(user_id=12345)
        session.chart_type = ChartSelection.COMPOSITE
        session.person1_data = BirthData(
            name="Person One",
            birth_date=date(1990, 5, 15),
            birth_time=time(14, 30),
            location="New York",
            latitude=40.7128,
            longitude=-74.0060,
            timezone="America/New_York",
        )
        session.person2_data = BirthData(
            name="Person Two",
            birth_date=date(1985, 12, 25),
            birth_time=time(8, 0),
            location="London",
            # Missing geocoding data
        )

        assert not session.is_complete()

    def test_is_complete_composite_chart_complete_data(self):
        """Test is_complete returns True for composite chart with complete data."""
        from datetime import date, time

        session = UserSession(user_id=12345)
        session.chart_type = ChartSelection.COMPOSITE
        session.person1_data = BirthData(
            name="Person One",
            birth_date=date(1990, 5, 15),
            birth_time=time(14, 30),
            location="New York",
            latitude=40.7128,
            longitude=-74.0060,
            timezone="America/New_York",
        )
        session.person2_data = BirthData(
            name="Person Two",
            birth_date=date(1985, 12, 25),
            birth_time=time(8, 0),
            location="London",
            latitude=51.5074,
            longitude=-0.1278,
            timezone="Europe/London",
        )

        assert session.is_complete()

    def test_clear_session(self):
        """Test clearing session data."""
        from datetime import date, time

        session = UserSession(user_id=12345)
        session.chart_type = ChartSelection.NATAL
        session.person1_data = BirthData(
            name="John Doe",
            birth_date=date(1990, 5, 15),
            birth_time=time(14, 30),
            location="New York",
        )
        original_last_updated = session.last_updated

        # Clear session
        import time as time_module

        time_module.sleep(0.01)
        session.clear()

        # Verify all data cleared
        assert session.chart_type is None
        assert session.person1_data is None
        assert session.person2_data is None
        assert session.last_updated > original_last_updated

    def test_clear_session_composite(self):
        """Test clearing composite chart session data."""
        from datetime import date, time

        session = UserSession(user_id=12345)
        session.chart_type = ChartSelection.COMPOSITE
        session.person1_data = BirthData(
            name="Person One",
            birth_date=date(1990, 5, 15),
            birth_time=time(14, 30),
            location="New York",
        )
        session.person2_data = BirthData(
            name="Person Two",
            birth_date=date(1985, 12, 25),
            birth_time=time(8, 0),
            location="London",
        )

        session.clear()

        # Verify all data cleared
        assert session.chart_type is None
        assert session.person1_data is None
        assert session.person2_data is None
