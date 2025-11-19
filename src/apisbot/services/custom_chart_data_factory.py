# -*- coding: utf-8 -*-
"""
Custom chart data factory with optional sign similarity filtering for aspects.
"""

from typing import List, Optional, Union, cast

from kerykeion.chart_data_factory import ChartDataFactory
from kerykeion.schemas import ActiveAspect
from kerykeion.schemas.kr_literals import AstrologicalPoint
from kerykeion.schemas.kr_models import (
    AstrologicalSubjectModel,
    ChartDataModel,
    CompositeSubjectModel,
    PlanetReturnModel,
    SingleChartDataModel,
)

from .custom_aspects_factory import CustomAspectsFactory

# Common type for all astrological subjects
SubjectType = Union[
    AstrologicalSubjectModel,
    CompositeSubjectModel,
    PlanetReturnModel,
]


class CustomChartDataFactory(ChartDataFactory):
    """
    Factory for creating natal chart data with optional aspect filtering
    based on sign similarity (Fire with Fire, Earth with Earth, etc.).
    """

    @staticmethod
    def create_natal_chart_data(
        subject: SubjectType,
        active_points: Optional[List[AstrologicalPoint]] = None,
        active_aspects: Optional[List[ActiveAspect]] = None,
        *,
        restrict_to_similar_signs: bool = False,
        **kwargs,
    ) -> ChartDataModel:
        """
        Creates natal chart data with the option to restrict aspects to planets
        in similar element signs (Fire, Earth, Air, Water).

        Args:
            subject: The astrological subject to create chart data for
            active_points: List of celestial points to include in calculations
            active_aspects: List of active aspects with their orb settings
            restrict_to_similar_signs: If True, only aspects between planets
                in the same element sign are retained
            **kwargs: Additional parameters for parent class compatibility

        Returns:
            SingleChartDataModel containing the calculated chart data
        """

        # If no special filtering is needed, simply delegate to parent
        if not restrict_to_similar_signs:
            return ChartDataFactory.create_natal_chart_data(
                subject=subject,
                active_points=active_points,
                active_aspects=cast(List[ActiveAspect], active_aspects),
                **kwargs,
            )

        # === RECOMPOSITION PATTERN ===
        # 1. First get the base data (with default aspects) from parent
        # This gives us element_distribution, quality_distribution, etc.
        # without recalculating them manually
        base_data = ChartDataFactory.create_natal_chart_data(
            subject=subject,
            active_points=active_points,
            active_aspects=cast(List[ActiveAspect], active_aspects),
            **kwargs,
        )

        # 2. Cast to the specific type we know it is for a natal chart
        # (This is safe because we called create_natal_chart_data)
        base_single_chart = cast(SingleChartDataModel, base_data)

        # 3. Recalculate aspects with our custom filter
        custom_aspects_model = CustomAspectsFactory.single_chart_aspects(
            subject=subject,
            active_points=base_single_chart.active_points,
            active_aspects=base_single_chart.active_aspects,
            restrict_to_similar_signs=True,
        )

        # 4. Create new model reusing ALL parent's calculations
        # except for the aspects, which we replace with our filtered ones
        return SingleChartDataModel(
            chart_type=base_single_chart.chart_type,
            subject=base_single_chart.subject,
            aspects=custom_aspects_model.aspects,  # Only this is custom
            element_distribution=base_single_chart.element_distribution,  # Reused
            quality_distribution=base_single_chart.quality_distribution,  # Reused
            active_points=base_single_chart.active_points,
            active_aspects=base_single_chart.active_aspects,
        )
