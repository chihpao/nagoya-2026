from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Optional

from PIL import Image, ExifTags
from pillow_heif import register_heif_opener

register_heif_opener()

ROOT = Path(".")
ALBUM_ROOT = ROOT / "images" / "album"
UNASSIGNED = ALBUM_ROOT / "unassigned"

DAY_MAP = {
    "20260401": 1,
    "20260402": 2,
    "20260403": 3,
    "20260404": 4,
    "20260405": 5,
    "20260406": 6,
    "20260407": 7,
}

DATE_TAGS = ("DateTimeOriginal", "DateTime", "DateTimeDigitized")
LOOKUP = {v: k for k, v in ExifTags.TAGS.items()}


def parse_date_yyyymmdd(value: str) -> Optional[str]:
    if not value:
        return None
    # EXIF format usually like 2026:04:01 12:47:02
    first = value.split(" ")[0].replace(":", "")
    if len(first) == 8 and first.isdigit():
        return first
    return None


def read_exif_date(file_path: Path) -> Optional[str]:
    try:
        with Image.open(file_path) as img:
            exif = img.getexif()
    except Exception:
        return None

    if not exif:
        return None

    for tag_name in DATE_TAGS:
        tag_id = LOOKUP.get(tag_name)
        if not tag_id:
            continue
        raw = exif.get(tag_id)
        if raw is None:
            continue
        date = parse_date_yyyymmdd(str(raw))
        if date:
            return date
    return None


def next_index_by_day() -> dict[int, int]:
    result: dict[int, int] = {}
    for day in range(1, 8):
        day_dir = ALBUM_ROOT / f"day{day}"
        day_dir.mkdir(parents=True, exist_ok=True)
        max_idx = 0
        for f in day_dir.iterdir():
            if not f.is_file():
                continue
            stem = f.stem.lower()
            prefix = f"day{day}-"
            if stem.startswith(prefix):
                try:
                    idx = int(stem.split("-")[-1])
                    if idx > max_idx:
                        max_idx = idx
                except ValueError:
                    pass
        result[day] = max_idx + 1
    return result


def main() -> None:
    if not UNASSIGNED.exists():
        print(f"unassigned folder not found: {UNASSIGNED}")
        return

    counters = next_index_by_day()
    moved = defaultdict(int)
    kept = 0

    files = sorted([f for f in UNASSIGNED.iterdir() if f.is_file()])
    for f in files:
        date = read_exif_date(f)
        if not date or date not in DAY_MAP:
            kept += 1
            continue

        day = DAY_MAP[date]
        idx = counters[day]
        counters[day] += 1

        ext = f.suffix.lower()
        target = ALBUM_ROOT / f"day{day}" / f"day{day}-{idx:04d}{ext}"
        f.rename(target)
        moved[day] += 1

    print("Reassigned by EXIF date:")
    for day in range(1, 8):
        print(f"day{day}\t{moved[day]}")
    print(f"unassigned_left\t{kept}")


if __name__ == "__main__":
    main()
