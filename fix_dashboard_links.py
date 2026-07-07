import os
import re

directories = [
    r'c:\Users\Win11\Downloads\erp\erp\backend',
    r'c:\Users\Win11\Downloads\erp\erp\frontend'
]

replacements = [
    (r'window\.location\.href\s*=\s*"admin-dashboard\.html"', r'window.location.href = "/erp/admin-dashboard/"'),
    (r'window\.location\.href\s*=\s*"dashboard\.html"', r'window.location.href = "/erp/dashboard/"')
]

for directory in directories:
    for root, _, files in os.walk(directory):
        if 'venv' in root:
            continue
        for file in files:
            if file.endswith('.html') or file.endswith('.js'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                for pattern, replacement in replacements:
                    content = re.sub(pattern, replacement, content)
                
                if content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Updated {file} at {filepath}")

print("Done fixing dashboard redirects.")
