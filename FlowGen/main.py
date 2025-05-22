import tkinter as tk
from tkinter import filedialog, messagebox
from canvas import CanvasManager
from templates import TEMPLATES
from exporter import export_png, export_pdf

class FlowGenApp:
    def __init__(self, root):
        """
        Initialize a FlowGenApp.

        :param root: The Tkinter root to build the UI on.
        """
        root.title("FlowGen - Flowchart Generator")
        self.canvas_manager = CanvasManager(root)
        self._create_menu(root)
        self._create_toolbar(root)

    def _create_menu(self, root):
        """
        Create a menu bar with items for loading templates,
        saving/exporting flowcharts, and exiting the app.
        """
        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=self.canvas_manager.clear)
        filemenu.add_command(label="Save", command=self.save)
        filemenu.add_separator()
        filemenu.add_command(label="Export PNG", command=lambda: self._export(export_png))
        filemenu.add_command(label="Export PDF", command=lambda: self._export(export_pdf))
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        templatemenu = tk.Menu(menubar, tearoff=0)
        for name in TEMPLATES:
            templatemenu.add_command(label=name, command=lambda n=name: self.canvas_manager.load_template(TEMPLATES[n]))
        menubar.add_cascade(label="Templates", menu=templatemenu)
        root.config(menu=menubar)

    def _create_toolbar(self, root):
        """
        Create a toolbar with buttons for adding each shape type.
        """
        
        toolbar = tk.Frame(root)
        for tool in ["Rectangle", "Circle", "Diamond", "Connect"]:
            btn = tk.Button(toolbar, text=tool, command=lambda t=tool: self.canvas_manager.start_adding(t.lower()))
            btn.pack(side=tk.LEFT, padx=2, pady=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)

    def save(self):
        """
        Open a file dialog for saving the current flowchart to a JSON file.
        After selecting a file path, show a message box confirming the save.
        """
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files","*.json")])
        if path:
            self.canvas_manager.save(path)
            messagebox.showinfo("Save", f"Project saved to {path}")

    def _export(self, fn):
        """
        Open a file dialog for saving the current flowchart to a file using
        the given export function.

        :param fn: The export function to use. Should take two arguments:
            `canvas_widget` and `path`.
        """
        path = filedialog.asksaveasfilename()
        if path:
            fn(self.canvas_manager.canvas, path)
            messagebox.showinfo("Export", f"Exported to {path}")

def main():
    root = tk.Tk()
    app = FlowGenApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
