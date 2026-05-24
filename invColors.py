from __future__ import annotations

import argparse
import multiprocessing
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from io import BytesIO
from pathlib import Path

import pymupdf
from PIL import Image


def invert_pdf(
    input_path: str,
    output_path: str,
    dpi: int = 300
) -> None:

    doc = pymupdf.open(input_path)
    new_doc = pymupdf.open()

    try:

        for page_num in range(len(doc)):

            page = doc[page_num]

            scale = dpi / 72.0

            mat = pymupdf.Matrix(
                scale,
                scale
            )

            pix = page.get_pixmap(
                matrix=mat,
                alpha=False
            )

            img = Image.frombytes(
                "RGB",
                [pix.width, pix.height],
                pix.samples
            )

            # invert
            img = Image.eval(
                img,
                lambda x: 255 - x
            )

            # pure black cleanup
            pixels = img.load()

            width, height = img.size

            threshold = 100

            for y in range(height):
                for x in range(width):

                    r, g, b = pixels[x, y]

                    if (
                        r < threshold
                        and g < threshold
                        and b < threshold
                    ):
                        pixels[x, y] = (0, 0, 0)

            # save temp PNG in memory
            buffer = BytesIO()

            img.save(
                buffer,
                format="PNG"
            )

            img_bytes = buffer.getvalue()

            # create page
            new_page = new_doc.new_page(
                width=page.rect.width,
                height=page.rect.height
            )

            new_page.insert_image(
                new_page.rect,
                stream=img_bytes
            )

        # TOC
        try:

            toc = doc.get_toc()

            if toc:
                new_doc.set_toc(toc)

        except Exception:
            pass

        # metadata
        try:

            new_doc.set_metadata(
                doc.metadata
            )

        except Exception:
            pass

        new_doc.save(
            output_path,
            deflate=True,
            garbage=4,
            clean=True
        )

    finally:

        new_doc.close()
        doc.close()


def process_pdf(
    args: tuple[str, str, int]
) -> tuple[bool, str, str, str | None]:

    input_path, output_path, dpi = args

    try:

        invert_pdf(
            input_path,
            output_path,
            dpi
        )

        return (
            True,
            input_path,
            output_path,
            None
        )

    except Exception as e:

        return (
            False,
            input_path,
            output_path,
            str(e)
        )


def main() -> None:

    parser = argparse.ArgumentParser(
        description='Invert PDF colors'
    )

    parser.add_argument(
        'dir',
        nargs='?',
        default='.'
    )

    parser.add_argument(
        '-o',
        '--output',
        default=None
    )

    parser.add_argument(
        '-s',
        '--sufix',
        default='_inverted'
    )

    parser.add_argument(
        '-d',
        '--dpi',
        type=int,
        default=300
    )

    parser.add_argument(
        '-j',
        '--jobs',
        type=int,
        default=multiprocessing.cpu_count()
    )

    parser.add_argument(
        '--ext',
        default='.pdf'
    )

    args = parser.parse_args()

    input_dir = Path(
        args.dir
    ).resolve()

    if not input_dir.exists():

        print(
            f"Error: '{input_dir}' does not exist"
        )

        sys.exit(1)

    output_dir = (
        Path(args.output).resolve()
        if args.output
        else input_dir
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    pdfs = sorted(
        input_dir.glob(f'*{args.ext}')
    )

    pdfs = [
        p for p in pdfs
        if not p.name.endswith(
            f'{args.sufix}{args.ext}'
        )
    ]

    if not pdfs:

        print('No PDFs found')

        sys.exit(0)

    print(
        f'Finded {len(pdfs)} PDF(s) 4process'
    )

    print(
        f'DPI of renderized: {args.dpi}'
    )

    print(
        f'Parallel jobs: {args.jobs}'
    )

    print('-' * 50)

    tasks: list[
        tuple[str, str, int]
    ] = []

    for pdf_path in pdfs:

        output_name : str = (
            f'{pdf_path.stem}'
            f'{args.sufix}'
            f'{args.ext}'
        )

        output_path = (
            output_dir / output_name
        )

        if output_path.exists():
            continue

        tasks.append(
            (
                str(pdf_path),
                str(output_path),
                args.dpi
            )
        )

    success_count: int = 0
    failed_count: int = 0

    with ProcessPoolExecutor(
        max_workers=args.jobs
    ) as executor:

        futures = {
            executor.submit(
                process_pdf,
                task
            ): task
            for task in tasks
        }

        for future in as_completed(futures):

            success, input_path, output_path, error = (
                future.result()
            )

            name = Path(
                input_path
            ).name

            if success:

                print(
                    f'✅ {name} -> '
                    f'{Path(output_path).name}'
                )

                success_count += 1

            else:

                print(
                    f'❌ {name}: {error}'
                )

                failed_count += 1

    print('-' * 50)

    print(
        f'Process fulled: '
        f'{success_count} success, '
        f'{failed_count} failed'
    )

    if failed_count > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()