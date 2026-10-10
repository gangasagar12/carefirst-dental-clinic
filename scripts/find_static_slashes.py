import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

base_dir = Path(__file__).resolve().parent.parent
templates_dir = base_dir / 'templates'

total = 0
for html_file in templates_dir.rglob('*.html'):
    try:
        content = html_file.read_text(encoding='utf-8', errors='ignore')
        matches = re.finditer(r'{%\s*static\s+[\'\"](/[^\'\"]+)[\'\"]\s*%}', content)
        found = list(matches)
        if found:
            print(f"\n{html_file.relative_to(base_dir)}:")
            for m in found:
                total += 1
                print(f"  Line {content[:m.start()].count('\n') + 1}: {m.group(0)}")
    except Exception as e:
        print(f"Error {html_file}: {e}")

print(f"\nTotal invalid static references with leading slash: {total}")
