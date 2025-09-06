"""Group hex colors by base color families"""

def analyze_hex_color(hex_color):
    """Analyze hex color and determine its base color family"""
    # Remove # if present
    hex_val = hex_color.lstrip('#').upper()
    
    # Convert to RGB
    r = int(hex_val[0:2], 16)
    g = int(hex_val[2:4], 16) 
    b = int(hex_val[4:6], 16)
    
    # Determine base color by analyzing RGB dominance and values
    max_component = max(r, g, b)
    
    # Very dark colors (all components low)
    if max_component < 40:
        return "Very Dark"
    
    # Near grayscale (components close together)
    if abs(r - g) < 20 and abs(g - b) < 20 and abs(r - b) < 20:
        if max_component < 80:
            return "Dark Gray"
        elif max_component > 180:
            return "Light Gray" 
        else:
            return "Medium Gray"
    
    # Color categorization based on dominant channels
    if r > g and r > b:
        # Red is dominant
        if g > b + 30:  # Red with green = orange/yellow
            if g > 150:
                return "Yellow"
            else:
                return "Orange"
        else:
            return "Red"
    
    elif g > r and g > b:
        # Green is dominant
        if b > r + 20:  # Green with blue = teal/cyan
            return "Teal/Cyan"
        elif r > b + 20:  # Green with red = yellow/lime
            return "Yellow/Lime"
        else:
            return "Green"
    
    elif b > r and b > g:
        # Blue is dominant
        if g > r + 20:  # Blue with green = teal/cyan
            return "Teal/Cyan"
        elif r > g + 20:  # Blue with red = purple
            return "Purple"
        else:
            return "Blue"
    
    # Equal dominance cases
    if abs(r - g) < 15 and r > b + 20:
        return "Yellow"
    elif abs(r - b) < 15 and r > g + 20:
        return "Purple/Magenta"
    elif abs(g - b) < 15 and g > r + 20:
        return "Teal/Cyan"
    
    return "Mixed"

# Read colors from file
colors = []
try:
    with open('hex_colors.txt', 'r') as file:
        for line in file:
            color = line.strip()
            if color and color.startswith('#'):
                colors.append(color)
    print(f"Loaded {len(colors)} colors")
except FileNotFoundError:
    print("hex_colors.txt not found!")
    exit()

# Group colors by category
color_groups = {}
for color in colors:
    category = analyze_hex_color(color)
    if category not in color_groups:
        color_groups[category] = []
    color_groups[category].append(color)

# Display results and save to files
print("\nColor Groups:")
print("=" * 50)

for category in sorted(color_groups.keys()):
    group_colors = color_groups[category]
    percentage = (len(group_colors) / len(colors)) * 100
    
    print(f"\n{category}: {len(group_colors)} colors ({percentage:.1f}%)")
    print(f"  First 5: {', '.join(group_colors[:5])}")
    
    # Save each group to a separate file
    filename = f"colors_{category.lower().replace('/', '_').replace(' ', '_')}.txt"
    with open(filename, 'w') as f:
        for color in group_colors:
            f.write(color + '\n')
    print(f"  Saved to: {filename}")

print(f"\nTotal: {len(colors)} colors grouped into {len(color_groups)} categories")
