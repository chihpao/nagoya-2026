#!/usr/bin/env python3
"""
Convert local album images to WebP, upload to Cloudflare R2, and generate manifest.json.

Example:
  python scripts/build_album_manifest_and_upload.py --upload
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import boto3
from PIL import Image, ImageOps
from pillow_heif import register_heif_opener

register_heif_opener()

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".avif"}
DAY_RE = re.compile(r"day(\d+)", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert album images to WebP, optionally upload to R2, and generate manifest."
    )
    parser.add_argument("--source-dir", default="images/album", help="Source album directory")
    parser.add_argument("--output-dir", default="build/album-webp", help="Output directory for converted WebP files")
    parser.add_argument("--manifest-path", default="data/manifest.json", help="Output manifest JSON path")
    parser.add_argument("--quality", type=int, default=78, help="WebP quality (0-100)")
    parser.add_argument("--max-side", type=int, default=2400, help="Max width/height in pixels")
    parser.add_argument("--r2-prefix", default="album", help="R2 key prefix for uploaded images")
    parser.add_argument("--public-base-url", default=os.getenv("R2_PUBLIC_BASE_URL", ""), help="Public URL base used in manifest")
    parser.add_argument("--upload", action="store_true", help="Upload output files to R2")
    parser.add_argument("--clean-output", action="store_true", help="Remove existing output directory before conversion")
    parser.add_argument("--skip-existing", action="store_true", help="Skip conversion when destination WebP already exists")
    parser.add_argument("--limit", type=int, default=0, help="Convert first N files only (0 = no limit)")
    return parser.parse_args()


def find_day(path: Path) -> str:
    for part in path.parts:
        m = DAY_RE.fullmatch(part)
        if m:
            return m.group(1)

    m = DAY_RE.match(path.stem)
    if m:
        return m.group(1)

    return "unknown"


def discover_images(source_dir: Path) -> List[Path]:
    files = [
        p
        for p in source_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    ]
    return sorted(files)


def to_output_path(source_path: Path, source_root: Path, output_root: Path) -> Path:
    rel = source_path.relative_to(source_root)
    return (output_root / rel).with_suffix(".webp")


def convert_one(src: Path, dst: Path, quality: int, max_side: int) -> Tuple[int, int, int]:
    dst.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(src) as img:
        img = ImageOps.exif_transpose(img)
        if max(img.width, img.height) > max_side:
            img.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)

        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA" if "A" in img.getbands() else "RGB")

        img.save(dst, "WEBP", quality=quality, method=6)
        return img.width, img.height, dst.stat().st_size


def build_manifest(
    converted: List[Tuple[Path, str]],
    output_dir: Path,
    r2_prefix: str,
    public_base_url: str,
) -> Dict[str, List[str]]:
    manifest: Dict[str, List[str]] = {str(i): [] for i in range(1, 8)}

    for output_file, day in converted:
        rel = output_file.relative_to(output_dir).as_posix()
        key = f"{r2_prefix.strip('/')}/{rel}" if r2_prefix else rel
        if public_base_url:
            value = f"{public_base_url.rstrip('/')}/{key}"
        else:
            value = f"./{output_file.as_posix()}"

        manifest.setdefault(day, []).append(value)

    for day in manifest:
        manifest[day].sort()
    return manifest


def create_r2_client() -> Tuple[object, str]:
    account_id = os.getenv("R2_ACCOUNT_ID", "").strip()
    access_key = os.getenv("R2_ACCESS_KEY_ID", "").strip()
    secret_key = os.getenv("R2_SECRET_ACCESS_KEY", "").strip()
    bucket = os.getenv("R2_BUCKET_NAME", "").strip()
    endpoint = os.getenv("R2_ENDPOINT_URL", "").strip()

    if not endpoint:
        if not account_id:
            raise ValueError("Missing R2_ACCOUNT_ID or R2_ENDPOINT_URL for upload")
        endpoint = f"https://{account_id}.r2.cloudflarestorage.com"

    missing = [k for k, v in {
        "R2_ACCESS_KEY_ID": access_key,
        "R2_SECRET_ACCESS_KEY": secret_key,
        "R2_BUCKET_NAME": bucket,
    }.items() if not v]
    if missing:
        raise ValueError(f"Missing required env vars for upload: {', '.join(missing)}")

    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
    )
    return client, bucket


def upload_files(
    client,
    bucket: str,
    converted: List[Tuple[Path, str]],
    output_dir: Path,
    r2_prefix: str,
    manifest_path: Path,
) -> None:
    for output_file, _day in converted:
        rel = output_file.relative_to(output_dir).as_posix()
        key = f"{r2_prefix.strip('/')}/{rel}" if r2_prefix else rel

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

    manifest_key = manifest_path.as_posix().lstrip("./")
    client.put_object(
        Bucket=bucket,
        Key=manifest_key,
        Body=manifest_path.read_bytes(),
        ContentType="application/json",
        CacheControl="public, max-age=60",
    )


def main() -> int:
    args = parse_args()

    source_dir = Path(args.source_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    manifest_path = Path(args.manifest_path).resolve()

    if not source_dir.exists():
        print(f"[ERROR] Source folder not found: {source_dir}")
        return 1

    if args.clean_output and output_dir.exists():
        for p in sorted(output_dir.rglob("*"), reverse=True):
            if p.is_file():
                p.unlink()
            elif p.is_dir():
                p.rmdir()

    files = discover_images(source_dir)
    if args.limit > 0:
        files = files[: args.limit]

    if not files:
        print("[WARN] No image files found.")
        return 0

    converted: List[Tuple[Path, str]] = []
    skipped = 0
    total_bytes = 0
    for idx, src in enumerate(files, start=1):
        day = find_day(src.relative_to(source_dir))
        dst = to_output_path(src, source_dir, output_dir)
        if args.skip_existing and dst.exists():
            skipped += 1
            converted.append((dst, day))
        else:
            width, height, size = convert_one(src, dst, args.quality, args.max_side)
            total_bytes += size
            converted.append((dst, day))
            if idx % 50 == 0 or idx == len(files):
                print(f"[{idx}/{len(files)}] converted: {src.name} -> {dst.name} ({width}x{height})")

    manifest = build_manifest(
        converted=converted,
        output_dir=output_dir,
        r2_prefix=args.r2_prefix,
        public_base_url=args.public_base_url,
    )
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[OK] Source files: {len(files)}")
    print(f"[OK] Converted now: {len(files) - skipped}")
    print(f"[OK] Skipped existing: {skipped}")
    print(f"[OK] Output folder: {output_dir}")
    print(f"[OK] Manifest: {manifest_path}")
    print(f"[OK] Total output size: {total_bytes / (1024 * 1024):.1f} MB")

    if args.upload:
        client, bucket = create_r2_client()
        upload_files(
            client=client,
            bucket=bucket,
            converted=converted,
            output_dir=output_dir,
            r2_prefix=args.r2_prefix,
            manifest_path=manifest_path,
        )
        print(f"[OK] Uploaded to R2 bucket: {bucket}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
