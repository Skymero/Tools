"""Color Groups - Organize hex colors by base color families"""

def create_color_groups():
    """Manually categorize colors based on hex value analysis"""
    
    # Read all colors from file
    with open('hex_colors.txt', 'r') as f:
        all_colors = [line.strip() for line in f if line.strip().startswith('#')]
    
    # Define color groups based on hex patterns and RGB dominance
    groups = {
        'Dark_Blue_Teal': [],      # #01-#19 range, blue-green dominant
        'Teal_Cyan': [],           # #1a-#2f range, teal shades  
        'Green': [],               # #30-#4f range, green dominant
        'Yellow_Green': [],        # #50-#6f range, yellow-green
        'Orange_Yellow': [],       # #70-#bf range, orange to yellow
        'Red_Orange': [],          # #c0-#df range, red-orange
        'Light_Neutrals': [],      # Light grays and beiges
        'Mixed': []                # Colors that don't fit clear categories
    }
    
    for color in all_colors:
        hex_val = color.lstrip('#').upper()
        
        # Convert first two hex digits to get red component
        red = int(hex_val[0:2], 16)
        green = int(hex_val[2:4], 16)  
        blue = int(hex_val[4:6], 16)
        
        # Categorize based on RGB values and patterns
        if red < 50 and blue > green:
            # Dark blues and teals
            groups['Dark_Blue_Teal'].append(color)
        elif red < 80 and green >= blue and abs(green - blue) < 40:
            # Teal and cyan shades
            groups['Teal_Cyan'].append(color)
        elif green > red and green > blue and red < 100:
            # Pure greens
            groups['Green'].append(color)
        elif green >= 120 and red > 80 and red < 140:
            # Yellow-green range
            groups['Yellow_Green'].append(color)
        elif red > 150 and green > 100 and blue < 50:
            # Orange and yellow range
            groups['Orange_Yellow'].append(color)
        elif red > 180 and green < 120:
            # Red and red-orange range
            groups['Red_Orange'].append(color)
        elif abs(red - green) < 30 and abs(green - blue) < 30 and red > 150:
            # Light neutrals and grays
            groups['Light_Neutrals'].append(color)
        else:
            # Mixed or unclear category
            groups['Mixed'].append(color)
    
    return groups, all_colors

def save_and_display_groups():
    """Save color groups to files and display summary"""
    groups, all_colors = create_color_groups()
    
    print("Color Groups Analysis")
    print("=" * 60)
    
    total_colors = len(all_colors)
    
    for group_name, colors in groups.items():
        if colors:  # Only show groups that have colors
            percentage = (len(colors) / total_colors) * 100
            print(f"\n{group_name.replace('_', ' ')}: {len(colors)} colors ({percentage:.1f}%)")
            
            # Show sample colors
            samples = colors[:5]
            print(f"  Samples: {', '.join(samples)}")
            
            # Save to file
            filename = f"colors_{group_name.lower()}.txt"
            with open(filename, 'w') as f:
                for color in colors:
                    f.write(color + '\n')
            print(f"  → Saved to {filename}")
    
    print(f"\nTotal colors processed: {total_colors}")
    print(f"Groups created: {len([g for g in groups.values() if g])}")
    
    return groups

if __name__ == "__main__":
    save_and_display_groups()
