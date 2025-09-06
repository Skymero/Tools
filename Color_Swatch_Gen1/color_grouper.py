"""Color Grouper - Groups hex colors by base color families"""

import colorsys
from collections import defaultdict

def hex_to_rgb(hex_color):
    """Convert hex color to RGB values (0-255)"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hsv(r, g, b):
    """Convert RGB (0-255) to HSV (0-360, 0-100, 0-100)"""
    r, g, b = r/255.0, g/255.0, b/255.0
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return h * 360, s * 100, v * 100

def get_color_category(hex_color):
    """
    Determine the base color category based on HSV values.
    Returns the color family name.
    """
    r, g, b = hex_to_rgb(hex_color)
    h, s, v = rgb_to_hsv(r, g, b)
    
    # Handle near-grayscale colors (low saturation)
    if s < 15:
        if v < 30:
            return "Black/Dark Gray"
        elif v > 80:
            return "White/Light Gray"
        else:
            return "Gray"
    
    # Handle very dark colors (low value)
    if v < 20:
        return "Very Dark"
    
    # Categorize by hue ranges
    if h >= 0 and h < 15:
        return "Red"
    elif h >= 15 and h < 45:
        return "Orange"
    elif h >= 45 and h < 75:
        return "Yellow"
    elif h >= 75 and h < 150:
        return "Green"
    elif h >= 150 and h < 210:
        return "Cyan/Teal"
    elif h >= 210 and h < 270:
        return "Blue"
    elif h >= 270 and h < 330:
        return "Purple/Magenta"
    else:  # h >= 330 and h < 360
        return "Red"

def group_colors_from_file(filename="hex_colors.txt"):
    """
    Read hex colors from file and group them by base color categories.
    Returns a dictionary with color categories as keys and lists of hex colors as values.
    """
    color_groups = defaultdict(list)
    
    try:
        with open(filename, 'r') as file:
            for line in file:
                color = line.strip()
                if color and color.startswith('#'):
                    category = get_color_category(color)
                    color_groups[category].append(color)
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return {}
    
    return dict(color_groups)

def print_color_groups(color_groups):
    """Print color groups with counts and sample colors"""
    print("Color Groups Analysis:")
    print("=" * 50)
    
    total_colors = sum(len(colors) for colors in color_groups.values())
    
    for category, colors in sorted(color_groups.items()):
        percentage = (len(colors) / total_colors) * 100
        print(f"\n{category}: {len(colors)} colors ({percentage:.1f}%)")
        print(f"  Sample colors: {', '.join(colors[:5])}")
        if len(colors) > 5:
            print(f"  ... and {len(colors) - 5} more")

def save_grouped_colors(color_groups, base_filename="grouped_colors"):
    """Save each color group to separate files"""
    for category, colors in color_groups.items():
        # Create safe filename
        safe_category = category.lower().replace('/', '_').replace(' ', '_')
        filename = f"{base_filename}_{safe_category}.txt"
        
        with open(filename, 'w') as file:
            for color in colors:
                file.write(f"{color}\n")
        
        print(f"Saved {len(colors)} {category} colors to {filename}")

if __name__ == "__main__":
    # Group the colors
    groups = group_colors_from_file()
    
    # Print analysis
    print_color_groups(groups)
    
    # Save to separate files
    print("\n" + "=" * 50)
    save_grouped_colors(groups)
    
    print(f"\nTotal colors processed: {sum(len(colors) for colors in groups.values())}")
