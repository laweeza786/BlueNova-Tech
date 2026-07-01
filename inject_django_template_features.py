import os

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(base_dir, 'backend', 'templates')
    
    sync_code = """
    {% if request.user.is_authenticated %}
    <script>
        localStorage.setItem("erp_users", '{{ json_users|escapejs }}');
        localStorage.setItem("erp_files", '{{ json_files|escapejs }}');
        localStorage.setItem("erp_notifications", '{{ json_notifications|escapejs }}');
        localStorage.setItem("erp_messages", '{{ json_messages|escapejs }}');
        localStorage.setItem("erp_logs", '{{ json_logs|escapejs }}');
        localStorage.setItem("erp_history", '{{ json_history|escapejs }}');
        localStorage.setItem("erp_session", '{{ session_token }}');
    </script>
    {% endif %}
    """
    
    for file_name in os.listdir(templates_dir):
        if file_name.endswith('.html'):
            file_path = os.path.join(templates_dir, file_name)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 1. Inject Sync script right after <body> tag
            if '<body>' in content:
                content = content.replace('<body>', '<body>\n' + sync_code)
                
            # 2. Inject CSRF Token right after any <form> tag
            # We look for <form ...> and replace with <form ...>\n{% csrf_token %}
            # Let's do it by finding <form and searching for the closing >
            idx = 0
            while True:
                idx = content.find('<form', idx)
                if idx == -1:
                    break
                close_idx = content.find('>', idx)
                if close_idx == -1:
                    break
                
                # Check if csrf_token is already there
                if '{% csrf_token %}' not in content[close_idx:close_idx+30]:
                    content = content[:close_idx+1] + '\n{% csrf_token %}\n' + content[close_idx+1:]
                idx = close_idx + 15
                
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"Processed template: {file_name}")

if __name__ == '__main__':
    main()
