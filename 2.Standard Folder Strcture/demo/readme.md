# Django + Tailwind CSS Setup Guide

This project demonstrates how to use [Tailwind CSS](https://tailwindcss.com/) with Django using the [django-tailwind](https://django-tailwind.readthedocs.io/) package.

## Prerequisites

- Python 3.8+
- Django 3.2+
- Node.js and npm (https://nodejs.org)

## Installation Steps

1. **Install Django and django-tailwind**

   ```sh
   pip install django django-tailwind
   ```

2. **Create your Django project and app**

   ```sh
   django-admin startproject demo
   cd demo
   python manage.py startapp website
   ```

3. **Add `tailwind` and your Tailwind app to `INSTALLED_APPS`**

   In `settings.py`:

   ```python
   INSTALLED_APPS = [
       # ... other apps ...
       'website',
       'tailwind',
       'theme',  # This will be your Tailwind app
   ]

   TAILWIND_APP_NAME = 'theme'
   ```

4. **Create the Tailwind app**

   ```sh
   python manage.py tailwind init theme
   ```

5. **Configure Tailwind app**

   In `theme/apps.py`, set:

   ```python
   class ThemeConfig(TailwindConfig):
       name = 'theme'
   ```

   In `theme/templates/`, create your base templates and use `{% tailwind_css %}` to load Tailwind styles.

6. **Install Node.js dependencies**

   ```sh
   cd theme
   npm install
   cd ..
   ```

7. **Build Tailwind CSS**

   For development (watch for changes):

   ```sh
   python manage.py tailwind start
   ```

   For production (build once):

   ```sh
   python manage.py tailwind build
   ```

8. **Use Tailwind in your templates**

   In your base template (e.g., `layout.html`):

   ```django
   {% load tailwind_tags %}
   <!DOCTYPE html>
   <html>
   <head>
       {% tailwind_css %}
   </head>
   <body>
       <!-- Your content -->
   </body>
   </html>
   ```

## Troubleshooting

- **Node.js/npm not found:**  
  Make sure Node.js and npm are installed and available in your PATH.  
  On Windows, you may need to set `NPM_BIN_PATH` in `settings.py`:

  ```python
  NPM_BIN_PATH = r"C:\Program Files\nodejs\npm.cmd"
  ```

- **TAILWIND_APP_NAME error:**  
  Ensure `TAILWIND_APP_NAME` is set to your Tailwind app name in `settings.py`.

## References

- [django-tailwind documentation](https://django-tailwind.readthedocs.io/)
- [Tailwind CSS documentation](https://tailwindcss.com/docs/installation)