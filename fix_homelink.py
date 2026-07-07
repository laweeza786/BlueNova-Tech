import os, re

base = r'c:\Users\Win11\Downloads\erp\erp\backend\templates'
replacements = [
    (r'homeLink\.href\s*=\s*"admin-dashboard\.html"', 'homeLink.href = "/erp/admin-dashboard/"'),
    (r'homeLink\.href\s*=\s*"dashboard\.html"', 'homeLink.href = "/erp/dashboard/"'),
]

for fn in os.listdir(base):
    if not fn.endswith('.html'):
        continue
    fp = os.path.join(base, fn)
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    orig = content
    for pat, rep in replacements:
        content = re.sub(pat, rep, content)
    if content != orig:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(content)
        print('Fixed:', fn)
print('Done.')
