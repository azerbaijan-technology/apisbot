# -*- coding: utf-8 -*-
from kerykeion.chart_data_factory import ChartDataFactory
from custom_aspects_factory import CustomAspectsFactory
from kerykeion.schemas.kr_models import AstrologicalSubjectModel, SingleChartDataModel
from kerykeion.schemas import ActiveAspect
from kerykeion.schemas.kr_literals import AstrologicalPoint
from typing import Optional, List, Mapping

class CustomChartDataFactory(ChartDataFactory):
    @staticmethod
    def create_natal_chart_data(
        subject: AstrologicalSubjectModel,
        active_points: Optional[List[AstrologicalPoint]] = None,
        active_aspects: List[ActiveAspect] = None,
        *,
        restrict_to_similar_signs: bool = False,
        **kwargs
    ) -> SingleChartDataModel:
        
        # Вызываем оригинальный метод, но с заменой фабрики аспектов
        from kerykeion.aspects import AspectsFactory
        
        # Сохраняем оригинальный метод
        original = AspectsFactory.single_chart_aspects
        # Заменяем на кастомный
        AspectsFactory.single_chart_aspects = CustomAspectsFactory.single_chart_aspects
        
        try:
            result = ChartDataFactory.create_natal_chart_data(
                subject,
                active_points=active_points,
                active_aspects=active_aspects,
                **kwargs
            )
            # Если restrict_to_similar_signs=True, пересчитываем аспекты
            if restrict_to_similar_signs:
                aspects_model = CustomAspectsFactory.single_chart_aspects(
                    subject,
                    active_points=active_points,
                    active_aspects=active_aspects,
                    restrict_to_similar_signs=True,
                )
                result = SingleChartDataModel(
                    chart_type="Natal",
                    subject=subject,
                    aspects=aspects_model.aspects,
                    element_distribution=result.element_distribution,
                    quality_distribution=result.quality_distribution,
                    active_points=result.active_points,
                    active_aspects=result.active_aspects,
                )
        finally:
            # Восстанавливаем оригинал
            AspectsFactory.single_chart_aspects = original
        
        return result