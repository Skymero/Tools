"""
Module to generate PDF reports of extracted website content.
"""

import os
from fpdf import FPDF

class WebsiteContentPDF(FPDF):
    """Custom PDF class for website content reports."""
    
    def __init__(self):
        super().__init__()
        self.title = "Website Content Report"
        self.set_auto_page_break(auto=True, margin=15)
    
    def header(self):
        # Set up header with title
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, self.title, ln=True, align="C")
        self.ln(5)
    
    def footer(self):
        # Add page number at the bottom
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")
    
    def chapter_title(self, title):
        # Add a chapter title
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, ln=True)
        self.ln(5)
    
    def chapter_body(self, content, max_length=5000):
        # Add chapter body text with reasonable truncation
        self.set_font("Arial", "", 10)
        
        # Truncate very long content to avoid PDF generation issues
        if len(content) > max_length:
            content = content[:max_length] + "...\n[Content truncated due to length]"
            
        # Replace tabs with spaces for better formatting
        content = content.replace("\t", "    ")
        
        # Handle Unicode characters by replacing them with ASCII equivalents or removing them
        content = self._sanitize_text(content)
            
        # Output the text with line breaks preserved
        self.multi_cell(0, 5, content)
        self.ln(5)
    
    def _sanitize_text(self, text):
        """Sanitize text to be compatible with FPDF's latin-1 encoding."""
        # Create a mapping of common Unicode characters to their ASCII equivalents
        replacements = {
            '\u2013': '-',  # en dash
            '\u2014': '--',  # em dash
            '\u2018': "'",  # left single quote
            '\u2019': "'",  # right single quote
            '\u201c': '"',  # left double quote
            '\u201d': '"',  # right double quote
            '\u2022': '*',  # bullet
            '\u2026': '...',  # ellipsis
            '\u21e7': '^',  # upwards white arrow
            '\u25b2': '^',  # black up-pointing triangle
            '\u25bc': 'v',  # black down-pointing triangle
            '\u2192': '->',  # rightwards arrow
            '\u2190': '<-',  # leftwards arrow
            '\u00a9': '(c)',  # copyright sign
            '\u00ae': '(R)',  # registered sign
            '\u00b0': 'deg',  # degree sign
            '\u00b1': '+/-',  # plus-minus sign
        }
        
        # Replace known problematic characters
        for unicode_char, replacement in replacements.items():
            text = text.replace(unicode_char, replacement)
        
        # Remove any remaining non-latin1 characters
        text = ''.join(c if ord(c) < 256 else ' ' for c in text)
        
        return text
    
    def add_file_content(self, file_path, title=None):
        """Add the content of a file to the PDF."""
        # Skip if file doesn't exist
        if not os.path.exists(file_path):
            return False
            
        # Use filename as title if none provided
        if title is None:
            title = os.path.basename(file_path)
        
        try:
            # Read file content
            is_binary = file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))
            
            if is_binary:
                # For binary image files, add as image
                self.chapter_title(f"Image: {title}")
                try:
                    self.image(file_path, x=10, w=180)
                    self.ln(5)
                except Exception as e:
                    self.chapter_body(f"[Could not render image: {str(e)}]")
            else:
                # For text files, add as text
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    self.chapter_title(title)
                    self.chapter_body(content)
                except UnicodeDecodeError:
                    # If we can't decode as text, it might be binary after all
                    self.chapter_title(title)
                    self.chapter_body("[Binary content - not displayed]")
                except Exception as e:
                    self.chapter_title(title)
                    self.chapter_body(f"[Error reading file: {str(e)}]")
            
            return True
        except Exception as e:
            print(f"Error adding file {file_path} to PDF: {str(e)}")
            return False

def generate_pdf(extracted_files, output_path):
    """
    Generate a PDF report of the extracted website content.
    
    Args:
        extracted_files (dict): Dictionary of extracted file paths by type
        output_path (str): Path where to save the PDF report
        
    Returns:
        bool: True if PDF generation was successful, False otherwise
    """
    try:
        print(f"Starting PDF generation, output path: {output_path}")
        print(f"Files to include: {extracted_files}")
        
        # Create PDF object
        pdf = WebsiteContentPDF()
        pdf.title = "Website Content Extraction Report - Lupin the 1st"
        
        # Add information page
        pdf.add_page()
        pdf.chapter_title("Extraction Summary")
        
        summary_text = "This report contains the extracted content from the website.\n\n"
        summary_text += "Files extracted:\n"
        
        # Add count of files by type
        for file_type, files in extracted_files.items():
            if files:
                summary_text += f"- {file_type.upper()}: {len(files)} files\n"
        
        pdf.chapter_body(summary_text)
        
        # Add HTML content
        if extracted_files.get('html'):
            print(f"Adding HTML content: {len(extracted_files['html'])} files")
            pdf.add_page()
            pdf.chapter_title("HTML Content")
            for html_file in extracted_files['html']:
                try:
                    pdf.add_file_content(html_file)
                except Exception as e:
                    print(f"Error adding HTML file {html_file}: {str(e)}")
                    pdf.chapter_body(f"[Error processing file: {str(e)}]")
        
        # Add CSS content
        if extracted_files.get('css'):
            print(f"Adding CSS content: {len(extracted_files['css'])} files")
            pdf.add_page()
            pdf.chapter_title("CSS Content")
            for css_file in extracted_files['css']:
                try:
                    pdf.add_file_content(css_file)
                except Exception as e:
                    print(f"Error adding CSS file {css_file}: {str(e)}")
                    pdf.chapter_body(f"[Error processing file: {str(e)}]")
        
        # Add JavaScript content
        if extracted_files.get('js'):
            print(f"Adding JavaScript content: {len(extracted_files['js'])} files")
            pdf.add_page()
            pdf.chapter_title("JavaScript Content")
            for js_file in extracted_files['js']:
                try:
                    pdf.add_file_content(js_file)
                except Exception as e:
                    print(f"Error adding JS file {js_file}: {str(e)}")
                    pdf.chapter_body(f"[Error processing file: {str(e)}]")
        
        # Add images
        if extracted_files.get('images'):
            print(f"Adding images: {len(extracted_files['images'])} files")
            pdf.add_page()
            pdf.chapter_title("Images")
            for image_file in extracted_files['images'][:10]:  # Limit to first 10 images
                try:
                    pdf.add_file_content(image_file)
                except Exception as e:
                    print(f"Error adding image file {image_file}: {str(e)}")
                    pdf.chapter_body(f"[Error processing file: {str(e)}]")
            
            if len(extracted_files['images']) > 10:
                pdf.chapter_body(f"[{len(extracted_files['images']) - 10} more images not shown]")
        
        # Output the PDF
        print(f"Writing PDF to {output_path}")
        pdf.output(output_path)
        print(f"PDF generation complete: {output_path}")
        return True
    except Exception as e:
        print(f"Error generating PDF report: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
