#!/usr/bin/env python3
import re
import sys
from pathlib import Path

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <input.c> <output.c>")
    sys.exit(1)

text = Path(sys.argv[1]).read_text()
out = []

# Match any vfmadd132sd instruction inside inline asm
vfmadd132sd_re = re.compile(
    r'vfmadd132sd\s+%%xmm\d+\s*,\s*%%xmm\d+\s*'
)

for line in text.splitlines():
    if vfmadd132sd_re.search(line):
        out.append(
            vfmadd132sd_re.sub(
                'vfmadd132sd %%xmm0, %%xmm0',
                line
            )
        )
    else:
        out.append(line)

Path(sys.argv[2]).write_text("\n".join(out))
