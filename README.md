# 🐕 Pet Care Booker

A full-stack Django application for booking trusted pet care services in Leicester. Features user authentication, booking management, and secure Stripe payments.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Demo](#demo)
- [Screenshots](#screenshots)
- [Folder Structure](#folder-structure)
- [Tech Stack](#tech-stack)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [Testing](#testing)
- [Acknowledgements](#acknowledgements)
- [Attributions](#attributions)

## Overview

Pet Care Booker is a responsive web application that connects pet owners in Leicester with trusted local carers for dog walking, grooming, and boarding services. Users can create accounts, book services, make secure payments via Stripe, and manage their bookings.

**Live Demo**: https://pet-care-booker-62152b813817.herokuapp.com/

## Features

- User authentication (signup/login/logout)
- Service browsing (dog walking, grooming, boarding)
- Booking creation with date/time selection
- Secure Stripe checkout integration
- CRUD operations for bookings (create/read/update/delete)
- Responsive design (mobile-first Bootstrap 5)
- Django admin panel for content management

## Demo

### User Journey
1. **Guest**: View services → Signup
2. **Logged In**: Book service → Pay with Stripe → Manage bookings
3. **Admin**: Full CRUD via Django admin

## Screenshots

### Guest Experience
[![01 Home Logged Out](screenshots/01-home-logged-out.png)](https://pet-care-booker-62152b813817.herokuapp.com/)
[![02 Signup Page](screenshots/02-signup-page.png)](https://pet-care-booker-62152b813817.herokuapp.com/signup/)

### Authenticated Experience
[![03 Home Logged In](screenshots/03-home-logged-in.png)](https://pet-care-booker-62152b813817.herokuapp.com/)
[![04 Services Page](screenshots/04-services-page.png)](https://pet-care-booker-62152b813817.herokuapp.com/services/)

### Booking Flow (CRUD)
[![05 Booking Form Empty](screenshots/05-booking-form-empty.png)](https://pet-care-booker-62152b813817.herokuapp.com/book/)
[![06 Booking Form Filled](screenshots/06-booking-form-filled.png)](https://pet-care-booker-62152b813817.herokuapp.com/book/)
[![07 Booking Confirmation](screenshots/07-booking-form-confirmation.png)](https://pet-care-booker-62152b813817.herokuapp.com/book/?booking_id=1)
[![08 Stripe Checkout](screenshots/08-stripe-checkout.png)](https://pet-care-booker-62152b813817.herokuapp.com/create-checkout-session/)

### Dashboard & Management
[![09 Bookings Paid](screenshots/09-booking-page-paid.png)](https://pet-care-booker-62152b813817.herokuapp.com/bookings/)
[![10 Profile Page](screenshots/10-profile-page.png)](https://pet-care-booker-62152b813817.herokuapp.com/profile/)

### CRUD Operations & Mobile
[![11 Edit Booking](screenshots/11-booking-form-edit.png)](https://pet-care-booker-62152b813817.herokuapp.com/bookings/)
[![12 Delete Booking](screenshots/12-booking-form-delete.png)](https://pet-care-booker-62152b813817.herokuapp.com/booking/1/edit/)
[![13 Mobile Responsive Home](screenshots/13-mobile-responsiveness-home.png)](https://pet-care-booker-62152b813817.herokuapp.com/booking/1/delete/)
[![14 Mobile Responsive Services](screenshots/14-mobile-responsiveness-services.png)](https://pet-care-booker-62152b813817.herokuapp.com/)

## Folder Structure
pet-care-booker/
├── accounts/ # Main app (views, models, templates)
│ ├── migrations/
│ ├── static/
│ ├── templates/
│ └── admin.py
├── pet_care_booker/ # Project settings
├── screenshots/ # Demo screenshots
├── Procfile # Heroku process types
├── requirements.txt # Python dependencies
└── README.md

## Tech Stack

| Frontend | Backend | Database | Deployment | Payments |
|----------|---------|----------|------------|----------|
| HTML5, Bootstrap 5, Crispy Forms | Django 5.0, Python 3.12 | PostgreSQL | Heroku | Stripe |
| jQuery, Vanilla JS | Gunicorn WSGI | SQLite (dev) | Whitenoise (static) | |

## Environment Variables
Create `.env` file:
DEBUG=False
SECRET_KEY=your-super-secret-key-here
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
DATABASE_URL=postgres://...

## Deployment

### Heroku
1) heroku create pet-care-booker-62152b813817
2) heroku addons:create heroku-postgresql:hobby-dev
3) heroku config:set SECRET_KEY=...
4) git push heroku main
5) heroku run python manage.py migrate

## Local Setup

```bash
# Clone & Setup
git clone <repo-url>
cd pet-care-booker
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install
pip install -r requirements.txt

# Migrate
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Run
python manage.py runserver


