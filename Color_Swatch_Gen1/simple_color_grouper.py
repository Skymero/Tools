"""Simple Color Grouper - Groups hex colors by analyzing RGB values"""

def hex_to_rgb(hex_color):
    """Convert hex to RGB values"""
    hex_color = hex_color.lstrip('#')
    return int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

def categorize_color(hex_color):
    """Categorize color based on RGB dominance and ranges"""
    r, g, b = hex_to_rgb(hex_color)
    
    # Calculate which channel is dominant
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    
    # Check for grayscale (all values close)
    if abs(max_val - min_val) < 30:
        if max_val < 50:
            return "Dark_Gray_Black"
        elif max_val > 200:
            return "Light_Gray_White"
        else:
            return "Medium_Gray"
    
    # Determine dominant color
    if r > g and r > b:
        if g > 100:  # Red with significant green = orange/yellow
            return "Orange_Yellow"
        else:
            return "Red"
    elif g > r and g > b:
        if r > 80:  # Green with red = yellow/lime
            return "Yellow_Lime"
        elif b > 80:  # Green with blue = cyan/teal
            return "Cyan_Teal"
        else:
            return "Green"
    elif b > r and b > g:
        if g > 80:  # Blue with green = cyan/teal
            return "Cyan_Teal"
        elif r > 80:  # Blue with red = purple
            return "Purple_Magenta"
        else:
            return "Blue"
    
    # Handle equal dominance cases
    if r == g and r > b:
        return "Yellow_Lime"
    elif r == b and r > g:
        return "Purple_Magenta"
    elif g == b and g > r:
        return "Cyan_Teal"
    
    return "Mixed"

# Read and process colors
color_groups = {}
with open('hex_colors.txt', 'r') as file:
    for line in file:
        color = line.strip()
        if color and color.startswith('#'):
            category = categorize_color(color)
            if category not in color_groups:
                color_groups[category] = []
            color_groups[category].append(color)

# Print results
print("Color Analysis Results:")
print("=" * 60)
total_colors = sum(len(colors) for colors in color_groups.values())

for category in sorted(color_groups.keys()):
    colors = color_groups[category]
    percentage = (len(colors) / total_colors) * 100
    print(f"\n{category.replace('_', ' ')}: {len(colors)} colors ({percentage:.1f}%)")
    
    # Show first few colors as samples
    sample_colors = colors[:5]
    print(f"  Samples: {', '.join(sample_colors)}")
    
    # Save to individual file
    filename = f"colors_{category.lower()}.txt"
    with open(filename, 'w') as f:
        for color in colors:
            f.write(color + '\n')
    print(f"  Saved to: {filename}")

print(f"\nTotal colors processed: {total_colors}")
print("\nAll color groups have been saved to separate files!")
