"""
Exporters - PDF Export for ComicCraft.
Compiles comic panels and narration into a downloadable PDF file.
"""
import os
from pathlib import Path
from datetime import datetime
from fpdf import FPDF


# Directory for saving exported PDFs
BASE_DIR = Path(__file__).resolve().parent.parent
EXPORTS_DIR = BASE_DIR / "static" / "exports"
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


class ComicPDF(FPDF):
    """Custom PDF class for ComicCraft comics."""

    def header(self):
        """Add header to each page."""
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, 'ComicCraft - AI Comic Story Creator', 0, 1, 'C')
        self.ln(2)

    def footer(self):
        """Add footer with page number."""
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')


def save_pdf(layout: list, title: str = "ComicCraft Comic") -> str:
    """
    Compile the full comic into a multi-page PDF file.

    Args:
        layout: List of panel dictionaries from build_comic_layout()
        title: Title for the comic

    Returns:
        Relative file path to the saved PDF (for use in HTML templates)
    """
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"comic_{timestamp}.pdf"
    filepath = EXPORTS_DIR / filename
    relative_path = f"/static/exports/{filename}"

    try:
        pdf = ComicPDF()
        pdf.alias_nb_pages()
        pdf.set_auto_page_break(auto=True, margin=20)

        # Title page
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 28)
        pdf.set_text_color(45, 27, 105)
        pdf.ln(40)
        pdf.cell(0, 20, title, 0, 1, 'C')
        pdf.set_font('Helvetica', '', 14)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 10, 'Created with ComicCraft AI', 0, 1, 'C')
        pdf.cell(0, 10, datetime.now().strftime("%B %d, %Y"), 0, 1, 'C')

        # Add each panel as a page
        for panel in layout:
            pdf.add_page()

            # Panel title
            pdf.set_font('Helvetica', 'B', 18)
            pdf.set_text_color(45, 27, 105)
            panel_title = f"Panel {panel.get('panel_number', '')}: {panel.get('title', '')}"
            pdf.cell(0, 12, panel_title, 0, 1, 'C')
            pdf.ln(5)

            # Panel image
            image_path = panel.get('image_path', '')
            if image_path:
                # Convert relative path to absolute
                abs_image_path = BASE_DIR / image_path.lstrip('/')
                if abs_image_path.exists():
                    try:
                        # Calculate image dimensions to fit page width
                        page_width = pdf.w - 2 * pdf.l_margin
                        img_width = min(page_width, 170)
                        x_pos = (pdf.w - img_width) / 2
                        pdf.image(str(abs_image_path), x=x_pos, w=img_width)
                        pdf.ln(5)
                    except Exception as img_err:
                        print(f"Error adding image to PDF: {img_err}")

            # Scene description
            scene_desc = panel.get('scene_description', '')
            if scene_desc:
                pdf.set_font('Helvetica', 'I', 11)
                pdf.set_text_color(80, 80, 80)
                pdf.multi_cell(0, 6, scene_desc)
                pdf.ln(3)

            # Panel story text
            text = panel.get('text', '')
            if text:
                pdf.set_font('Helvetica', '', 11)
                pdf.set_text_color(40, 40, 40)
                # Clean text for PDF (remove markdown formatting)
                clean_text = text.replace('**', '').replace('*', '')
                clean_text = clean_text.replace('##', '').replace('#', '')
                pdf.multi_cell(0, 6, clean_text)

        # Save PDF
        pdf.output(str(filepath))
        print(f"PDF saved: {filepath}")
        return relative_path

    except Exception as e:
        print(f"Error creating PDF: {e}")
        raise
