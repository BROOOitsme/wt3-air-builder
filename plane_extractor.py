#!/usr/bin/env python3
"""Extract a stock plane .blk from aces.vromfs.bin using wt_blk."""
import sys
from pathlib import Path

from wt_blk.vromf import Vromf
from wt_blk.blk import Blk

WT_DIR = Path.home() / ".local/share/Steam/steamapps/common/War Thunder"
ACES = WT_DIR / "aces.vromfs.bin"
OUTDIR = Path.home() / "wt-builder" / "extracted"
OUTDIR.mkdir(parents=True, exist_ok=True)

def main():
    if len(sys.argv) < 2:
        print("usage: extract_plane_wtblk.py <plane_id>")
        sys.exit(1)

    plane_id = sys.argv[1]
    print(f"Opening {ACES.name} …")

    vromf = Vromf(str(ACES))
    entry_path = f"gamedata/flightmodels/{plane_id}.blk"

    try:
        data = vromf.get_file(entry_path)
    except Exception as e:
        print(f"ERROR: {entry_path} not found in archive ({e})")
        sys.exit(1)

    out_blk = OUTDIR / f"{plane_id}.blk"
    out_blk.write_bytes(data)
    print(f"WROTE: {out_blk} ({len(data)} bytes)")

    try:
        blk = Blk(data)
        out_json = OUTDIR / f"{plane_id}.json"
        out_json.write_text(blk.to_json(), encoding="utf-8")
        print(f"WROTE: {out_json} (parsed BLK)")
    except Exception as e:
        print(f"Note: could not parse as BLK ({e}). Raw .blk still saved.")

if __name__ == "__main__":
    main()