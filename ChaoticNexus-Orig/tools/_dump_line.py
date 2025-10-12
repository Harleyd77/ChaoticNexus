from pathlib import Path

s = Path('src/powder_app/templates/nav.html').read_text(encoding='utf-8', errors='replace')
line = s.splitlines()[4]
print(repr(line))
for i, ch in enumerate(line):
    print(i, ch, hex(ord(ch)))

