# Complete Community Census & Matrimonial Platform Backend (Production Ready)

## Tech Stack
- Django
- Django REST Framework
- PostgreSQL
- JWT Authentication (email-based login)

## Features Included
- Hierarchical Location Management (Community -> State -> District -> Zone -> Vidhansabha -> Ward)
- Role-Based Access Control (super_admin, state_admin, etc.)
- Email+Password Authentication with simplejwt
- Family & Member Management (Nested serialization, soft delete)
- Matrimonial Feature for unmarried members
- Pagination & Search & Filtering

## Setup Guide

1. Create a Python Virtual Environment:
```bash
python -m venv venv
venv\Scripts\activate  # on Windows
```

2. Install Requirements:
```bash
pip install -r requirements.txt
```

3. Setup PostgreSQL:
- Create a Database named `census_db`
- User `postgres`, Password `password`
- Or, fallback to SQLite for immediate testing:
```bash
set USE_SQLITE=True
```

4. Run Migrations:
```bash
python manage.py makemigrations accounts community locations families members matrimonial
python manage.py migrate
```

5. Seed Super Admin:
```bash
python seed.py
```

6. Run Server:
```bash
python manage.py runserver
```

## API Testing Guide

### Auth
`POST /api/auth/login`
- body: `{"email": "admin@example.com", "password": "Password123!"}`
- returns JWT token with user_id, role, location_id.

### Locations (Super Admin only for create/update)
`GET /api/locations?type=state`

### Families
`GET /api/families` (Returns paginated {count, results} format with nested details)
`POST /api/families`
- nested members supported.

### Members
`GET /api/members?family_id=<id>`

### Matrimony
`POST /api/matrimonial/create`
`GET /api/matrimonial/list`
