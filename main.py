#!/usr/bin/env python3
import os
import shutil
import struct
from pathlib import Path


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_SIZE = 1048576


def validate_png(path: Path) -> dict:
    data = path.read_bytes()
    size = len(data)
    result = {
        "path": str(path),
        "exists": path.exists(),
        "size": size,
        "size_ok": size <= MAX_SIZE,
        "png_signature_ok": data.startswith(PNG_SIGNATURE),
        "ihdr_ok": False,
        "width": None,
        "height": None,
    }
    if len(data) >= 24 and data.startswith(PNG_SIGNATURE):
        # IHDR chunk: length(4) + type(4)="IHDR" + width(4) + height(4)
        chunk_type = data[12:16]
        if chunk_type == b"IHDR":
            width, height = struct.unpack(">II", data[16:24])
            result["width"] = width
            result["height"] = height
            result["ihdr_ok"] = width == 1024 and height == 1024
    result["valid"] = (
        result["exists"]
        and result["size_ok"]
        and result["png_signature_ok"]
        and result["ihdr_ok"]
    )
    return result


def print_validation(result: dict) -> None:
    print(f"path: {result['path']}")
    print(f"size: {result['size']}")
    print(f"size_ok: {result['size_ok']}")
    print(f"png_signature_ok: {result['png_signature_ok']}")
    print(f"width: {result['width']}")
    print(f"height: {result['height']}")
    print(f"ihdr_ok: {result['ihdr_ok']}")
    print(f"valid: {result['valid']}")


def check_mode(out_dir: Path) -> int:
    dst = out_dir / "entry.png"
    if not dst.exists():
        print(f"path: {dst}")
        print("valid: False")
        print("error: output file does not exist")
        return 1
    result = validate_png(dst)
    print_validation(result)
    return 0 if result["valid"] else 1


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Write or validate ramen entry image.")
    parser.add_argument("--check", action="store_true", help="Only validate existing output file")
    args = parser.parse_args()

    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.check:
        return check_mode(out_dir)

    repo_root = Path(__file__).resolve().parent
    src = repo_root / "food.png"
    dst = out_dir / "entry.png"

    shutil.copyfile(src, dst)

    result = validate_png(dst)
    print_validation(result)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())