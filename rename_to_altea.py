#!/usr/bin/env python3
"""
Rename project to Altea
"""

import os
import re
from pathlib import Path

def replace_in_file(file_path, replacements):
    """Replace text in file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        modified = False
        for old, new in replacements.items():
            if old in content:
                content = content.replace(old, new)
                modified = True
        
        if modified:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"✓ Updated: {file_path}")
    except Exception as e:
        print(f"✗ Error in {file_path}: {e}")

def main():
    # Replacements mapping
    replacements = {
        'Altea': 'Altea',
        'Altea': 'Altea',
        'altea': 'altea',
        'altea': 'altea',
        'altea': 'altea',
        'Altea': 'Altea',
        'ALTEA': 'ALTEA',
        'Addiction Recovery & Wellness Tracking': 'Addiction Altea & Wellness Tracking',
        'altea': 'altea',
        'Altea Wellness': 'Altea Wellness',
        'Altea Wellness Center': 'Altea Wellness',
    }
    
    # File extensions to process
    extensions = ['.py', '.html', '.md', '.txt', '.yml', '.yaml', '.env.example', '.json']
    
    # Directories to skip
    skip_dirs = {'venv', 'env', '.git', '__pycache__', 'staticfiles', 'media', 'node_modules', '.pytest_cache'}
    
    # Process all files
    root_path = Path('.')
    for file_path in root_path.rglob('*'):
        if file_path.is_file():
            # Skip if in excluded directory
            if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
                continue
            
            # Process only relevant extensions
            if file_path.suffix in extensions or file_path.name in ['.env', 'Dockerfile']:
                replace_in_file(file_path, replacements)
    
    print("\n✅ Project renamed to Altea successfully!")
    print("\n📝 Next steps:")
    print("1. Update .env file with your settings")
    print("2. Review docker-compose.yml")
    print("3. Commit changes: git add . && git commit -m 'refactor: Rename project to Altea'")
    print("4. Push: git push")

if __name__ == '__main__':
    main()
