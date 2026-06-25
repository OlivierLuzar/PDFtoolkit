"""
compress_pdf.py

Kompresuje/oczyszcza plik PDF i zapisuje lżejszą kopię.

Skrypt używa PyMuPDF. Najczęściej daje dobre efekty dla PDF-ów zawierających obrazy
albo zbędne obiekty zapisane w pliku.

Przykład:
    python compress_pdf.py
    python compress_pdf.py --file dokument.pdf --output dokument_compressed.pdf
"""

from __future__ import annotations

import argparse
from pathlib import Path

import fitz  # PyMuPDF


def find_single_pdf(input_dir: Path) -> Path:
    """Znajduje pierwszy plik PDF w folderze wejściowym."""
    if not input_dir.exists():
        raise FileNotFoundError(f"Folder input nie istnieje: {input_dir}")

    pdfs = sorted(input_dir.glob("*.pdf"), key=lambda path: path.name.lower())
    if not pdfs:
        raise ValueError("Brak pliku PDF w folderze input.")

    return pdfs[0]


def format_size(size_bytes: int) -> str:
    """Zamienia liczbę bajtów na czytelny format."""
    units = ["B", "KB", "MB", "GB"]
    size = float(size_bytes)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size_bytes} B"


def compress_pdf(input_pdf: Path, output_pdf: Path) -> Path:
    """Zapisuje zoptymalizowaną wersję PDF-a."""
    if not input_pdf.exists():
        raise FileNotFoundError(f"Nie znaleziono pliku: {input_pdf}")

    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    document = fitz.open(input_pdf)
    document.save(
        output_pdf,
        garbage=4,
        deflate=True,
        clean=True,
    )
    document.close()

    return output_pdf


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Kompresja i optymalizacja pliku PDF.")
    parser.add_argument("--input-dir", default="input", help="Folder z wejściowym PDF-em.")
    parser.add_argument("--output-dir", default="output", help="Folder na skompresowany PDF.")
    parser.add_argument("--file", default=None, help="Konkretna nazwa pliku PDF z folderu input.")
    parser.add_argument("--output", default="compressed.pdf", help="Nazwa wynikowego pliku PDF.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)

    input_pdf = input_dir / args.file if args.file else find_single_pdf(input_dir)
    output_pdf = output_dir / args.output

    original_size = input_pdf.stat().st_size
    result = compress_pdf(input_pdf, output_pdf)
    compressed_size = result.stat().st_size

    if original_size > 0:
        ratio = 100 * (1 - compressed_size / original_size)
    else:
        ratio = 0

    print(f"Plik wejściowy: {input_pdf}")
    print(f"Plik wynikowy: {result}")
    print(f"Przed: {format_size(original_size)}")
    print(f"Po:    {format_size(compressed_size)}")
    print(f"Zmiana rozmiaru: {ratio:.2f}%")


if __name__ == "__main__":
    main()
