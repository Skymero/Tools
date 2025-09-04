"""Color_Swatch_Gen1 - A new Python project"""

from PIL import Image, ImageDraw

def extract_colors_from_file(filename="hex_colors.txt"):
    """
    Extracts hex color codes from a text file and returns them as a list.
    Each line in the file should contain one hex color code.
    """
    colors = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                # Strip whitespace and ensure the line is not empty
                color = line.strip()
                if color and color.startswith('#'):
                    colors.append(color)
    except FileNotFoundError:
        print(f"Error: {filename} not found. Using default colors.")
        # Return some default colors if file is not found
        return ["#016743", "#022644", "#028376", "#04615a", "#047a90"]
    
    return colors

# Extract colors from hex_colors.txt file
hex_colors = extract_colors_from_file()
print(f"Loaded {len(hex_colors)} colors from file")



# size of each swatch
swatch_size = 100
cols = 5  # number of columns
rows = (len(hex_colors) + cols - 1) // cols

# create new image
img = Image.new("RGB", (cols * swatch_size, rows * swatch_size), "white")
draw = ImageDraw.Draw(img)

for i, hex_color in enumerate(hex_colors):
    row, col = divmod(i, cols)
    x0, y0 = col * swatch_size, row * swatch_size
    x1, y1 = x0 + swatch_size, y0 + swatch_size
    draw.rectangle([x0, y0, x1, y1], fill=hex_color)

img.save("color_collage.png")
