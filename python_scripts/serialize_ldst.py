#!/usr/bin/env python3
import re
import sys

if len(sys.argv) != 3:
    print("Usage: python replace_movsd_zero.py input.asm output.asm")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file, 'r') as f:
    code = f.read()

# Replace all movsd instructions with memory offset to 0 and xmm0 register
# Matches lines like: movsd 16(%%rax), %%xmm1 or movsd %%xmm2, 24(%%rax)
pattern = re.compile(r'(movsd\s+)([^\s,]+),\s*([^\s\\]+)(\\n\\t\\t)?')

def replace_zero_offset(match):
    instr = match.group(1)
    src = match.group(2)
    dst = match.group(3)
    suffix = match.group(4) or ''

    # Determine if it's a load or store and set xmm0
    if dst.startswith('%%xmm'):
        # Load: memory -> xmm0
        src = '0(%%rax)'
        dst = '%%xmm0'
    else:
        # Store: xmm0 -> memory
        src = '%%xmm0'
        dst = '0(%%rax)'

    return f"{instr}{src}, {dst}{suffix}"

new_code = pattern.sub(replace_zero_offset, code)

with open(output_file, 'w') as f:
    f.write(new_code)

print(f"All movsd instructions replaced to use 0(%%rax) and %%xmm0 in {output_file}")
