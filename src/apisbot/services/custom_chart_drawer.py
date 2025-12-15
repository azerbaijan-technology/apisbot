from pathlib import Path
from typing import Optional, Union, get_args

from kerykeion.charts.chart_drawer import ChartDrawer
from kerykeion.charts.charts_utils import sliceToX, sliceToY
from kerykeion.schemas import ChartType, Sign

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

        slice_path = f'<path d="M{str(r)},{str(r)} L{str(dropin + sliceToX(num, r - dropin, offset))},{str(dropin + sliceToY(num, r - dropin, offset))} A{str(r - dropin)},{str(r - dropin)} 0 0,0 {str(dropin + sliceToX(num + 1, r - dropin, offset))},{str(dropin + sliceToY(num + 1, r - dropin, offset))} z" style="{style}"/>'

        # symbols
        offset = offset  # <-- REMOVED to fix alignment
        offset = offset + 15
        # check transit
        if chart_type == "Transit" or chart_type == "Synastry" or chart_type == "DualReturnChart":
            dropin = 54
        else:
            dropin = 18 + c1

        sign = f'<g transform="translate(-16,-16)"><use x="{str(dropin + sliceToX(num, r - dropin, offset))}" y="{str(dropin + sliceToY(num, r - dropin, offset))}" xlink:href="#{type}" /></g>'

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
