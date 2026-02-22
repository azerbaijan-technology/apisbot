from pathlib import Path
from typing import Optional, Union, get_args

from kerykeion.charts.chart_drawer import ChartDrawer
import kerykeion.charts.chart_drawer
from kerykeion.charts.charts_utils import sliceToX, sliceToY, degreeDiff
from kerykeion.schemas import ChartType, Sign, KerykeionException

# Список встроенных тем (копия из KerykeionChartTheme)
VALID_THEMES = ["light", "dark", "dark-high-contrast", "classic", "strawberry", "black-and-white"]


class CustomChartDrawer(ChartDrawer):
    def __init__(self, chart_data, *, theme: Optional[str] = None, **kwargs):  # Принимаем любую строку
        # Сохраняем тему для кастомной загрузки
        self._custom_theme = theme

        # Определяем стандартную тему (если указана)
        standard_theme = theme if theme in VALID_THEMES else None

        # Вызываем родительский конструктор с правильным типом
        super().__init__(chart_data, theme=standard_theme, **kwargs)  # type: ignore

    def set_up_theme(self, theme=None):  # type: ignore[override]
        """Загрузка темы: сначала ищем кастомную, потом стандартную."""

        # Пробуем загрузить кастомную тему
        if self._custom_theme is not None:
            custom_theme_dir = Path(__file__).parent.parent / "themes"
            theme_file = custom_theme_dir / f"{self._custom_theme}.css"

            if theme_file.exists():
                with open(theme_file, "r", encoding="utf-8") as f:
                    self.color_style_tag = f.read()
                    return

        # Если кастомной нет, используем стандартный механизм
        super().set_up_theme(theme)

    def _custom_draw_zodiac_slice(
        self,
        c1: Union[int, float],
        chart_type: ChartType,
        seventh_house_degree_ut: Union[int, float],
        num: int,
        r: Union[int, float],
        style: str,
        type: str,
    ) -> str:
        """Draws a zodiac slice based on the given parameters.

        Custom version that removes the +15 degree offset for symbols.
        """

        # pie slices
        offset = 360 - seventh_house_degree_ut
        # check transit
        if chart_type == "Transit" or chart_type == "Synastry" or chart_type == "DualReturnChart":
            dropin: Union[int, float] = 0
        else:
            dropin = c1

        slice_path = (
            f'<path d="M{str(r)},{str(r)} '
            f"L{str(dropin + sliceToX(num, r - dropin, offset))},{str(dropin + sliceToY(num, r - dropin, offset))} "
            f"A{str(r - dropin)},{str(r - dropin)} 0 0,0 "
            f"{str(dropin + sliceToX(num + 1, r - dropin, offset))},"
            f'{str(dropin + sliceToY(num + 1, r - dropin, offset))} z" style="{style}"/>'
        )

        # symbols
        offset = offset  # <-- REMOVED to fix alignment
        offset = offset + 15
        # check transit
        if chart_type == "Transit" or chart_type == "Synastry" or chart_type == "DualReturnChart":
            dropin = 54
        else:
            dropin = 18 + c1

        # Scale glyphs
        glyph_scale = 0.5
        half_size = 16 * glyph_scale
        x_pos = dropin + sliceToX(num, r - dropin, offset)
        y_pos = dropin + sliceToY(num, r - dropin, offset)

        sign = (
            f'<g transform="translate({x_pos},{y_pos}) scale({glyph_scale}) translate(-16, -16)">'
            f'<use xlink:href="#{type}" /></g>'
        )

        return slice_path + "" + sign


    def _draw_zodiac_circle_slices(self, r):
        """
        Draw zodiac circle slices for each sign.
        Overridden to use _custom_draw_zodiac_slice.
        """
        sings = get_args(Sign)
        output = ""
        for i, sing in enumerate(sings):
            output += self._custom_draw_zodiac_slice(
                c1=self.first_circle_radius,
                chart_type=self.chart_type,
                seventh_house_degree_ut=self.first_obj.seventh_house.abs_pos,
                num=i,
                r=r,
                style=f'fill:{self.chart_colors_settings[f"zodiac_bg_{i}"]}; fill-opacity: 0.5;',
                type=sing,
            )

        return output


# --- Monkeypatching Kerykeion chart generation ---

# Define desired stroke width for rings
CUSTOM_RING_WIDTH = "1.5px"

def _patched_draw_first_circle(
    r: Union[int, float], stroke_color: str, chart_type: ChartType, c1: Union[int, float, None] = None
) -> str:
    """Patched draw_first_circle with custom stroke width."""
    # Note: stroke-width changed from 1px to CUSTOM_RING_WIDTH
    if chart_type == "Synastry" or chart_type == "Transit" or chart_type == "DualReturnChart":
        return f'<circle cx="{r}" cy="{r}" r="{r - 36}" style="fill: none; stroke: {stroke_color}; stroke-width: {CUSTOM_RING_WIDTH}; stroke-opacity:.4;" />'
    else:
        if c1 is None:
            raise KerykeionException("c1 is None")

        return (
            f'<circle cx="{r}" cy="{r}" r="{r - c1}" style="fill: none; stroke: {stroke_color}; stroke-width: {CUSTOM_RING_WIDTH}; " />'
        )

def _patched_draw_second_circle(
    r: Union[int, float], stroke_color: str, fill_color: str, chart_type: ChartType, c2: Union[int, float, None] = None
) -> str:
    """Patched draw_second_circle with custom stroke width."""
    # Note: stroke-width changed from 1px to CUSTOM_RING_WIDTH
    if chart_type == "Synastry" or chart_type == "Transit" or chart_type == "DualReturnChart":
        # Synastry/Transit has opacity .4
        return f'<circle cx="{r}" cy="{r}" r="{r - 72}" style="fill: {fill_color}; fill-opacity:.4; stroke: {stroke_color}; stroke-opacity:.4; stroke-width: {CUSTOM_RING_WIDTH}" />'
    else:
        if c2 is None:
            raise KerykeionException("c2 is None")

        # Natal/Composite has fill-opacity .2 and stroke-opacity .4
        # We set stroke-opacity explicitly to check visibility
        return f'<circle cx="{r}" cy="{r}" r="{r - c2}" style="fill: {fill_color}; fill-opacity:.2; stroke: {stroke_color}; stroke-opacity:1; stroke-width: {CUSTOM_RING_WIDTH}" />'

def _patched_draw_third_circle(
    radius: Union[int, float],
    stroke_color: str,
    fill_color: str,
    chart_type: ChartType,
    c3: Union[int, float]
) -> str:
    """Patched draw_third_circle with custom stroke width."""
    # Note: stroke-width changed from 1px to CUSTOM_RING_WIDTH
    if chart_type in {"Synastry", "Transit", "DualReturnChart"}:
         return f'<circle cx="{radius}" cy="{radius}" r="{radius - 160}" style="fill: {fill_color}; fill-opacity:.8; stroke: {stroke_color}; stroke-width: {CUSTOM_RING_WIDTH}" />'
    else:
        return f'<circle cx="{radius}" cy="{radius}" r="{radius - c3}" style="fill: {fill_color}; fill-opacity:.8; stroke: {stroke_color}; stroke-width: {CUSTOM_RING_WIDTH}" />'


def _patched_draw_degree_ring(
    r: Union[int, float], c1: Union[int, float], seventh_house_degree_ut: Union[int, float], stroke_color: str
) -> str:
    """Draws the degree ring (Monkeypatched to point outwards/into zodiac band)."""
    out = '<g id="degreeRing">'
    for i in range(360):
        offset = float(i * 1) - seventh_house_degree_ut
        if offset < 0:
            offset = offset + 360.0
        elif offset > 360:
            offset = offset - 360.0
        
        # Override c1 if user wants fixed width, but typically respect argument.
        # If user wants c1=31 specifically, uncomment next line:
        c1 = 36 # Used for positioning logic

        # Determine tick length based on degree
        # logic from kerykeion_chart_svg.py snippet
        if i % 30 == 0:
            height = 36  # Longest tick
            opacity = 1
            width = 1.5
        elif i % 10 == 0:
            height = 15  # Medium tick
            opacity = 1
            width = 1.5
        elif i % 5 == 0:
            height = 10  # Short tick
            opacity = 1
            width = 1.5
        else:
            height = 10   # Smallest tick (every degree)
            opacity = 0.4
            width = 1

        # We want dashes to point OUTWARDS from the inner circle (r - c1).
        # Inner circle radius = r - c1 (offset from center r by -c1)
        
        # Start point (on inner circle)
        x1 = sliceToX(0, r - c1, offset) + c1
        y1 = sliceToY(0, r - c1, offset) + c1
        
        # End point (pointing outwards by 'height')
        # outer_radius = r - c1 + height
        outer_radius = r - c1 + height
        
        # r - outer_radius = r - (r - c1 + height) = c1 - height
        x2 = sliceToX(0, outer_radius, offset) + c1 - height
        y2 = sliceToY(0, outer_radius, offset) + c1 - height

        out += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" style="stroke: {stroke_color}; stroke-width: {width}px; stroke-opacity:{opacity};"/>'
    out += "</g>"

    return out

# Apply Monkeypatches
# We patch the FUNCTIONS imported in kerykeion.charts.chart_drawer directly
kerykeion.charts.chart_drawer.draw_first_circle = _patched_draw_first_circle
kerykeion.charts.chart_drawer.draw_second_circle = _patched_draw_second_circle
kerykeion.charts.chart_drawer.draw_third_circle = _patched_draw_third_circle
kerykeion.charts.chart_drawer.draw_degree_ring = _patched_draw_degree_ring

def _patched_draw_houses_cusps_and_text_number(
    r: Union[int, float],
    first_subject_houses_list: list,
    standard_house_cusp_color: str,
    first_house_color: str,
    tenth_house_color: str,
    seventh_house_color: str,
    fourth_house_color: str,
    c1: Union[int, float],
    c3: Union[int, float],
    chart_type: ChartType,
    second_subject_houses_list: Union[list, None] = None,
    transit_house_cusp_color: Union[str, None] = None,
    external_view: bool = False,
) -> str:
    """Overridden drawing of house cusps to remove dashes and enforce a solid black line."""
    path = ""
    xr = 12

    for i in range(xr):
        # c3 (120) - начало линии (центральный круг).
        # roff = 36 - конец линии (2-й внутренний круг, перед зодиаком).
        dropin, roff, t_roff = (160, 72, 36) if chart_type in ["Transit", "Synastry", "DualReturnChart"] else (c3, 36, False)
        offset = (int(first_subject_houses_list[int(xr / 2)].abs_pos) / -1) + int(first_subject_houses_list[i].abs_pos)

        x1 = sliceToX(0, (r - dropin), offset) + dropin
        y1 = sliceToY(0, (r - dropin), offset) + dropin
        x2 = sliceToX(0, r - roff, offset) + roff
        y2 = sliceToY(0, r - roff, offset) + roff

        next_index = (i + 1) % xr
        text_offset = offset + int(
            degreeDiff(first_subject_houses_list[next_index].abs_pos, first_subject_houses_list[i].abs_pos) / 2
        )

        # Force line to be black
        linecolor = "#000000"

        if chart_type in ["Transit", "Synastry", "DualReturnChart"]:
            if second_subject_houses_list is None or transit_house_cusp_color is None:
                raise KerykeionException("second_subject_houses_list_ut or transit_house_cusp_color is None")

            zeropoint = 360 - first_subject_houses_list[6].abs_pos
            t_offset = (zeropoint + second_subject_houses_list[i].abs_pos) % 360

            t_x1 = sliceToX(0, (r - t_roff), t_offset) + t_roff
            t_y1 = sliceToY(0, (r - t_roff), t_offset) + t_roff
            t_x2 = sliceToX(0, r, t_offset)
            t_y2 = sliceToY(0, r, t_offset)

            t_text_offset = t_offset + int(
                degreeDiff(second_subject_houses_list[next_index].abs_pos, second_subject_houses_list[i].abs_pos) / 2
            )
            t_linecolor = "#000000"
            xtext = sliceToX(0, (r - 8), t_text_offset) + 8
            ytext = sliceToY(0, (r - 8), t_text_offset) + 8

            fill_opacity = "0" if chart_type == "Transit" else ".4"
            path += '<g kr:node="HouseNumber">'
            path += f'<text style="fill: var(--kerykeion-chart-color-house-number); fill-opacity: {fill_opacity}; font-size: 14px"><tspan x="{xtext - 3}" y="{ytext + 3}">{i + 1}</tspan></text>'
            path += "</g>"

            stroke_opacity = "0" if chart_type == "Transit" else ".3"
            path += f'<g kr:node="Cusp" kr:absoluteposition="{second_subject_houses_list[i].abs_pos}" kr:signposition="{second_subject_houses_list[i].position}" kr:sing="{second_subject_houses_list[i].sign}" kr:slug="{second_subject_houses_list[i].name}">'
            path += f"<line x1='{t_x1}' y1='{t_y1}' x2='{t_x2}' y2='{t_y2}' style='stroke: {t_linecolor}; stroke-width: {CUSTOM_RING_WIDTH}; stroke-opacity:{stroke_opacity};'/>"
            path += "</g>"

        dropin_map = {"Transit": 84, "Synastry": 84, "DualReturnChart": 84}
        if external_view:
            dropin = 100
        else:
            dropin = dropin_map.get(chart_type, 48)
        xtext = sliceToX(0, (r - dropin), text_offset) + dropin
        ytext = sliceToY(0, (r - dropin), text_offset) + dropin

        path += f'<g kr:node="Cusp" kr:absoluteposition="{first_subject_houses_list[i].abs_pos}" kr:signposition="{first_subject_houses_list[i].position}" kr:sing="{first_subject_houses_list[i].sign}" kr:slug="{first_subject_houses_list[i].name}">'
        # No dashed array, solidly opaque
        path += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" style="stroke: {linecolor}; stroke-width: {CUSTOM_RING_WIDTH}; stroke-opacity: 0.4;"/>'
        path += "</g>"

        path += '<g kr:node="HouseNumber">'
        path += f'<text style="fill: var(--kerykeion-chart-color-house-number); fill-opacity: .6; font-size: 14px"><tspan x="{xtext - 3}" y="{ytext + 3}">{i + 1}</tspan></text>'
        path += "</g>"

    return path

kerykeion.charts.chart_drawer.draw_houses_cusps_and_text_number = _patched_draw_houses_cusps_and_text_number
