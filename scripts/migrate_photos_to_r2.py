#!/usr/bin/env python3
"""
Scan project images, convert to WebP, optionally upload to Cloudflare R2,
and write data/photos.json.

Usage:
  python scripts/migrate_photos_to_r2.py
  python scripts/migrate_photos_to_r2.py --upload
  python scripts/migrate_photos_to_r2.py --upload --delete-originals
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import boto3
from PIL import Image, ImageOps, UnidentifiedImageError
from pillow_heif import register_heif_opener

register_heif_opener()

DAY_RE = re.compile(r"day\s*([1-7])", re.IGNORECASE)
DEFAULT_EXTENSIONS = ".jpg,.jpeg,.png,.gif,.heic,.heif"


@dataclass
class PhotoRecord:
    id: str
    filename: str
    title: str
    url: str
    day: int | None
    source: str
    key: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert local photos to WebP and optionally upload to Cloudflare R2."
    )
    parser.add_argument("--source-dir", default="images", help="Source image root")
    parser.add_argument("--output-dir", default="build/photos-webp", help="Converted WebP output dir")
    parser.add_argument("--photos-json", default="data/photos.json", help="Output photos json path")
    parser.add_argument("--quality", type=int, default=80, help="WebP quality (0-100)")
    parser.add_argument("--max-side", type=int, default=2400, help="Resize longest edge to this size (0 = no resize)")
    parser.add_argument("--r2-prefix", default="photos", help="R2 object key prefix")
    parser.add_argument("--extensions", default=DEFAULT_EXTENSIONS, help="Comma-separated source extensions")
    parser.add_argument("--upload", action="store_true", help="Upload converted files to R2")
    parser.add_argument("--delete-originals", action="store_true", help="Delete original files after successful upload")
    parser.add_argument("--clean-output", action="store_true", help="Delete output folder before converting")
    parser.add_argument("--skip-existing", action="store_true", help="Skip convert if destination webp exists")
    parser.add_argument("--limit", type=int, default=0, help="Convert first N files only (0 = all)")
    return parser.parse_args()


def parse_extensions(raw: str) -> set[str]:
    values = [item.strip().lower() for item in raw.split(",") if item.strip()]
    normalized = {item if item.startswith(".") else f".{item}" for item in values}
    return normalized


def discover_images(source_dir: Path, extensions: set[str]) -> List[Path]:
    files = [
        path
        for path in source_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in extensions
    ]
    return sorted(files)


def infer_day(rel_path: Path) -> int | None:
    for part in rel_path.parts:
        match = DAY_RE.search(part)
        if match:
            return int(match.group(1))

    match = DAY_RE.search(rel_path.stem)
    if match:
        return int(match.group(1))

    return None


def to_output_path(src: Path, source_root: Path, output_root: Path) -> Path:
    rel = src.relative_to(source_root)
    return (output_root / rel).with_suffix(".webp")


def to_key(output_file: Path, output_root: Path, prefix: str) -> str:
    rel = output_file.relative_to(output_root).as_posix()
    normalized_prefix = prefix.strip("/")
    return f"{normalized_prefix}/{rel}" if normalized_prefix else rel


def clean_output_dir(output_dir: Path) -> None:
    if not output_dir.exists():
        return

    for child in sorted(output_dir.rglob("*"), reverse=True):
        if child.is_file():
            child.unlink()
        elif child.is_dir():
            child.rmdir()


def convert_to_webp(src: Path, dst: Path, quality: int, max_side: int) -> Tuple[int, int, int]:
    dst.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(src) as image:
        image = ImageOps.exif_transpose(image)

        if max_side > 0 and max(image.width, image.height) > max_side:
            image.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)

        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA" if "A" in image.getbands() else "RGB")

        image.save(dst, "WEBP", quality=quality, method=6)

    size = dst.stat().st_size
    return image.width, image.height, size


def create_r2_client() -> Tuple[object, str, str]:
    account_id = os.getenv("R2_ACCOUNT_ID", "").strip()
    access_key = os.getenv("R2_ACCESS_KEY_ID", "").strip()
    secret_key = os.getenv("R2_SECRET_ACCESS_KEY", "").strip()
    bucket = os.getenv("R2_BUCKET_NAME", "").strip()
    public_url = os.getenv("R2_PUBLIC_URL", "").strip()

    endpoint = f"https://{account_id}.r2.cloudflarestorage.com" if account_id else ""

    missing = [
        name
        for name, value in {
            "R2_ACCOUNT_ID": account_id,
            "R2_ACCESS_KEY_ID": access_key,
            "R2_SECRET_ACCESS_KEY": secret_key,
            "R2_BUCKET_NAME": bucket,
            "R2_PUBLIC_URL": public_url,
        }.items()
        if not value
    ]
    if missing:
        raise ValueError(f"Missing required env vars: {', '.join(missing)}")

    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
    )
    return client, bucket, public_url.rstrip("/")


def upload_files(client, bucket: str, output_and_key: List[Tuple[Path, str]]) -> None:
    total = len(output_and_key)
    for index, (output_file, key) in enumerate(output_and_key, start=1):
        content_type = mimetypes.guess_type(output_file.name)[0] or "application/octet-stream"
        client.upload_file(
            str(output_file),
            bucket,
            key,
            ExtraArgs={
                "ContentType": content_type,
                "CacheControl": "public, max-age=31536000, immutable",
            },
        )

        if index % 100 == 0 or index == total:
            print(f"[UPLOAD {index}/{total}] {key}")


def write_photos_json(path: Path, records: List[PhotoRecord]) -> None:
    payload = [
        {
            "id": record.id,
            "filename": record.filename,
            "title": record.title,
            "url": record.url,
            "day": record.day,
            "source": record.source,
            "key": record.key,
        }
        for record in records
    ]

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def delete_original_files(files: List[Path]) -> None:
    for file_path in files:
        file_path.unlink(missing_ok=True)


def main() -> int:
    args = parse_args()

    source_dir = Path(args.source_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    photos_json_path = Path(args.photos_json).resolve()

    if not source_dir.exists():
        print(f"[ERROR] Source dir not found: {source_dir}")
        return 1

    if args.delete_originals and not args.upload:
        print("[ERROR] --delete-originals requires --upload")
        return 1

    extensions = parse_extensions(args.extensions)

    if args.clean_output:
        clean_output_dir(output_dir)

    source_files = discover_images(source_dir, extensions)
    if args.limit > 0:
        source_files = source_files[: args.limit]

    if not source_files:
        print("[WARN] No matching image files found.")
        return 0

    print(f"[INFO] Found {len(source_files)} files in {source_dir}")

    converted_items: List[Tuple[Path, Path, str, int | None, str]] = []
    errors: List[Tuple[Path, str]] = []
    skipped = 0
    total_size = 0

    for index, src in enumerate(source_files, start=1):
        rel_source = src.relative_to(source_dir)
        day = infer_day(rel_source)
        output_path = to_output_path(src, source_dir, output_dir)
        key = to_key(output_path, output_dir, args.r2_prefix)
        source_ref = f"./{src.relative_to(Path.cwd()).as_posix()}"

        if args.skip_existing and output_path.exists():
            skipped += 1
            converted_items.append((src, output_path, key, day, source_ref))
            continue

        try:
            width, height, size = convert_to_webp(src, output_path, args.quality, args.max_side)
            total_size += size
            converted_items.append((src, output_path, key, day, source_ref))
            if index % 100 == 0 or index == len(source_files):
                print(f"[CONVERT {index}/{len(source_files)}] {src.name} -> {output_path.name} ({width}x{height})")
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            errors.append((src, str(exc)))
            print(f"[WARN] Skip {src}: {exc}")

    records: List[PhotoRecord] = []
    width = max(3, len(str(len(converted_items))))
    for idx, (_src, output_path, key, day, source_ref) in enumerate(converted_items, start=1):
        photo_id = str(idx).zfill(width)
        title = output_path.stem.replace("_", " ").replace("-", " ")
        records.append(
            PhotoRecord(
                id=photo_id,
                filename=output_path.name,
                title=title,
                url="",
                day=day,
                source=source_ref,
                key=key,
            )
        )

    uploaded = False
    if args.upload:
        client, bucket, public_url = create_r2_client()
        upload_files(client, bucket, [(item[1], item[2]) for item in converted_items])
        for record in records:
            record.url = f"{public_url}/{record.key}"
        uploaded = True

    write_photos_json(photos_json_path, records)

    if args.delete_originals:
        delete_original_files([item[0] for item in converted_items])

    print(f"[OK] Converted files: {len(converted_items)}")
    print(f"[OK] Skipped existing: {skipped}")
    print(f"[OK] Failed files: {len(errors)}")
    print(f"[OK] Total converted size: {total_size / (1024 * 1024):.2f} MB")
    print(f"[OK] photos.json: {photos_json_path}")
    print(f"[OK] Uploaded: {'yes' if uploaded else 'no'}")
    if args.delete_originals:
        print(f"[OK] Original files deleted: {len(converted_items)}")

    if errors:
        print("[WARN] Failed examples:")
        for src, message in errors[:10]:
            print(f"  - {src}: {message}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
