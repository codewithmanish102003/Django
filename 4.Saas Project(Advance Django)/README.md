# SaaS Project: Team Task Manager

A web-based SaaS application for teams to manage tasks, collaborate, and handle subscriptions. This project is designed to help you learn advanced Django concepts through hands-on development.

---

## Project Overview

**Team Task Manager** allows organizations to:
- Sign up and create an organization (tenant)
- Invite team members
- Create, assign, and track tasks within their organization
- Upgrade to paid plans for advanced features (e.g., unlimited projects, file attachments)
- Access an admin dashboard for managing users and billing

---

## Key Features & Learning Goals

| Feature                        | Django Concepts/Skills Learned                |
|--------------------------------|----------------------------------------------|
| User registration/login        | Custom user model, authentication            |
| Organization/Team management   | Multi-tenancy, related models                |
| Task/project management        | CRUD, permissions, class-based views         |
| Team invitations               | Email, tokens, signals                       |
| Subscription & billing         | Stripe integration, webhooks, plans          |
| Role-based permissions         | Django permissions, groups                   |
| REST API (optional)            | Django REST Framework                        |
| Background tasks (optional)    | Celery, async email sending                  |
| Testing                        | Unit/integration tests                       |
| Deployment                     | Static/media, environment variables          |

---

## Suggested MVP (Minimum Viable Product) Steps

1. **Project Setup**
   - Create Django project and core apps (`accounts`, `organizations`, `tasks`, `billing`)
2. **User & Organization Models**
   - Custom user model, organization/team model, user-organization relationship
3. **Authentication**
   - Registration, login, password reset, email verification
4. **Task Management**
   - CRUD for tasks, assign to users, organization scoping
5. **Team Invitations**
   - Invite by email, accept invitation flow
6. **Subscription & Billing**
   - Integrate Stripe, handle plans, restrict features for free users
7. **Admin Panel**
   - Manage users, organizations, tasks, billing
8. **Testing & Deployment**
   - Write tests, deploy to Heroku or similar

---

## Initial Project Structure

```
saas_project/
  manage.py
  saas_project/
    __init__.py
    settings.py
    urls.py
    wsgi.py
    asgi.py
  accounts/           # User authentication, registration, profiles
    __init__.py
    models.py
    views.py
    urls.py
    ...
  organizations/      # Organization/team management, invitations
    __init__.py
    models.py
    views.py
    urls.py
    ...
  tasks/              # Task and project management
    __init__.py
    models.py
    views.py
    urls.py
    ...
  billing/            # Subscription, payments, Stripe integration
    __init__.py
    models.py
    views.py
    urls.py
    ...
  templates/
    ...
  static/
    ...
  requirements.txt
  README.md
```

- Each app (`accounts`, `organizations`, `tasks`, `billing`) is responsible for a core domain of the SaaS platform.
- `templates/` and `static/` hold your HTML, CSS, and JS assets.
- `requirements.txt` lists your dependencies.

---

## Recommended Packages
- `django-allauth` (authentication)
- `django-rest-framework`
- `dj-stripe` (Stripe integration)
- `django-tenant-schemas` or `django-tenants` (multi-tenancy)
- `celery` (background tasks)
- `django-environ` (env variables)

---

## Learning Resources
- [Django SaaS Boilerplate](https://github.com/MicroPyramid/django-saas-boilerplate)
- [Django Stripe Tutorial](https://testdriven.io/blog/django-stripe-subscriptions/)
- [Django Tenants Docs](https://django-tenants.readthedocs.io/en/latest/)

---

## Next Steps
1. Scaffold the project structure
2. Implement user and organization models
3. Build features step by step, learning advanced Django as you go!

---

**Happy coding!** 