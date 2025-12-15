import re
import math
from pathlib import Path

def get_bounds(d):
    # Robust SVG path parser handling scientific notation
    number_re = re.compile(r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?")
    
    parts = re.split(r"([a-zA-Z])", d)
    
    min_x, min_y = float('inf'), float('inf')
    max_x, max_y = float('-inf'), float('-inf')
    
    current_x, current_y = 0.0, 0.0
    start_x, start_y = 0.0, 0.0
    
    i = 0
    while i < len(parts):
        part = parts[i].strip()
        if not part:
            i += 1
            continue
            
        if len(part) == 1 and part.isalpha():
            cmd = part
            i += 1
            args_str = ""
            if i < len(parts):
                args_str = parts[i]
                i += 1
            
            nums = [float(x) for x in number_re.findall(args_str)]
            
            k = 0
            try:
                if cmd in ['M', 'L', 'T']:
                    while k + 1 < len(nums):
                        current_x, current_y = nums[k], nums[k+1]
                        if cmd == 'M': start_x, start_y = current_x, current_y
                        min_x, max_x = min(min_x, current_x), max(max_x, current_x)
                        min_y, max_y = min(min_y, current_y), max(max_y, current_y)
                        k += 2
                        cmd = 'L'
                
                elif cmd in ['m', 'l', 't']:
                    while k + 1 < len(nums):
                        current_x += nums[k]
                        current_y += nums[k+1]
                        if cmd == 'm': start_x, start_y = current_x, current_y
                        min_x, max_x = min(min_x, current_x), max(max_x, current_x)
                        min_y, max_y = min(min_y, current_y), max(max_y, current_y)
                        k += 2
                        cmd = 'l'

                elif cmd == 'H':
                    while k < len(nums):
                        current_x = nums[k]
                        min_x, max_x = min(min_x, current_x), max(max_x, current_x)
                        k += 1
                
                elif cmd == 'h':
                    while k < len(nums):
                        current_x += nums[k]
                        min_x, max_x = min(min_x, current_x), max(max_x, current_x)
                        k += 1

                elif cmd == 'V':
                    while k < len(nums):
                        current_y = nums[k]
                        min_y, max_y = min(min_y, current_y), max(max_y, current_y)
                        k += 1
                
                elif cmd == 'v':
                    while k < len(nums):
                        current_y += nums[k]
                        min_y, max_y = min(min_y, current_y), max(max_y, current_y)
                        k += 1
                
                elif cmd == 'Z' or cmd == 'z':
                    current_x, current_y = start_x, start_y
                    
                elif cmd in ['C', 'S', 'Q']:
                    stride = 6 if cmd == 'C' else 4
                    while k + stride - 1 < len(nums):
                        for j in range(0, stride, 2):
                            px, py = nums[k+j], nums[k+j+1]
                            min_x, max_x = min(min_x, px), max(max_x, px)
                            min_y, max_y = min(min_y, py), max(max_y, py)
                        current_x, current_y = nums[k+stride-2], nums[k+stride-1]
                        k += stride

                elif cmd in ['c', 's', 'q']:
                    stride = 6 if cmd == 'c' else 4
                    while k + stride - 1 < len(nums):
                        for j in range(0, stride, 2):
                            px, py = current_x + nums[k+j], current_y + nums[k+j+1]
                            min_x, max_x = min(min_x, px), max(max_x, px)
                            min_y, max_y = min(min_y, py), max(max_y, py)
                        current_x += nums[k+stride-2]
                        current_y += nums[k+stride-1]
                        k += stride
                        
                elif cmd in ['A', 'a']:
                    while k + 6 < len(nums):
                        if cmd == 'A':
                            current_x, current_y = nums[k+5], nums[k+6]
                        else:
                            current_x += nums[k+5]
                            current_y += nums[k+6]
                        min_x, max_x = min(min_x, current_x), max(max_x, current_x)
                        min_y, max_y = min(min_y, current_y), max(max_y, current_y)
                        k += 7
            except IndexError:
                pass

        else:
            i += 1
            
    return min_x, min_y, max_x, max_y

def generate_debug_svg(chart_xml_path, output_path):
    content = Path(chart_xml_path).read_text()
    
    pattern = re.compile(r"<symbol id=['\"](\w+)['\"]>(.*?)</symbol>", re.DOTALL)
    matches = pattern.findall(content)
    
    zodiac_signs = ['Ari', 'Tau', 'Gem', 'Can', 'Leo', 'Vir', 'Lib', 'Sco', 'Sag', 'Cap', 'Aqu', 'Pis']
    
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="800" height="600" viewBox="0 0 800 600" style="background-color: #f0f0f0;">
    <style>
        .bbox { fill: none; stroke: blue; stroke-width: 0.5; stroke-dasharray: 2,2; }
        .center { fill: red; stroke: none; }
        .origin { fill: none; stroke: black; stroke-width: 1; }
        .default-center { fill: none; stroke: green; stroke-width: 0.5; }
        text { font-family: sans-serif; font-size: 12px; }
    </style>
    <defs>
    """
    
    # Add symbol definitions
    for symbol_id, body in matches:
        if symbol_id in zodiac_signs:
            svg_content += f'<symbol id="{symbol_id}">{body}</symbol>\n'
            
    svg_content += "</defs>\n"
    
    x_start = 50
    y_start = 50
    col_width = 100
    row_height = 100
    cols = 6
    
    for i, sign in enumerate(zodiac_signs):
        row = i // cols
        col = i % cols
        
        x = x_start + col * col_width
        y = y_start + row * row_height
        
        # Find symbol body to calculate bounds
        body = next((b for s, b in matches if s == sign), "")
        path_match = re.search(r"d=['\"](.*?)['\"]", body)
        
        min_x, min_y, max_x, max_y = 0, 0, 0, 0
        center_x, center_y = 0, 0
        
        if path_match:
            d = path_match.group(1)
            min_x, min_y, max_x, max_y = get_bounds(d)
            width = max_x - min_x
            height = max_y - min_y
            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2
        
        # Draw grid cell
        svg_content += f'<g transform="translate({x},{y})">'
        
        # Label
        svg_content += f'<text x="0" y="-20">{sign}</text>'
        
        # Draw symbol (no translation, just placed at 0,0 relative to cell)
        # We want to see where it draws relative to (0,0)
        # But we need to shift it to visible area. Let's put (0,0) at (50, 50) in the cell
        cell_origin_x = 50
        cell_origin_y = 50
        
        svg_content += f'<g transform="translate({cell_origin_x},{cell_origin_y})">'
        
        # Origin crosshair (0,0)
        svg_content += '<line x1="-10" y1="0" x2="10" y2="0" class="origin"/>'
        svg_content += '<line x1="0" y1="-10" x2="0" y2="10" class="origin"/>'
        
        # The symbol itself
        svg_content += f'<use xlink:href="#{sign}" />'
        
        # Bounding box
        svg_content += f'<rect x="{min_x}" y="{min_y}" width="{max_x-min_x}" height="{max_y-min_y}" class="bbox"/>'
        
        # Calculated geometric center
        svg_content += f'<circle cx="{center_x}" cy="{center_y}" r="2" class="center"/>'
        
        # Default assumed center (16, 16)
        svg_content += f'<rect x="16" y="16" width="32" height="32" transform="translate(-16,-16)" class="default-center"/>'
        svg_content += f'<circle cx="16" cy="16" r="2" style="fill:green"/>'
        
        svg_content += '</g>' # End cell content
        
        # Info text
        svg_content += f'<text x="0" y="90" font-size="10">C: {center_x:.1f}, {center_y:.1f}</text>'
        
        svg_content += '</g>\n'
        
    svg_content += "</svg>"
    
    Path(output_path).write_text(svg_content)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_debug_svg(".venv/lib/python3.12/site-packages/kerykeion/charts/templates/chart.xml", "debug_symbols.svg")
