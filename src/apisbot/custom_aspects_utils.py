# -*- coding: utf-8 -*-
from typing import Union, Optional
from swisseph import difdeg2n

def _min_sign_diff(p1_sign: int, p2_sign: int) -> int:
    diff = abs(p1_sign - p2_sign)
    return diff if diff <= 6 else 12 - diff

def get_aspect_from_two_points_with_signs(
    aspects_settings: list[dict],
    point_one: Union[float, int],
    point_two: Union[float, int],
    *,
    p1_sign: Optional[int] = None,
    p2_sign: Optional[int] = None,
    check_signs: bool = False,
) -> dict:
    """Расчёт аспекта с опциональной проверкой знаков."""
    distance = abs(difdeg2n(point_one, point_two))
    diff = abs(point_one - point_two)

    for aid, aspect in enumerate(aspects_settings):
        deg = aspect["degree"]
        orb = aspect["orb"]

        if (deg - orb) <= int(distance) <= (deg + orb):
            name = aspect["name"]

            if check_signs and p1_sign is not None and p2_sign is not None:
                d = _min_sign_diff(p1_sign, p2_sign)

                if name == "conjunction" and d != 0: continue
                if name == "opposition"  and d != 6: continue
                if name == "square"      and d != 3: continue
                if name == "trine"       and d != 4: continue
                if name == "sextile"     and d != 2: continue

            return {
                "verdict": True,
                "name": name,
                "orbit": abs(distance - deg),
                "aspect_degrees": deg,
                "diff": diff,
                "aid": aid,
            }

    return {"verdict": False, "name": None, "orbit": 0, "aspect_degrees": 0, "diff": diff, "aid": None}