import os

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(base_dir, 'backend', 'templates')
    
    # List of files we need to fix
    for file_name in os.listdir(templates_dir):
        if file_name.endswith('.html'):
            file_path = os.path.join(templates_dir, file_name)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace relative settings link with absolute Django ERP setting path
            if 'href="settings.html"' in content:
                content = content.replace('href="settings.html"', 'href="/erp/settings/"')
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                print(f"Fixed link in: {file_name}")

if __name__ == '__main__':
    main()
