#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Fill data/photos.json url from key with a public base URL.')
    parser.add_argument('--public-base', required=True, help='Example: https://<bucket>.<account>.r2.dev or https://img.example.com')
    parser.add_argument('--photos-json', default='data/photos.json')
    args = parser.parse_args()

    path = Path(args.photos_json)
    data = json.loads(path.read_text(encoding='utf-8'))
    base = args.public_base.rstrip('/')

    for item in data:
        key = str(item.get('key','')).lstrip('/')
        item['url'] = f"{base}/{key}" if key else ''

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"updated {len(data)} records in {path}")

if __name__ == '__main__':
    main()
