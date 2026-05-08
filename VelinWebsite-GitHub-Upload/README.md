# Velin Flagship Website

Velin is a Django-based flagship website for NFC-powered digital business cards. The core flow is:

`create account -> verify email -> build profile -> get permanent public link -> share it through the Velin card`

This version includes:

- premium dark landing page
- real signup/login with optional Google sign-in
- email verification and GDPR-aware publish controls
- profile dashboard and live profile editor
- permanent public profile links
- products catalog with stock and pricing
- session-backed cart and order summary
- rebranded `Velin Administration Database`

## Stack

- Django 6
- SQLite for local development
- PostgreSQL-ready production configuration through `DATABASE_URL`
- django-allauth for Google sign-in
- Django admin for managing users, profiles, consent records, deletion requests, and products

## Local Setup

1. Install dependencies:
   `py -m pip install -r requirements.txt`
2. Run migrations:
   `py manage.py migrate`
3. Create an admin account:
   `py manage.py createsuperuser`
4. Start the server:
   `py manage.py runserver`

## Core Routes

- `/` landing page
- `/accounts/signup/`
- `/accounts/login/`
- `/accounts/password-reset/`
- `/dashboard/`
- `/dashboard/profile/`
- `/products/`
- `/cart/`
- `/p/<public_id>/`
- `/privacy/`
- `/terms/`
- `/admin/`

## Environment Variables

Copy `.env.example` into your own environment source and provide:

- `SECRET_KEY`
- `DEBUG`
- `SITE_URL`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `DATABASE_URL`
- `EMAIL_BACKEND`
- `DEFAULT_FROM_EMAIL`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`

## EU Hosting Notes

Recommended production setup:

- Django app hosted in an EU region
- managed PostgreSQL in the EU
- EU object storage for uploaded profile photos and pitch media
- HTTPS termination at the edge
- daily automated database backups and restore tests

For launch readiness, keep profiles private by default, verify email before publishing, and review privacy/legal text with counsel before going live.
