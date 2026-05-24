"""
inv-pdf
=======
Invert PDF colors page-by-page with optional parallel processing.
Produces dark-mode versions of any PDF file.

Usage (CLI):
    inv-pdf /path/to/pdfs/
    inv-pdf /path/to/pdfs/ -o /output/ --dpi 150 --jobs 4

Usage (Python):
    from inv_pdf import invert_pdf
    invert_pdf("document.pdf", "document_inverted.pdf", dpi=300)
"""

__version__ = "0.1.0"
__author__ = "Santt997"
__license__ = "MIT"

from inv_pdf.cli import invert_pdf, process_pdf

__all__ = ["invert_pdf", "process_pdf", "__version__"]
