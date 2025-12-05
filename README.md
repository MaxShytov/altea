# Django Starter Template 🏥

> A production-ready Django starter template for workforce management applications

## 🎯 What's Included

### Core Features
- ✅ **Custom User Model** - Email-based authentication
- ✅ **Authentication System** - Login, Signup, Password Reset
- ✅ **Material Design 3 UI** - Beautiful, modern interface
- ✅ **Email Templates** - Extensible base template system
- ✅ **Dashboard Layout** - Sidebar, navbar, user menu
- ✅ **Docker Setup** - PostgreSQL, Redis, pgAdmin
- ✅ **Swiss Compliance** - Phone validation, timezone, country fields

### Tech Stack
- **Backend:** Django 5.0+, Python 3.12
- **Database:** PostgreSQL 15.8
- **Cache:** Redis 7.2
- **Frontend:** Bootstrap 5.3, Material Design 3
- **Container:** Docker & Docker Compose

### Project Structure
```markdown
project/ 
├── apps/ # Django applications 
│ ├── accounts/ # Authentication 
│ ├── dashboard/ # Main dashboard 
│ └── core/ # Shared utilities 
├── config/ # Django settings 
│ ├── settings/ │ │ ├── base.py 
│ │ ├── development.py 
│ │ └── production.py 
│ ├── urls.py 
│ ├── wsgi.py 
│ └── asgi.py 
├── templates/ # Global templates 
│ ├── base.html 
│ ├── layouts/ 
├── includes/ 
│ └── emails/ 
├── static/ # Static files 
├── docker-compose.yml # Development Docker 
└── requirements/ # Python dependencies

````

## 🚀 Quick Start

### Быстрый запуск (одна команда)

Убедитесь, что Docker Desktop запущен, затем выполните:

```bash
./start.sh

# Или если не работает:
bash start.sh
```

Скрипт автоматически:
- Создаст `.env` файл из примера
- Запустит Docker контейнеры (PostgreSQL, Redis)
- Создаст виртуальное окружение Python
- Установит все зависимости
- Применит миграции базы данных
- Запустит сервер разработки

После запуска:
- **Приложение:** http://127.0.0.1:8000
- **Админка:** http://127.0.0.1:8000/admin

**Суперадмин для локальной разработки:**
- Email: `admin@altea.com`
- Пароль: `password123`

Для создания нового суперпользователя (в новом терминале):
```bash
source venv/bin/activate
python manage.py createsuperuser
```

---

### Ручной запуск (пошагово)

#### 1. Clone the template
```bash
git clone https://github.com/yourusername/django-healthcare-starter.git my-new-project
cd my-new-project
rm -rf .git
git init
```

#### 2. Rename the project

Run the setup script:
```bash
python setup_project.py --name "MyProject" --slug "my_project"
```

Or manually:
1. Replace `medshift_` → `yourproject_` in Docker configs
2. Update `BASE_DIR` references if needed
3. Change project name in README

#### 3. Setup environment
```bash
# Copy environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

#### 4. Start Docker services

```bash
docker compose up -d
```

#### 5. Setup Django

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

#### 6. Access the application

- **App:** [http://localhost:8000](http://localhost:8000)
- **Admin:** [http://localhost:8000/admin](http://localhost:8000/admin)
- **pgAdmin:** [http://localhost:15433](http://localhost:15433) (admin@medshift.local / admin)

## 📝 Customization Guide

### Add New App

```bash
python manage.py startapp myapp apps/myapp
```

Then:

1. Add `'apps.myapp'` to `INSTALLED_APPS` in `config/settings/base.py`
2. Create templates in `apps/myapp/templates/myapp/`
3. Add URLs in `config/urls.py`

### Customize Email Templates

Extend `templates/emails/base_email.html`:
```html
{% extends "emails/base_email.html" %}

{% block email_content %}
<!-- Your content here -->
{% endblock %}
```

### Add New Settings

- **Common settings:** `config/settings/base.py`
- **Development only:** `config/settings/development.py`
- **Production only:** `config/settings/production.py`

## 🎨 UI Customization

### Colors

Edit `static/css/custom.css`:
```css
:root {
    --primary: #667eea;      /* Change primary color */
    --secondary: #764ba2;    /* Change secondary color */
}
```

### Logo
Replace logo in:
- `templates/layouts/auth_layout.html`
- `templates/layouts/dashboard_layout.html`

## 🐳 Docker Commands
```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f

# Restart services
docker compose restart

# Start with pgAdmin
docker compose --profile tools up -d
```

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=apps --cov-report=html

# Specific app
pytest apps/accounts/tests/
```

## 📦 Production Deployment

### 1. Update settings

Edit `.env`:
```bash
ENV_STAGE=production
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=yourdomain.com
```

### 2. Deploy with Docker Swarm
```bash
# Create secrets
echo "your-secret-key" | docker secret create django_secret_key -
echo "your-db-password" | docker secret create db_password -

# Deploy
ENV_STAGE=production docker stack deploy -c docker-compose-swarm.yaml myapp
```

## 🔐 Security Checklist

Before production:

- [ ]  Change `SECRET_KEY` in `.env`
- [ ]  Set `DEBUG=False`
- [ ]  Configure `ALLOWED_HOSTS`
- [ ]  Setup SSL/HTTPS
- [ ]  Configure production email backend
- [ ]  Enable security middleware
- [ ]  Setup Sentry for error tracking
- [ ]  Configure backups for PostgreSQL
- [ ]  Review CORS settings
- [ ]  Setup rate limiting

## 📚 What to Build Next

Common modules for healthcare/workforce apps:

1. **Employee Management** - CRUD, profiles, certifications
2. **Schedule Management** - Shift planning, calendar
3. **Time Tracking** - Clock-in/out, timesheet
4. **Leave Management** - Vacation requests, approvals
5. **Certification Tracking** - Medical licenses, expiry alerts
6. **Compliance** - Minimum staffing, break times
7. **Reports** - Labor costs, attendance, payroll

## 🤝 Contributing

This is a starter template. Feel free to:

- Fork and customize
- Submit improvements
- Share your projects built with this

## 🙏 Credits

Built with:

- Django
- Bootstrap
- Material Design
- Docker

---
### Шаг 5: Создать setup script для автоматической настройки
## **Ready to build something amazing?** 🚀

```
Создай `setup_project.py`:
```python
#!/usr/bin/env python
"""
Setup script for Django Healthcare Starter Template.
Renames project-specific references to your new project name.
"""

import os
import sys
import argparse
import re
from pathlib import Path


def replace_in_file(file_path, old_text, new_text):
    """Replace text in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        if old_text in content:
            content = content.replace(old_text, new_text)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"✓ Updated {file_path}")
    except Exception as e:
        print(f"✗ Error updating {file_path}: {e}")


def setup_project(project_name, project_slug):
    """
    Setup new project from template.
    
    Args:
        project_name: Human-readable project name (e.g., "My Clinic")
        project_slug: Snake_case slug (e.g., "my_clinic")
    """
    
    base_dir = Path.cwd()
    
    print(f"\n🚀 Setting up project: {project_name}")
    print(f"📦 Slug: {project_slug}\n")
    
    # Files to update
    files_to_update = [
        'docker-compose.yml',
        'docker-compose-swarm.yaml',
        '.env.example',
        'README.md',
        'config/settings/base.py',
    ]
    
    # Replacements
    replacements = {
        'medshift': project_slug,
        'MedShift Scheduler': project_name,
        'employee-scheduling-healthcare': f"{project_slug}-app",
        'employee_scheduling': project_slug,
    }
    
    # Apply replacements
    for file_path in files_to_update:
        full_path = base_dir / file_path
        if full_path.exists():
            for old, new in replacements.items():
                replace_in_file(full_path, old, new)
    
    print("\n✅ Project setup complete!")
    print(f"\nNext steps:")
    print(f"1. Review and update .env.example → .env")
    print(f"2. Run: docker compose up -d")
    print(f"3. Run: python manage.py migrate")
    print(f"4. Run: python manage.py createsuperuser")
    print(f"5. Start building! 🚀\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Setup Django Healthcare Starter Template'
    )
    parser.add_argument(
        '--name',
        required=True,
        help='Project name (e.g., "My Clinic System")'
    )
    parser.add_argument(
        '--slug',
        required=True,
        help='Project slug (e.g., "my_clinic")'
    )
    
    args = parser.parse_args()
    
    # Validate slug
    if not re.match(r'^[a-z][a-z0-9_]*$', args.slug):
        print("Error: Slug must be lowercase, start with a letter, and contain only letters, numbers, and underscores")
        sys.exit(1)
    
    setup_project(args.name, args.slug)
````

bash

```bash
chmod +x setup_project.py
```

---

### Шаг 6: Создать .gitignore для template
```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media/
staticfiles/

# Environment
.env
.env.local
.env.*.local
venv/
ENV/
env/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Docker
*.pid
*.seed

# Coverage
htmlcov/
.coverage
.coverage.*
coverage.xml
*.cover

# Testing
.pytest_cache/
.tox/

# Logs
logs/
*.log
EOF
```

---

### Шаг 7: Добавить LICENSE

```bash
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2025 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
```

---

### Шаг 8: Commit и push template

```bash
git add .
git commit -m "Initial commit: Django Healthcare Starter Template

Production-ready Django starter with:
- Custom User authentication
- Material Design 3 UI
- Email templates system
- Dashboard layout
- Docker setup (PostgreSQL, Redis)
- Swiss compliance fields
- Reusable project structure"

# Создай репозиторий на GitHub: django-healthcare-starter
git remote add origin https://github.com/yourusername/django-healthcare-starter.git
git branch -M main
git push -u origin main
```

---

## 🎯 Как использовать template для новых проектов

### Для нового проекта:
```bash
# 1. Клонировать template
git clone https://github.com/yourusername/django-healthcare-starter.git dental-clinic-app
cd dental-clinic-app

# 2. Удалить git history
rm -rf .git
git init

# 3. Запустить setup script
python setup_project.py --name "Dental Clinic Manager" --slug "dental_clinic"

# 4. Создать .env
cp .env.example .env
# Отредактировать .env

# 5. Запустить Docker
docker compose up -d

# 6. Setup Django
python -m venv venv
source venv/bin/activate
pip install -r requirements/development.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# 7. Первый commit нового проекта
git add .
git commit -m "Initial commit: Dental Clinic Manager"
git remote add origin https://github.com/yourusername/dental-clinic-app.git
git push -u origin main
```