# SkillConnect ⚡
### A Student-Focused Social Marketplace & Portfolio Platform

SkillConnect is a full-stack web application designed for college campuses where talented students can showcase creative and technical skills through social portfolio posts, and fellow students or clients can discover, chat, book services, track order milestones, and leave verified reviews.

Built with **Python Django**, **MySQL**, **Vanilla JavaScript**, **HTML5**, and modern **CSS3**.

---

## 🌟 Key Features

1. **Role-Based Access**:
   - **Customer**: Discover talent, personalized recommendation feed, order services, real-time chat, visual order tracking, star ratings & reviews.
   - **Student / Service Provider**: Portfolio posting, service catalog management, college identity verification submission, order fulfilment workflow, earnings analytics.
   - **Platform Administrator**: Custom admin dashboard, student verification approval/rejection with ID preview, content moderation & report investigations, user suspension, category & skill management.

2. **Student Identity Verification**:
   - Students submit official college credentials (University name, Student ID / Roll number, course, year, college ID card upload).
   - Platform admins review credentials to grant the official **"Verified Student"** checkmark badge.

3. **Personalized Recommended Feed**:
   - Algorithmic feed prioritizing posts matching user's selected interests, followed student creators, and verified student posts.
   - Interactive AJAX like toggle (♥/♡), inline AJAX comment submission, and one-click clipboard share link with toast popups.

4. **Visual Order Tracking System**:
   - Real-time step progress tracker:
     `Requested` &rarr; `Accepted` &rarr; `In Progress` &rarr; `Ready` &rarr; `Completed` (or `Cancelled`/`Rejected`).
   - Audit trail log recording every timestamp and note.

5. **One-to-One Real-Time Chat**:
   - Built with pure Django backend endpoints and Vanilla JavaScript polling (every 3 seconds).
   - Instant messaging bubbles, unread counts, and chat initiator shortcuts directly from student profiles and order pages.

6. **Safety & Moderation**:
   - Integrated reporting system for Profiles, Posts, Comments, and Services.
   - Custom Admin moderation panel for fast dispute resolution.

---

## 📁 Project Folder Structure

```text
SE-SKILLCONNECT/
│
├── manage.py                   # Django management CLI
├── populate_db.py              # Automated database seeding script
├── requirements.txt            # Python dependencies
├── .env                        # Local environment variables (active)
├── .env.example                # Example environment variables template
├── README.md                   # Complete documentation
│
├── skillconnect/               # Project core configuration
│   ├── __init__.py             # PyMySQL initialization
│   ├── settings.py             # Database, apps, static & media settings
│   ├── urls.py                 # Master URL routing
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                   # Authentication, custom User model, profiles, verification
│   ├── models.py               # User, Profile, StudentProfile, CustomerProfile, Follow, Category, Skill
│   ├── forms.py                # Registration, login, profile edit, verification forms
│   ├── views.py                # Auth, profile, follow toggle, verification views
│   └── urls.py
│
├── core/                       # Public pages, search, recommendation feed
│   ├── models.py               # ContactMessage
│   ├── views.py                # Landing, home feed, search, about, contact
│   ├── tests.py                # Automated unit & workflow tests
│   └── urls.py
│
├── posts/                      # Portfolio posts, likes, comments
│   ├── models.py               # Post, PostLike, Comment
│   ├── forms.py                # Post and Comment forms
│   ├── views.py                # Post CRUD, AJAX like, AJAX comment
│   └── urls.py
│
├── services/                   # Service listings & catalog
│   ├── models.py               # Service
│   ├── forms.py                # Service creation & edit forms
│   ├── views.py                # Services list, detail, student management
│   └── urls.py
│
├── orders/                     # Booking, status transitions & visual tracker
│   ├── models.py               # Order, OrderStatusHistory
│   ├── forms.py                # Service booking form
│   ├── views.py                # Order booking, list, tracking stepper, status update
│   └── urls.py
│
├── chat/                       # One-to-one messaging & polling
│   ├── models.py               # Conversation, Message
│   ├── views.py                # Chat window, AJAX send, AJAX polling
│   └── urls.py
│
├── reviews/                    # Order ratings & written reviews
│   ├── models.py               # Review (1-5 stars)
│   ├── forms.py                # Review submission form
│   ├── views.py                # Create review view
│   └── urls.py
│
├── reports/                    # User & content reporting system
│   ├── models.py               # Report (User, Post, Comment, Service)
│   ├── forms.py                # Report form
│   ├── views.py                # Submit report view
│   └── urls.py
│
├── notifications/              # In-app notifications & badges
│   ├── models.py               # Notification
│   ├── views.py                # Notifications list, mark read
│   └── urls.py
│
├── admin_panel/                # Custom platform administrator dashboard
│   ├── views.py                # KPIs, user management, verifications, moderation
│   └── urls.py
│
├── templates/                  # Django HTML templates (37 templates)
│   ├── base.html               # Main layout with responsive navbar & footer
│   ├── core/                   # landing.html, home_feed.html, search.html, about.html, contact.html
│   ├── accounts/               # login.html, register.html, profile.html, edit_profile.html, verification.html, etc.
│   ├── posts/                  # post_detail.html, create_post.html, edit_post.html, manage_posts.html, etc.
│   ├── services/               # service_list.html, service_detail.html, create_service.html, etc.
│   ├── orders/                 # order_list.html, order_detail.html, book_service.html
│   ├── chat/                   # chat.html
│   ├── reviews/                # create_review.html
│   ├── reports/                # submit_report.html
│   ├── notifications/          # notification_list.html
│   └── admin_panel/            # dashboard.html, user_management.html, verifications.html, reports.html, etc.
│
├── static/                     # Static assets
│   ├── css/
│   │   └── style.css           # Clean, responsive CSS with original SkillConnect identity
│   └── js/
│       ├── main.js             # Vanilla JS: AJAX likes, comments, follows, toasts, clipboard share
│       └── chat.js             # Vanilla JS: real-time AJAX chat polling
│
└── media/                      # Uploaded media (profile pictures, posts, service images, ID cards)
```

---

## 🛠️ Prerequisites & Installation

### 1. Requirements
- **Python**: 3.10+ (Tested on Python 3.13)
- **MySQL Server**: 8.0 or later

### 2. Set Up Virtual Environment
```bash
# In the SE-SKILLCONNECT directory:
python -m venv .venv

# On Windows (PowerShell / Command Prompt):
.\.venv\Scripts\activate
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

---

## 🗄️ MySQL Database Setup

### 1. Create the Database
Log into your local MySQL client or MySQL Workbench:
```sql
CREATE DATABASE IF NOT EXISTS skillconnect_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` (or update existing `.env`):
```ini
DJANGO_SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=skillconnect_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

---

## 🚀 Running Migrations & Seeding Data

### 1. Run Django Migrations
Create the database tables and relational foreign keys:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Populate Sample Demo Data
Run the built-in seeding script to populate categories, skills, demo students, posts, services, and orders:
```bash
python populate_db.py
```

---

## 👤 Pre-Configured Demo Accounts

| Role | Username | Password | Notes / Skills |
| :--- | :--- | :--- | :--- |
| **Platform Administrator** | `admin` | `admin123` | Full Admin Console & Moderation Access |
| **Student (Verified)** | `aarav_patel` | `student123` | Photography (PDEU, B.Tech CSE) |
| **Student (Verified)** | `riya_shah` | `student123` | Graphic Design (PDEU, B.Des) |
| **Student (Verified)** | `krisha_mehta` | `student123` | Mehndi & Henna Art (Final Year) |
| **Student (Verified)** | `dev_shah` | `student123` | Web Development & Coding (4th Year) |
| **Student (Verified)** | `anaya_patel` | `student123` | Makeup & Styling (2nd Year) |
| **Student (Pending)** | `rohan_joshi` | `student123` | Video Editing (Pending review in Admin) |
| **Customer** | `neha_customer` | `customer123` | Has active orders, interests, and reviews |

*(You can also create a new custom superuser anytime using `python manage.py createsuperuser`)*.

---

## 🖥️ Running the Development Server

Start the local Django server:
```bash
python manage.py runserver
```

Open your browser and navigate to:
- **Main Website**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Recommended Feed**: [http://127.0.0.1:8000/feed/](http://127.0.0.1:8000/feed/)
- **Campus Services**: [http://127.0.0.1:8000/services/](http://127.0.0.1:8000/services/)
- **Orders & Tracking**: [http://127.0.0.1:8000/orders/](http://127.0.0.1:8000/orders/)
- **Real-Time Chat**: [http://127.0.0.1:8000/chat/](http://127.0.0.1:8000/chat/)
- **SkillConnect Admin Console**: [http://127.0.0.1:8000/platform-admin/](http://127.0.0.1:8000/platform-admin/)
- **Django Admin**: [http://127.0.0.1:8000/django-admin/](http://127.0.0.1:8000/django-admin/)

---

## 🧪 Running Automated Tests

Run the test suite:
```bash
python manage.py test core
```
Tests cover:
- Public landing page loading
- Customer authentication and feed access
- Order booking and status state machine validation
- One-to-one chat creation and AJAX polling
- Role-based security for admin panel access

---

## 🛡️ Security Best Practices
- **Password Hashing**: Django PBKDF2 with SHA256.
- **CSRF Protection**: Token validation on all form posts and AJAX calls.
- **Role Permission Checks**: Decorators verify user ownership and admin privileges before allowing updates or deletes.
- **Sensitive Settings**: DB passwords and secret keys loaded securely from `.env`.
