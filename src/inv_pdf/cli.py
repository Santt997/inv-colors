#!/usr/bin/env python3
"""
inv-pdf CLI
===========
Invert the colors of every page in a PDF file (or all PDFs in a directory),
producing dark-mode output files.  Processing is parallelised across CPU cores.

Dependencies:
    pip install pymupdf Pillow

Usage:
    inv-pdf [DIR] [-o OUTPUT_DIR] [-s SUFFIX] [-d DPI] [-j JOBS] [--ext EXT]
"""

from __future__ import annotations

import argparse
import multiprocessing
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from io import BytesIO
from pathlib import Path


def invert_pdf(
    input_path: str,
    output_path: str,
    dpi: int = 300,
) -> None:
    """
    Invert the colors of every page in a PDF and save the result.

    Each page is rasterised at *dpi* resolution, pixel values are
    negated (255 − x), near-black pixels are clamped to pure black,
    and the result is embedded back into a new PDF preserving the
    original page dimensions, TOC, and metadata.

    Args:
        input_path:  Path to the source PDF.
        output_path: Path where the inverted PDF will be written.
        dpi:         Render resolution in dots-per-inch (default 300).

    Raises:
        Any exception raised by pymupdf or Pillow propagates to the caller.
    """
    import pymupdf
    from PIL import Image

    doc = pymupdf.open(input_path)
    new_doc = pymupdf.open()

    try:
        for page_num in range(len(doc)):
            page = doc[page_num]
            scale = dpi / 72.0
            mat = pymupdf.Matrix(scale, scale)
            pix = page.get_pixmap(matrix=mat, alpha=False)

            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Invert all pixel values
            img = Image.eval(img, lambda x: 255 - x)

            # Clamp near-black pixels to pure black
            threshold = 100
            pixels = img.load()
            for y in range(img.height):
                for x in range(img.width):
                    r, g, b = pixels[x, y]
                    if r < threshold and g < threshold and b < threshold:
                        pixels[x, y] = (0, 0, 0)

            # Encode page as PNG in memory
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            img_bytes = buffer.getvalue()

            # Insert into new PDF at original dimensions
            new_page = new_doc.new_page(
                width=page.rect.width,
                height=page.rect.height,
            )
            new_page.insert_image(new_page.rect, stream=img_bytes)

        # Preserve TOC if present
        try:
            toc = doc.get_toc()
            if toc:
                new_doc.set_toc(toc)
        except Exception:
            pass

        # Preserve metadata
        try:
            new_doc.set_metadata(doc.metadata)
        except Exception:
            pass

        new_doc.save(output_path, deflate=True, garbage=4, clean=True)

    finally:
        new_doc.close()
        doc.close()


def process_pdf(
    args: tuple[str, str, int],
) -> tuple[bool, str, str, str | None]:
    """
    Worker function for parallel execution.

    Args:
        args: Tuple of (input_path, output_path, dpi).

    Returns:
        Tuple of (success, input_path, output_path, error_message_or_None).
    """
    input_path, output_path, dpi = args
    try:
        invert_pdf(input_path, output_path, dpi)
        return (True, input_path, output_path, None)
    except Exception as e:
        return (False, input_path, output_path, str(e))


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="inv-pdf",
        description="Invert PDF colors (dark-mode) for a file or all PDFs in a directory.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  inv-pdf .                          # invert all PDFs in current dir
  inv-pdf ./pdfs -o ./inverted       # write results to separate folder
  inv-pdf ./pdfs --dpi 150 --jobs 2  # lower DPI, 2 parallel workers
  inv-pdf ./pdfs --suffix _dark      # custom output file suffix
        """,
    )
    parser.add_argument(
        "dir",
        nargs="?",
        default=".",
        metavar="DIR",
        help="Directory containing PDF files to invert (default: current directory)",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        metavar="OUTPUT_DIR",
        help="Output directory (default: same as input directory)",
    )
    parser.add_argument(
        "-s", "--suffix",
        default="_inverted",
        metavar="SUFFIX",
        help="Suffix to append to output filenames (default: _inverted)",
    )
    parser.add_argument(
        "-d", "--dpi",
        type=int,
        default=300,
        metavar="DPI",
        help="Render resolution in DPI (default: 300)",
    )
    parser.add_argument(
        "-j", "--jobs",
        type=int,
        default=multiprocessing.cpu_count(),
        metavar="JOBS",
        help=f"Parallel worker processes (default: {multiprocessing.cpu_count()} = CPU count)",
    )
    parser.add_argument(
        "--ext",
        default=".pdf",
        metavar="EXT",
        help="File extension to process (default: .pdf)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )

    args = parser.parse_args()

    input_dir = Path(args.dir).resolve()
    if not input_dir.exists():
        print(f"Error: '{input_dir}' does not exist", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output).resolve() if args.output else input_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(input_dir.glob(f"*{args.ext}"))
    pdfs = [p for p in pdfs if not p.name.endswith(f"{args.suffix}{args.ext}")]

    if not pdfs:
        print("No PDFs found.")
        sys.exit(0)

    print(f"Found {len(pdfs)} PDF(s) to process")
    print(f"Render DPI: {args.dpi}")
    print(f"Parallel jobs: {args.jobs}")
    print("-" * 50)

    tasks = []
    for pdf_path in pdfs:
        out_name = f"{pdf_path.stem}{args.suffix}{args.ext}"
        out_path = output_dir / out_name
        if not out_path.exists():
            tasks.append((str(pdf_path), str(out_path), args.dpi))

    success_count = 0
    failed_count = 0

    with ProcessPoolExecutor(max_workers=args.jobs) as executor:
        futures = {executor.submit(process_pdf, task): task for task in tasks}
        for future in as_completed(futures):
            success, inp, outp, error = future.result()
            name = Path(inp).name
            if success:
                print(f"✅ {name} → {Path(outp).name}")
                success_count += 1
            else:
                print(f"❌ {name}: {error}")
                failed_count += 1

    print("-" * 50)
    print(f"Done: {success_count} succeeded, {failed_count} failed")

    if failed_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
