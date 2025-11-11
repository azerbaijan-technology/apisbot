# -*- coding: utf-8 -*-
from typing import List, Optional, Union
from kerykeion.aspects.aspects_utils import get_active_points_list, calculate_aspect_movement
from custom_aspects_utils import get_aspect_from_two_points_with_signs
from kerykeion.schemas.kr_models import AspectModel, ActiveAspect, AstrologicalSubjectModel
from kerykeion.settings.chart_defaults import DEFAULT_CELESTIAL_POINTS_SETTINGS, DEFAULT_CHART_ASPECTS_SETTINGS
from kerykeion.settings.config_constants import DEFAULT_ACTIVE_ASPECTS
from kerykeion.utilities import find_common_active_points
from kerykeion.aspects.aspects_factory import AspectsFactory

class CustomAspectsFactory:
    @staticmethod
    def single_chart_aspects(
        subject: AstrologicalSubjectModel,
        *,
        active_points: Optional[List[str]] = None,
        active_aspects: Optional[List[ActiveAspect]] = None,
        axis_orb_limit: Optional[float] = None,
        restrict_to_similar_signs: bool = False,
    ):
        from kerykeion.schemas.kr_models import SingleChartAspectsModel
        
        celestial_points = DEFAULT_CELESTIAL_POINTS_SETTINGS
        aspects_settings = DEFAULT_CHART_ASPECTS_SETTINGS
        active_aspects_resolved = active_aspects or DEFAULT_ACTIVE_ASPECTS

        effective = active_points or subject.active_points
        if active_points:
            effective = find_common_active_points(subject.active_points, active_points)

        points = get_active_points_list(subject, effective)
        
        planet_id_lookup = {p["name"]: p["id"] for p in celestial_points}
        filtered_settings = AspectsFactory._update_aspect_settings(aspects_settings, active_aspects_resolved)

        all_aspects = []
        opposite_pairs = {
            ("Ascendant", "Descendant"), ("Descendant", "Ascendant"),
            ("Medium_Coeli", "Imum_Coeli"), ("Imum_Coeli", "Medium_Coeli"),
            ("True_North_Lunar_Node", "True_South_Lunar_Node"),
            ("Mean_North_Lunar_Node", "Mean_South_Lunar_Node"),
        }

        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                p1 = points[i]
                p2 = points[j]
                
                if (p1.name, p2.name) in opposite_pairs:
                    continue

                p1_sign = getattr(p1, "sign_num", None) if restrict_to_similar_signs else None
                p2_sign = getattr(p2, "sign_num", None) if restrict_to_similar_signs else None

                asp = get_aspect_from_two_points_with_signs(
                    filtered_settings,
                    p1.abs_pos,
                    p2.abs_pos,
                    p1_sign=p1_sign,
                    p2_sign=p2_sign,
                    check_signs=restrict_to_similar_signs and p1_sign is not None,
                )

                if asp["verdict"]:
                    all_aspects.append(
                        AspectModel(
                            p1_name=p1.name,
                            p1_owner=subject.name,
                            p1_abs_pos=p1.abs_pos,
                            p2_name=p2.name,
                            p2_owner=subject.name,
                            p2_abs_pos=p2.abs_pos,
                            aspect=asp["name"],
                            orbit=asp["orbit"],
                            aspect_degrees=asp["aspect_degrees"],
                            diff=asp["diff"],
                            p1=planet_id_lookup.get(p1.name, 0),
                            p2=planet_id_lookup.get(p2.name, 0),
                            aspect_movement=calculate_aspect_movement(
                                p1.abs_pos, p2.abs_pos, asp["aspect_degrees"]
                            ),
                        )
                    )

        filtered = AspectsFactory._filter_relevant_aspects(
            all_aspects, axis_orb_limit, apply_axis_orb_filter=axis_orb_limit is not None
        )

        return SingleChartAspectsModel(
            subject=subject,
            aspects=filtered,
            active_points=effective,
            active_aspects=active_aspects_resolved,
        )