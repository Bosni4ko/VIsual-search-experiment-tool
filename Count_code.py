#!/usr/bin/env python3
import os

total = 0
for root, dirs, files in os.walk('.'):
    for fname in files:
        if fname.endswith('.py'):
            path = os.path.join(root, fname)
            with open(path, 'r', encoding='utf-8') as f:
                num = sum(1 for _ in f)
            print(f"{num:6}  {path}")
            total += num

print(f"\nTotal Python lines: {total}")
