import re
import graphviz
import sys

# Check if a file path is provided as a command line argument
if len(sys.argv) < 2:
    print("Usage: python plant2diag.py <path_to_plantuml_file>")
    sys.exit(1)

# Read PlantUML file from command line argument
plantuml_file_path = sys.argv[1]
try:
    with open(plantuml_file_path, 'r') as file:
        plantuml_code = file.read()
except FileNotFoundError:
    print(f"Error: File '{plantuml_file_path}' not found.")
    sys.exit(1)
except Exception as e:
    print(f"Error reading file: {e}")
    sys.exit(1)

# Extract the output filename from the input path
import os
output_base = os.path.splitext(os.path.basename(plantuml_file_path))[0]

# Extract activity lines
activity_lines = re.findall(r':(.*?);', plantuml_code)
nodes = [line.strip() for line in activity_lines]
node_ids = [f"n{i}" for i in range(len(nodes))]

# Create graphviz Digraph
dot = graphviz.Digraph(format='png')
dot.attr(rankdir='LR', size='12,6')

# Add nodes and edges
for nid, label in zip(node_ids, nodes):
    dot.node(nid, label)

for i in range(len(node_ids) - 1):
    dot.edge(node_ids[i], node_ids[i + 1])

# Render with specific path
result_file = dot.render(filename=output_base, cleanup=False)
print(f"Generated file: {result_file}")
