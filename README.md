# inv-pdf

[![PyPI version](https://badge.fury.io/py/inv-pdf.svg)](https://pypi.org/project/inv-pdf/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub](https://img.shields.io/badge/GitHub-Santt997%2Finv--colors-181717?logo=github)](https://github.com/Santt997/inv-colors)

> Invert PDF colors (dark-mode) for a file or entire directory — with parallel processing across CPU cores.

---

## The Problem

Reading white-background PDFs at night or on OLED screens is painful. `inv-pdf` inverts every page of a PDF to produce a dark-mode version, with near-black pixels clamped to pure black to avoid muddy greys.

---

## Installation

```bash
pip install inv-pdf
```

**Dependencies:** `pymupdf` and `Pillow` are installed automatically.

---

## Usage

### CLI

```bash
# Invert all PDFs in current directory (creates file_inverted.pdf for each)
inv-pdf .

# Specify output directory
inv-pdf ./pdfs -o ./dark-pdfs

# Custom DPI, suffix, and parallelism
inv-pdf ./pdfs --dpi 150 --suffix _dark --jobs 4

# Full help
inv-pdf --help
```

### Python API

```python
from inv_pdf import invert_pdf

# Invert a single PDF
invert_pdf("document.pdf", "document_inverted.pdf", dpi=300)
```

---

## Options

| Flag | Default | Description |
|---|---|---|
| `DIR` | `.` | Directory of PDFs to process |
| `-o / --output` | Same as input | Output directory |
| `-s / --suffix` | `_inverted` | Suffix added to output filenames |
| `-d / --dpi` | `300` | Render resolution (higher = better quality, slower) |
| `-j / --jobs` | CPU count | Number of parallel worker processes |
| `--ext` | `.pdf` | File extension to match |

---

## How It Works

1. Opens each PDF with **PyMuPDF** (`pymupdf`)
2. Rasterises each page at the specified DPI
3. Inverts pixel values: `255 − x` for each RGB channel via **Pillow**
4. Clamps near-black pixels (all channels < 100) to pure `(0, 0, 0)`
5. Re-encodes each page as PNG and embeds it back into a new PDF
6. Preserves the original TOC and metadata
7. Saves with `deflate=True, garbage=4, clean=True` for compact output

---

## Requirements

- Python 3.8+
- `pymupdf >= 1.23.0`
- `Pillow >= 9.0.0`

---

## License

MIT © [Santt997](https://github.com/Santt997)
