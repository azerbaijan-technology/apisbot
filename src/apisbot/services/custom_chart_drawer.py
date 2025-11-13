from pathlib import Path
from typing import Optional
from kerykeion.charts.chart_drawer import ChartDrawer

# Список встроенных тем (копия из KerykeionChartTheme)
VALID_THEMES = [
    "light", "dark", "dark-high-contrast", 
    "classic", "strawberry", "black-and-white"
]

class CustomChartDrawer(ChartDrawer):
    def __init__(
        self,
        chart_data,
        *,
        theme: Optional[str] = None,  # Принимаем любую строку
        **kwargs
    ):
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