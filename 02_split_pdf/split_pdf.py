"""
split_pdf.py

Dzieli jeden duży plik PDF na mniejsze pliki.

Obsługiwane tryby:
    1. Podział na N części:
       python split_pdf.py --parts 3

    2. Podział co K stron:
       python split_pdf.py --pages-per-file 5

Domyślnie skrypt szuka pierwszego pliku PDF w folderze input/ i zapisuje wyniki w output/.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from pypdf import PdfReader, PdfWriter


def find_single_pdf(input_dir: Path) -> Path:
    """Znajduje pierwszy plik PDF w folderze wejściowym."""
    if not input_dir.exists():
        raise FileNotFoundError(f"Folder input nie istnieje: {input_dir}")

    pdfs = sorted(input_dir.glob("*.pdf"), key=lambda path: path.name.lower())
    if not pdfs:
        raise ValueError("Brak pliku PDF w folderze input.")

    return pdfs[0]


def split_pdf(input_pdf: Path, output_dir: Path, pages_per_file: int) -> list[Path]:
    """Dzieli PDF co określoną liczbę stron."""
    if pages_per_file <= 0:
        raise ValueError("pages_per_file musi być dodatnią liczbą całkowitą.")

    reader = PdfReader(str(input_pdf))
    total_pages = len(reader.pages)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_files: list[Path] = []
    for start in range(0, total_pages, pages_per_file):
        writer = PdfWriter()
        end = min(start + pages_per_file, total_pages)

        for page_number in range(start, end):
            writer.add_page(reader.pages[page_number])

        part_number = len(output_files) + 1
        output_path = output_dir / f"part_{part_number:03d}.pdf"
        with output_path.open("wb") as file:
            writer.write(file)

        output_files.append(output_path)

    return output_files


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dzielenie pliku PDF na mniejsze części.")
    parser.add_argument("--input-dir", default="input", help="Folder z wejściowym PDF-em.")
    parser.add_argument("--output-dir", default="output", help="Folder na pocięte PDF-y.")
    parser.add_argument("--file", default=None, help="Konkretna nazwa pliku PDF z folderu input.")

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--parts", type=int, help="Liczba części, na które ma być podzielony PDF.")
    mode.add_argument("--pages-per-file", type=int, help="Liczba stron w jednym pliku wynikowym.")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)

    input_pdf = input_dir / args.file if args.file else find_single_pdf(input_dir)
    if not input_pdf.exists():
        raise FileNotFoundError(f"Nie znaleziono pliku: {input_pdf}")

    reader = PdfReader(str(input_pdf))
    total_pages = len(reader.pages)

    if args.parts:
        if args.parts <= 0:
            raise ValueError("parts musi być dodatnią liczbą całkowitą.")
        pages_per_file = math.ceil(total_pages / args.parts)
    else:
        pages_per_file = args.pages_per_file

    output_files = split_pdf(input_pdf, output_dir, pages_per_file)

    print(f"Plik wejściowy: {input_pdf}")
    print(f"Liczba stron: {total_pages}")
    print(f"Utworzono plików: {len(output_files)}")
    for path in output_files:
        print(f"- {path}")


if __name__ == "__main__":
    main()
