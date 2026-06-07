from jinja2 import Environment, FileSystemLoader
import os

env = Environment(loader=FileSystemLoader('app/templates'))

for root, dirs, files in os.walk('app/templates'):
    for f in files:
        if f.endswith('.html'):
            template_path = os.path.relpath(os.path.join(root, f), 'app/templates').replace('\\', '/')
            try:
                env.get_template(template_path)
                print(f"✓ {template_path}")
            except Exception as e:
                print(f"✗ {template_path}: {e}")
