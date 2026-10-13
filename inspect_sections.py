import re

with open(r'docs/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
for i, line in enumerate(lines):
    if '<section' in line or '<nav' in line or '<header' in line:
        print(f"Line {i+1}: {line.strip()[:120]}")
    m = re.search(r'id=["\']([^"\']+)["\']', line)
    if m and ('section' in line.lower() or 'container' in line.lower() or 'hero' in line.lower() or 'warroom' in line.lower()):
        print(f"   [ID] {m.group(1)} (Line {i+1})")
