import os

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(base_dir, 'backend', 'templates')
    
    for file_name in os.listdir(templates_dir):
        if file_name.endswith('.html'):
            file_path = os.path.join(templates_dir, file_name)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if 'href="/erp/settings/"' in content:
                content = content.replace('href="/erp/settings/"', 'href="{% url \'settings\' %}"')
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                print(f"Updated settings URL tag in template: {file_name}")

if __name__ == '__main__':
    main()
