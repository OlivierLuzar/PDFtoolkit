"""
images_to_pdf.py

Łączy pliki JPG/JPEG/PNG z folderu input/ w jeden wielostronicowy plik PDF.

Przykład:
    python images_to_pdf.py
    python images_to_pdf.py --output skany.pdf
    python images_to_pdf.py --input-dir ./input --output-dir ./output
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageOps

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def find_images(input_dir: Path) -> list[Path]:
    """Zwraca posortowaną listę obrazów z katalogu wejściowego."""
    if not input_dir.exists():
        raise FileNotFoundError(f"Folder input nie istnieje: {input_dir}")

    images = [
        path for path in input_dir.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    return sorted(images, key=lambda path: path.name.lower())


def load_as_rgb(image_path: Path) -> Image.Image:
    """Wczytuje obraz, uwzględnia orientację EXIF i konwertuje go do RGB."""
    image = Image.open(image_path)
    image = ImageOps.exif_transpose(image)

    if image.mode in {"RGBA", "LA"}:
        background = Image.new("RGB", image.size, "white")
        alpha_channel = image.getchannel("A") if "A" in image.getbands() else None
        background.paste(image.convert("RGBA"), mask=alpha_channel)
        return background

    return image.convert("RGB")


def images_to_pdf(image_paths: Iterable[Path], output_path: Path) -> Path:
    """Zapisuje obrazy jako jeden wielostronicowy PDF."""
    image_paths = list(image_paths)
    if not image_paths:
        raise ValueError("Brak plików JPG/JPEG/PNG w folderze input.")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    first_image, *remaining_paths = image_paths
    first = load_as_rgb(first_image)
    rest = [load_as_rgb(path) for path in remaining_paths]

    first.save(output_path, save_all=True, append_images=rest)
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Łączenie obrazów JPG/PNG w jeden PDF.")
    parser.add_argument("--input-dir", default="input", help="Folder z obrazami wejściowymi.")
    parser.add_argument("--output-dir", default="output", help="Folder na wynikowy PDF.")
    parser.add_argument("--output", default="merged.pdf", help="Nazwa wynikowego pliku PDF.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_path = Path(args.output_dir) / args.output

    images = find_images(input_dir)
    result = images_to_pdf(images, output_path)

    print(f"Zapisano: {result}")
    print(f"Liczba połączonych obrazów: {len(images)}")


if __name__ == "__main__":
    main()
