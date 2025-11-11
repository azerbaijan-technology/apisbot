from pathlib import Path
from pathlib import Path
from pathlib import Path
from pathlib import Path
from kerykeion import AstrologicalSubjectFactory, ChartDataFactory
from kerykeion.charts.chart_drawer import ChartDrawer

from custom_chart_data_factory import CustomChartDataFactory

# Step 1: Create subjects
natal_subject = AstrologicalSubjectFactory.from_birth_data(
    "Transit Natal", 2001, 6, 8, 14, 40,
    lng=56,
    lat=37,
    tz_str="Europe/Moscow",
    online=False,
    houses_system_identifier="W"
)

transit_subject = AstrologicalSubjectFactory.from_current_time(
    "Transit Positions",
    lng=56,
    lat=37,
    tz_str="Europe/Moscow",
    online=False,
    houses_system_identifier="W"
)

active_points = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
active_aspects = [
    {"name": "conjunction", "orb": 5},
    {"name": "opposition", "orb": 5},
    {"name": "trine", "orb": 5},
    {"name": "square", "orb": 5},
    {"name": "sextile", "orb": 3},
]

# Step 2: Pre-compute transit chart data
chart_data = ChartDataFactory.create_natal_chart_data(
    natal_subject,
    active_points=active_points,
    active_aspects=active_aspects,

)

# Step 3: Create visualization
chart_drawer = ChartDrawer(chart_data=chart_data)

output_dir = Path("charts_output")
output_dir.mkdir(exist_ok=True)

# Get the transit chart content
svg_content = chart_drawer.save_wheel_only_svg_file(output_path=output_dir)

new_chart_data = CustomChartDataFactory.create_natal_chart_data(
    natal_subject,
    active_points=active_points,
    active_aspects=active_aspects,
    restrict_to_similar_signs=True

)

new_chart_drawer = ChartDrawer(chart_data=new_chart_data)

new_output_dir = Path("new_charts_output")
new_output_dir.mkdir(exist_ok=True)

new_svg_content = new_chart_drawer.save_wheel_only_svg_file(output_path=new_output_dir)

print(new_chart_data.aspects)
# # После создания subjects
# print("=== Проверка структуры данных ===")
# sample_point = natal_subject.sun  # Пример: Солнце
# print(f"Солнце: {sample_point}")
# print(f"Атрибуты: {dir(sample_point)}")
# print(f"sign_num: {getattr(sample_point, 'sign_num', 'НЕТ')}")
# print(f"abs_pos: {getattr(sample_point, 'abs_zodiac_long', 'НЕТ')}")
# print("=== Конец проверки ===")