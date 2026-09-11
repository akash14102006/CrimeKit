#!/usr/bin/env python3
"""Scan repository working tree and print the top N largest files.
Usage: python tools/scan_large_files.py [N]
"""
import os
import sys

N = 50
if len(sys.argv) > 1:
    try:
        N = int(sys.argv[1])
    except Exception:
        pass

entries = []
for root, dirs, files in os.walk('.', topdown=True):
    # skip .git
    if '.git' in root.split(os.sep):
        continue
    for f in files:
        p = os.path.join(root, f)
        try:
            s = os.path.getsize(p)
            entries.append((s, p))
        except OSError:
            continue

entries.sort(reverse=True)
for s, p in entries[:N]:
    print(f"{s}\t{p.replace('\\\\','/')}")
