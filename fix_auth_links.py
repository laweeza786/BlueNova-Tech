import os
import re

directories = [
    r'c:\Users\Win11\Downloads\erp\erp\backend',
    r'c:\Users\Win11\Downloads\erp\erp\frontend'
]

html_replacements = [
    (r'href="login\.html"', r'href="{% url \'login\' %}"'),
    (r'href="signup\.html"', r'href="{% url \'signup\' %}"'),
    (r'href="forgot-password\.html"', r'href="{% url \'forgot_password\' %}"'),
    (r'href="reset-password\.html"', r'href="{% url \'reset_password\' %}"'),
    (r'action="login\.html"', r'action="{% url \'login\' %}"'),
    (r'action="signup\.html"', r'action="{% url \'signup\' %}"'),
    (r'window\.location\.href\s*=\s*"login\.html"', r'window.location.href = "/auth/login/"'),
    (r'window\.location\.href\s*=\s*"signup\.html"', r'window.location.href = "/auth/signup/"'),
    (r'window\.location\.href\s*=\s*"forgot-password\.html"', r'window.location.href = "/auth/forgot-password/"'),
    (r'window\.location\.href\s*=\s*"reset-password\.html"', r'window.location.href = "/auth/reset-password/"'),
    (r'/auth/signup/login\.html', r'/auth/login/'),
]

js_replacements = [
    (r'window\.location\.href\s*=\s*"login\.html"', r'window.location.href = "/auth/login/"'),
    (r'window\.location\.href\s*=\s*"signup\.html"', r'window.location.href = "/auth/signup/"'),
    (r'window\.location\.href\s*=\s*"forgot-password\.html"', r'window.location.href = "/auth/forgot-password/"'),
    (r'window\.location\.href\s*=\s*"reset-password\.html"', r'window.location.href = "/auth/reset-password/"'),
    (r'/auth/signup/login\.html', r'/auth/login/'),
]

for directory in directories:
    for root, _, files in os.walk(directory):
        if 'venv' in root:
            continue
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                for pattern, replacement in html_replacements:
                    content = re.sub(pattern, replacement, content)
                
                if content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Updated HTML: {filepath}")
            elif file.endswith('.js'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                for pattern, replacement in js_replacements:
                    content = re.sub(pattern, replacement, content)
                
                if content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Updated JS: {filepath}")

print("Done.")
