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
[![02 Signup Page](screenshots/02-signup-page-2.png)](https://pet-care-booker-62152b813817.herokuapp.com/signup/)

### Authenticated Experience
[![03 Home Logged In](screenshots/03-home-logged-in-3.png)](https://pet-care-booker-62152b813817.herokuapp.com/)
[![04 Services Page](screenshots/04-services-page-4.png)](https://pet-care-booker-62152b813817.herokuapp.com/services/)

### Booking Flow (CRUD)
[![05 Booking Form Empty](screenshots/05-booking-form-empty-5.png)](https://pet-care-booker-62152b813817.herokuapp.com/book/)
[![06 Booking Form Filled](screenshots/06-booking-form-filled-6.png)](https://pet-care-booker-62152b813817.herokuapp.com/book/)
[![07 Booking Confirmation](screenshots/07-booking-form-confirmation-7.png)](https://pet-care-booker-62152b813817.herokuapp.com/book/?booking_id=1)
[![08 Stripe Checkout](screenshots/08-stripe-checkout-8.png)](https://pet-care-booker-62152b813817.herokuapp.com/create-checkout-session/)

### Dashboard & Management
[![09 Bookings Paid](screenshots/09-booking-page-paid-9.png)](https://pet-care-booker-62152b813817.herokuapp.com/bookings/)
[![10 Profile Page](screenshots/10-profile-page-10.png)](https://pet-care-booker-62152b813817.herokuapp.com/profile/)

### CRUD Operations
[![11 Bookings List](screenshots/11-bookings-list.png)](https://pet-care-booker-62152b813817.herokuapp.com/bookings/)
[![12 Edit Booking](screenshots/12-edit-booking.png)](https://pet-care-booker-62152b813817.herokuapp.com/booking/1/edit/)
[![13 Delete Confirmation](screenshots/13-delete-confirm.png)](https://pet-care-booker-62152b813817.herokuapp.com/booking/1/delete/)
[![14 Mobile Responsive](screenshots/14-mobile-responsive.png)](https://pet-care-booker-62152b813817.herokuapp.com/)