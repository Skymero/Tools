from PIL import ImageGrab
from reportlab.pdfgen import canvas as pdf_canvas
import tempfile
import os

# Export functions for FlowGen

def export_png(canvas_widget, path):
    """Export the given canvas to a PNG file."""
    # Save canvas as postscript then convert
    ps = canvas_widget.postscript(colormode='color')
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.ps')
    tmp.write(ps.encode('utf-8'))
    tmp.close()
    img = ImageGrab.grabclipboard() if False else ImageGrab.grab(bbox=None)
    # Fallback: convert via postscript
    os.system(f'gs -q -dNOPAUSE -dBATCH -sDEVICE=pngalpha -sOutputFile="{path}" "{tmp.name}"')

def export_pdf(canvas_widget, path):
    """Export the given canvas to a PDF file."""
    ps = canvas_widget.postscript(colormode='color')
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.ps')
    tmp.write(ps.encode('utf-8'))
    tmp.close()
    c = pdf_canvas.Canvas(path)
    c.drawImage(tmp.name, 0, 0)
    c.showPage()
    c.save()
