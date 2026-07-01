import os
import shutil

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(base_dir, 'frontend')
    backend_dir = os.path.join(base_dir, 'backend')
    
    templates_dir = os.path.join(backend_dir, 'templates')
    static_css_dir = os.path.join(backend_dir, 'static', 'css')
    static_js_dir = os.path.join(backend_dir, 'static', 'js')
    
    # Create target folders if they do not exist
    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(static_css_dir, exist_ok=True)
    os.makedirs(static_js_dir, exist_ok=True)
    
    # Copy Static Assets
    shutil.copy2(
        os.path.join(frontend_dir, 'css', 'style.css'),
        os.path.join(static_css_dir, 'style.css')
    )
    shutil.copy2(
        os.path.join(frontend_dir, 'js', 'app.js'),
        os.path.join(static_js_dir, 'app.js')
    )
    shutil.copy2(
        os.path.join(frontend_dir, 'js', 'mockData.js'),
        os.path.join(static_js_dir, 'mockData.js')
    )
    
    print("Static assets copied to backend static folder.")
    
    # List of replacements for URL mapping in HTML templates
    replacements = {
        'href="css/style.css"': 'href="/static/css/style.css"',
        'src="js/mockData.js"': 'src="/static/js/mockData.js"',
        'src="js/app.js"': 'src="/static/js/app.js"',
        
        'href="index.html"': 'href="/"',
        'href="about.html"': 'href="/about/"',
        'href="contact.html"': 'href="/contact/"',
        'href="404.html"': 'href="/404/"',
        
        'href="login.html"': 'href="/auth/login/"',
        'href="signup.html"': 'href="/auth/signup/"',
        'href="forgot-password.html"': 'href="/auth/forgot-password/"',
        'href="reset-password.html"': 'href="/auth/reset-password/"',
        'href="logout.html"': 'href="/auth/logout/"',
        
        'href="dashboard.html"': 'href="/erp/dashboard/"',
        'href="admin-dashboard.html"': 'href="/erp/admin-dashboard/"',
        'href="profile.html"': 'href="/erp/profile/"',
        'href="edit-profile.html"': 'href="/erp/edit-profile/"',
        'href="upload-files.html"': 'href="/erp/upload-files/"',
        'href="user-management.html"': 'href="/erp/user-management/"',
        'href="messages.html"': 'href="/erp/messages/"',
        'href="history.html"': 'href="/erp/history/"',
        'href="notifications.html"': 'href="/erp/notifications/"',
        'href="activity-logs.html"': 'href="/erp/activity-logs/"',
        'href="data-management.html"': 'href="/erp/data-management/"',
        'href="help-center.html"': 'href="/erp/help-center/"',
        'href="feedback.html"': 'href="/erp/feedback/"',
        'href="reports.html"': 'href="/erp/reports/"',
        'href="search.html"': 'href="/erp/search/"',
        'href="settings.html"': 'href="{% url \'settings\' %}"',
        'href="analytics.html"': 'href="/erp/analytics/"',
        'action="search.html"': 'action="/erp/search/"',
    }
    
    # Process & Copy HTML pages
    for file_name in os.listdir(frontend_dir):
        if file_name.endswith('.html'):
            src_path = os.path.join(frontend_dir, file_name)
            dst_path = os.path.join(templates_dir, file_name)
            
            with open(src_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Execute search-replace operations
            for key, val in replacements.items():
                content = content.replace(key, val)
                
            with open(dst_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"Template {file_name} integrated.")

if __name__ == '__main__':
    main()
