import re
import sys
from pathlib import Path
import math

def get_bounds(d):
    # Robust SVG path parser handling scientific notation
    number_re = re.compile(r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?")
    
    tokens = []
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
                pass # Should be handled by while condition but just in case

        else:
            i += 1
            
    return min_x, min_y, max_x, max_y

def analyze_svg(filename):
    content = Path(filename).read_text()
    
    pattern = re.compile(r"<symbol id=['\"](\w+)['\"]>(.*?)</symbol>", re.DOTALL)
    matches = pattern.findall(content)
    
    print(f"{'Symbol':<10} {'Min X':<10} {'Max X':<10} {'Min Y':<10} {'Max Y':<10} {'Width':<10} {'Height':<10} {'Center X':<10} {'Center Y':<10}")
    print("-" * 100)
    
    zodiac_signs = ['Ari', 'Tau', 'Gem', 'Can', 'Leo', 'Vir', 'Lib', 'Sco', 'Sag', 'Cap', 'Aqu', 'Pis']
    
    for symbol_id, body in matches:
        if symbol_id not in zodiac_signs:
            continue
            
        path_match = re.search(r"d=['\"](.*?)['\"]", body)
        if path_match:
            d = path_match.group(1)
            min_x, min_y, max_x, max_y = get_bounds(d)
            
            width = max_x - min_x
            height = max_y - min_y
            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2
            
            print(f"{symbol_id:<10} {min_x:<10.2f} {max_x:<10.2f} {min_y:<10.2f} {max_y:<10.2f} {width:<10.2f} {height:<10.2f} {center_x:<10.2f} {center_y:<10.2f}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_symbols.py <svg_file>")
        sys.exit(1)
        
    analyze_svg(sys.argv[1])
