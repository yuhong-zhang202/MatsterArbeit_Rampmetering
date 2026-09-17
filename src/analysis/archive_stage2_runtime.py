"""Create a verified, immutable local archive of one Stage 2 runtime tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
from datetime import datetime, timezone


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def inventory(root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        mode = path.lstat().st_mode
        relative = path.relative_to(root).as_posix()
        if stat.S_ISDIR(mode):
            continue
        if not stat.S_ISREG(mode) or path.is_symlink():
            raise ValueError(f"Unsupported archive entry: {relative}")
        rows.append(
            {
                "relative_path": relative,
                "size_bytes": path.stat().st_size,
                "sha256": digest(path),
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--archive-root", type=Path, required=True)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--batch-id", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()

    source = args.source.resolve(strict=True)
    if not source.is_dir():
        raise ValueError("Source runtime must be a directory")
    archive_root = args.archive_root.resolve()
    archive_root.mkdir(parents=True, exist_ok=True)
    final = archive_root / args.attempt_id
    partial = archive_root / f".{args.attempt_id}.partial"
    if final.exists() or partial.exists() or args.manifest.exists():
        raise FileExistsError("Archive destination, partial directory, or manifest exists")

    before = inventory(source)
    partial.mkdir()
    try:
        for row in before:
            relative = Path(str(row["relative_path"]))
            target = partial / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / relative, target)
            shutil.copystat(source / relative, target, follow_symlinks=False)
        after_source = inventory(source)
        archived = inventory(partial)
        if before != after_source:
            raise RuntimeError("Source changed during archive copy")
        if before != archived:
            raise RuntimeError("Archive size/hash inventory differs from source")
        os.rename(partial, final)
    except Exception:
        raise

    final_relative = final.relative_to(Path.cwd().resolve()).as_posix()
    file_map = [
        {
            "original_absolute_path": str(source / str(row["relative_path"])),
            "archive_relative_path": f"{final_relative}/{row['relative_path']}",
            "size_bytes": row["size_bytes"],
            "sha256": row["sha256"],
        }
        for row in before
    ]
    manifest = {
        "schema_version": 1,
        "batch_id": args.batch_id,
        "logical_run_id": args.run_id,
        "attempt_id": args.attempt_id,
        "source_runtime_path": str(source),
        "archive_runtime_relative_path": final_relative,
        "archive_status": "complete",
        "source_file_count": len(before),
        "archive_file_count": len(before),
        "source_hashes_stable_during_copy": True,
        "special_entries": [],
        "summary_present": (source / "summary.json").is_file(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "file_map": file_map,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"archive": str(final), "files": len(before), "manifest": str(args.manifest)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
