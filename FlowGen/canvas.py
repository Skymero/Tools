import tkinter as tk
import uuid

class CanvasManager:
    """Manages the drawing canvas for FlowGen, handling shapes, connections, and interactions."""
    def __init__(self, root):
        self.canvas = tk.Canvas(root, bg='white', width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.shapes = {}  # shape_id -> metadata dict
        self.lines = []   # list of connection dicts
        self.mode = None
        self.selected_shape = None
        self.drag_data = None
        # Bind events
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<Double-1>', self.on_double_click)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)

    def start_adding(self, shape_type):
        """Begin adding a new shape or enter connect mode."""
        # Enter connect mode when selecting the connect tool
        if shape_type == 'connect':
            self.mode = 'connect'
        else:
            self.mode = f'add_{shape_type}'
        self.selected_shape = None

    def clear(self):
        """Clear all shapes and connections from the canvas."""
        self.canvas.delete('all')
        self.shapes.clear()
        self.lines.clear()

    def load_template(self, template):
        """Load a predefined template of nodes and connections."""
        self.clear()
        id_map = {}
        # Create nodes
        for idx, node in enumerate(template.get('nodes', [])):
            uid = self._create_shape(node['type'], node['x'], node['y'], node.get('text', ''), node.get('color'))
            id_map[str(idx)] = uid
        # Create connections
        for conn in template.get('connections', []):
            src = id_map.get(conn['from'])
            dst = id_map.get(conn['to'])
            if src and dst:
                self._connect_shapes(src, dst)

    def save(self, path):
        """Save the current flowchart to a JSON file."""
        import json
        data = {'nodes': [], 'connections': []}
        # Export nodes
        for uid, info in self.shapes.items():
            x1, y1, x2, y2 = self.canvas.bbox(info['item'])
            data['nodes'].append({
                'id': uid,
                'type': info['type'],
                'x': x1,
                'y': y1,
                'text': info['text'],
                'color': info['color']
            })
        # Export connections
        for line in self.lines:
            data['connections'].append({'from': line['src'], 'to': line['dst']})
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def on_click(self, event):
        """Handle single click for adding shapes or connecting."""
        if self.mode and self.mode.startswith('add_'):
            shape_type = self.mode.replace('add_', '')
            self._create_shape(shape_type, event.x, event.y)
            self.mode = None
        elif self.mode == 'connect':
            uid = self._get_shape_at(event.x, event.y)
            if uid:
                if not self.selected_shape:
                    self.selected_shape = uid
                else:
                    self._connect_shapes(self.selected_shape, uid)
                    self.selected_shape = None
        else:
            uid = self._get_shape_at(event.x, event.y)
            if uid:
                # Begin drag
                self.drag_data = {'uid': uid, 'x': event.x, 'y': event.y}

    def on_double_click(self, event):
        """Handle double-click to edit text of shape."""
        uid = self._get_shape_at(event.x, event.y)
        if uid:
            self._edit_text(uid)

    def on_drag(self, event):
        """Handle shape dragging and update connections."""
        if not self.drag_data:
            return
        uid = self.drag_data['uid']
        dx = event.x - self.drag_data['x']
        dy = event.y - self.drag_data['y']
        info = self.shapes[uid]
        # Move shape and its label
        self.canvas.move(info['item'], dx, dy)
        self.canvas.move(info['text_item'], dx, dy)
        # Update lines connected to this shape
        for line in self.lines:
            if line['src'] == uid or line['dst'] == uid:
                src_info = self.shapes[line['src']]
                dst_info = self.shapes[line['dst']]
                x1, y1, x2, y2 = self.canvas.bbox(src_info['item'])
                sx, sy = (x1+x2)/2, (y1+y2)/2
                x3, y3, x4, y4 = self.canvas.bbox(dst_info['item'])
                ex, ey = (x3+x4)/2, (y3+y4)/2
                self.canvas.coords(line['id'], sx, sy, ex, ey)
        # Update drag start position
        self.drag_data['x'] = event.x
        self.drag_data['y'] = event.y

    def on_release(self, event):
        """End dragging."""
        self.drag_data = None

    def _create_shape(self, shape_type, x, y, text='', color=None):
        """Internal: Create and register a new shape on the canvas."""
        shape_id = str(uuid.uuid4())
        size = 80
        fill = color or '#A0C4FF'
        # Draw shape
        if shape_type == 'rectangle':
            item = self.canvas.create_rectangle(x, y, x+size, y+size, fill=fill)
        elif shape_type == 'circle':
            item = self.canvas.create_oval(x, y, x+size, y+size, fill=fill)
        elif shape_type == 'diamond':
            half = size/2
            points = [x+half, y, x+size, y+half, x+half, y+size, x, y+half]
            item = self.canvas.create_polygon(points, fill=fill)
        else:
            return
        # Add text label
        text_item = self.canvas.create_text(x+size/2, y+size/2, text=text or shape_type.capitalize())
        # Store metadata
        self.shapes[shape_id] = {
            'type': shape_type,
            'item': item,
            'text_item': text_item,
            'text': text or shape_type.capitalize(),
            'color': fill
        }
        return shape_id

    def _get_shape_at(self, x, y):
        """Internal: Return the shape_id at given canvas coordinates."""
        items = self.canvas.find_overlapping(x, y, x, y)
        for item in items:
            for uid, info in self.shapes.items():
                if item in (info['item'], info['text_item']):
                    return uid
        return None

    def _connect_shapes(self, src_id, dst_id):
        """Internal: Draw an arrowed line connecting two shapes."""
        src = self.shapes[src_id]
        dst = self.shapes[dst_id]
        # Compute centers
        x1, y1, x2, y2 = self.canvas.bbox(src['item'])
        sx, sy = (x1+x2)/2, (y1+y2)/2
        x3, y3, x4, y4 = self.canvas.bbox(dst['item'])
        dx, dy = (x3+x4)/2, (y3+y4)/2
        line_id = self.canvas.create_line(sx, sy, dx, dy, arrow=tk.LAST)
        self.lines.append({'id': line_id, 'src': src_id, 'dst': dst_id})

    def _edit_text(self, uid):
        """Internal: Open a dialog to edit shape text."""
        info = self.shapes[uid]
        x1, y1, _, _ = self.canvas.bbox(info['item'])
        dialog = tk.Toplevel()
        dialog.title('Edit Text')
        tk.Label(dialog, text='Text:').pack(side=tk.LEFT)
        var = tk.StringVar(value=info['text'])
        entry = tk.Entry(dialog, textvariable=var)
        entry.pack(side=tk.LEFT)
        def save_and_close():
            new = var.get()
            self.canvas.itemconfig(info['text_item'], text=new)
            info['text'] = new
            dialog.destroy()
        tk.Button(dialog, text='Save', command=save_and_close).pack(side=tk.RIGHT)
