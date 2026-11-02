# SkillConnect: Complete Master Project Documentation & Code Guide
**Full-Stack Student Talent Marketplace & Portfolio Social Platform**
*Developed with Python Django, MySQL 8.0, Semantic HTML5, CSS3, and Vanilla JavaScript (ES6+)*

---

## Table of Contents
1. [Executive Summary & Abstract](#1-executive-summary--abstract)
2. [Problem Statement & Proposed Solution](#2-problem-statement--proposed-solution)
3. [System Architecture (Django MVT Pattern)](#3-system-architecture-django-mvt-pattern)
4. [Complete File-by-File Guide (Every Application & File)](#4-complete-file-by-file-guide)
   - 4.1 Project Configuration (`skillconnect/`, `manage.py`, `.env`)
   - 4.2 Accounts App (`accounts/`)
   - 4.3 Posts App (`posts/`)
   - 4.4 Services App (`services/`)
   - 4.5 Orders App (`orders/`)
   - 4.6 Chat App (`chat/`)
   - 4.7 Reviews App (`reviews/`)
   - 4.8 Reports App (`reports/`)
   - 4.9 Notifications App (`notifications/`)
   - 4.10 Admin Panel App (`admin_panel/`)
   - 4.11 Core App (`core/`)
   - 4.12 Static Assets (`static/css/`, `static/js/`)
   - 4.13 Templates Architecture (`templates/`)
5. [Syntax & Code Deep Dive: How the Code Works Line by Line](#5-syntax--code-deep-dive)
   - 5.1 Python & Django Decorators (`@login_required`, `@user_passes_test`)
   - 5.2 Django ORM Methods (`filter`, `select_related`, `commit=False`, `get_object_or_404`)
   - 5.3 Django Template Language (DTL) Syntax (`{% extends %}`, `{% csrf_token %}`, etc.)
   - 5.4 Vanilla JavaScript AJAX & DOM Manipulation (`fetch`, `async/await`, Event Listeners)
   - 5.5 File Upload Handling (`ImageField`, `request.FILES`, `MEDIA_ROOT`)
6. [Step-by-Step Functional Workflow](#6-step-by-step-functional-workflow)
   - Step 1: User Registration (Student vs Customer)
   - Step 2: Student ID Card Upload & Admin Verification
   - Step 3: Publishing Visual Portfolio Posts
   - Step 4: Listing Freelance Services with Pricing (₹)
   - Step 5: Customer Discovery & Service Booking
   - Step 6: 5-Stage Milestone Order Stepper
   - Step 7: Real-Time Polling Chat
   - Step 8: Order Completion & Ratings/Reviews
7. [MySQL Database Schema & Entity Relationships](#7-mysql-database-schema--entity-relationships)
8. [Security Architecture & Best Practices](#8-security-architecture--best-practices)
9. [Viva & Project Evaluation Q&A (20 Questions & Answers)](#9-viva--project-evaluation-qa)
10. [Step-by-Step Execution Guide](#10-step-by-step-execution-guide)

---

## 1. Executive Summary & Abstract

**SkillConnect** is an enterprise-grade full-stack web application engineered to solve the disconnect between talented college students and potential clients seeking campus-friendly freelance services.

Traditional freelance platforms (such as Upwork or Fiverr) present steep barriers to entry for students: they impose high commission fees (up to 20%), require established work histories, and lack college-specific identity verification. SkillConnect introduces a dedicated ecosystem that bridges social portfolio sharing with a secure service marketplace, verifiable student credentials, milestone-based order tracking, live messaging, and community moderation.

### Technology Stack Summary:
* **Backend Framework**: Python 3.13 / Django 5.2 (Model-View-Template Architecture)
* **Relational Database**: MySQL Server 8.0 (`skillconnect_db`) with InnoDB transactional engine and foreign key constraints
* **Database Driver**: `PyMySQL` with `install_as_MySQLdb()` monkey-patching for seamless Python 3.13 integration
* **Frontend**: Semantic HTML5, Custom Responsive CSS3 (CSS Custom Properties, Flexbox, Grid), and Pure Vanilla JavaScript (ES6+)
* **Constraint Compliance**: Zero dependency on third-party frontend frameworks (No React, Vue, Angular) and no external Node.js server.
* **Authentication**: Django PBKDF2 with SHA-256 password hashing and role-based permissions (`CUSTOMER`, `STUDENT`, `ADMIN`).
* **Media Management**: Django File & Image handling using `Pillow 12.3.0`.

---

## 2. Problem Statement & Proposed Solution

### The Problem:
1. **Underutilized Student Talent**: College students possess exceptional skills in design, photography, tutoring, software development, mehndi, and event styling, but lack a formal local showcase.
2. **High Discovery Cost for Campus Clients**: Peers, college fests, and local businesses struggle to find reliable, verified student creators nearby.
3. **Absence of Accountability**: Informal arrangements over WhatsApp or Instagram frequently suffer from ghosting, unclear pricing, and payment disputes.

### The Solution:
* **Curated Social Feed**: Visual posts showcasing creative work with tags, likes, comments, and sharing.
* **Student Verification Workflow**: Students upload their institutional ID card. Platform administrators review and approve credentials, granting an official `✓ Verified Student` badge.
* **Service Marketplace**: Fixed-price packages in INR (₹) with delivery timelines and clear revisions.
* **Visual Milestone Order Tracker**: 5 distinct progress stages (`Requested` → `Accepted` → `In Progress` → `Ready for Review` → `Completed`) with real-time audit logs.
* **Real-Time Messaging**: Built-in 1-to-1 chat with automatic 3-second AJAX polling.
* **Trust & Reputation**: Verified customer reviews and community reporting tools.

---

## 3. System Architecture (Django MVT Pattern)

SkillConnect is built on the **Model-View-Template (MVT)** architectural pattern:

```text
       ┌────────────────────────────────────────────────────────┐
       │                   Web Browser (Client)                 │
       └───────────────▲────────────────────────┬───────────────┘
                       │                        │
         HTML/CSS/JS   │                        │ HTTP Request
         HTTP Response │                        │ (GET / POST)
                       │                        ▼
       ┌───────────────┴────────────────────────────────────────┐
       │                 Django URL Router (urls.py)            │
       └────────────────────────┬───────────────────────────────┘
                                │ Matches route and invokes
                                ▼
       ┌────────────────────────────────────────────────────────┐
       │                  Django Views (views.py)               │
       │                 Controller & Business Logic            │
       └───────────────┬────────────────────────▲───────────────┘
                       │                        │
         Queries &     │                        │ Context Data
         Modifies      ▼                        │ Dictionary
       ┌────────────────────────┐      ┌────────┴───────────────┐
       │      Django Models     │      │    Django Templates    │
       │       (models.py)      │      │        (*.html)        │
       └───────────────┬────────┘      └────────────────────────┘
                       │
         SQL Queries   │ (PyMySQL ORM)
                       ▼
       ┌────────────────────────┐
       │     MySQL Database     │
       │   (skillconnect_db)    │
       └────────────────────────┘
```

### Component Responsibilities:
1. **Model (`models.py`)**: Defines the data schema as Python classes. Django's Object-Relational Mapper (ORM) translates these classes into MySQL tables.
2. **View (`views.py`)**: Contains the business logic. It handles incoming HTTP requests, performs authentication checks, queries the models, and passes data to templates.
3. **Template (`*.html`)**: Presentation layer written in HTML enriched with Django Template Language (DTL) tags to render dynamic data.
4. **URL Conf (`urls.py`)**: Directs incoming URL requests to the correct view function using regular expressions or path converters.

---

## 4. Complete File-by-File Guide

Below is the exhaustive file-by-file breakdown of every directory and file in the SkillConnect repository.

### 4.1 Project Configuration & Root Files

#### `manage.py`
* **Purpose**: Django's primary command-line utility.
* **Function**: Executes administrative tasks such as `runserver`, `makemigrations`, `migrate`, and `test`. Sets the `DJANGO_SETTINGS_MODULE` environment variable to `skillconnect.settings`.

#### `populate_db.py`
* **Purpose**: Automated database seeder.
* **Function**: Programmatically populates MySQL with realistic demonstration data:
  * 12 Categories and 24 Skills
  * 8 User accounts (1 Admin, 6 diverse Student creators across Photography, UI/UX, Web Dev, Mehndi, Makeup, Video Editing, and 1 Customer)
  * Pillow-generated portfolio artwork and ID card samples
  * 6 Service packages, active orders, live chat messages, and customer reviews.

#### `requirements.txt`
* **Purpose**: Python package dependency declaration.
* **Function**: Lists exact versions required: `Django>=5.1,<6.0`, `PyMySQL`, `pillow`, `python-dotenv`, `sqlparse`, `cryptography`.

#### `.env` / `.env.example`
* **Purpose**: Environment variable storage.
* **Function**: Decouples sensitive configuration (MySQL database name, user, password, port, and Django `SECRET_KEY`) from source code for security compliance.

#### `skillconnect/__init__.py`
* **Purpose**: Python package initialization and MySQL driver binding.
* **Key Code**:
  ```python
  import pymysql
  pymysql.install_as_MySQLdb()
  ```
* **Why it is needed**: Python 3.13 on Windows lacks prebuilt C-extensions for the legacy `mysqlclient` package. PyMySQL provides a pure-Python MySQL driver, and `install_as_MySQLdb()` tricks Django into treating PyMySQL as the standard MySQLdb library.

#### `skillconnect/settings.py`
* **Purpose**: Central configuration for the entire application.
* **Function**:
  * Registers all 10 modular apps in `INSTALLED_APPS`.
  * Configures MySQL connection under `DATABASES`.
  * Configures custom user model: `AUTH_USER_MODEL = 'accounts.User'`.
  * Defines `STATIC_URL`, `STATICFILES_DIRS`, `MEDIA_URL`, and `MEDIA_ROOT`.
  * Sets security parameters: CSRF cookie settings, session timeouts, and password validators.

#### `skillconnect/urls.py`
* **Purpose**: Master URL routing directory.
* **Function**: Routes root paths to app-specific URL routers using `include()`. Appends media serving routes during development:
  ```python
  if settings.DEBUG:
      urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
  ```

---

### 4.2 Accounts App (`accounts/`)
Manages user authentication, profile data, student verification submissions, and social follower connections.

* **`accounts/models.py`**:
  * `User`: Custom user class inheriting from `AbstractUser`. Adds `user_type` (`CUSTOMER`, `STUDENT`, `ADMIN`), `phone_number`, `profile_photo`, `bio`, and `is_verified_student`.
  * `Category`: Stores creative domains (e.g., Photography, Graphic Design, Web Development).
  * `Skill`: Individual competencies linked to categories (e.g., Portrait Photography, Django, Canva).
  * `StudentProfile`: 1-to-1 profile for student users holding `college_name`, `course`, `year_of_study`, `college_id_card`, `verification_status` (`PENDING`, `VERIFIED`, `REJECTED`), and a many-to-many relationship to `Skill`.
  * `Follow`: Tracks student follower graphs (`follower` → `following`).
* **`accounts/views.py`**:
  * `register_view`: Handles new user signups with dynamic role switching (Customer vs Student).
  * `login_view`: Custom login accepting either username or email address.
  * `logout_view`: Invalidates session and redirects to homepage.
  * `profile_view`: Public showcase page displaying stats, portfolio posts, services, and reviews.
  * `edit_profile_view`: Allows users to update bios, avatars, and college details.
  * `toggle_follow_view`: AJAX endpoint for following/unfollowing student creators.
* **`accounts/forms.py`**:
  * `CustomUserCreationForm`: Validates unique emails and secure passwords.
  * `StudentProfileForm`: Handles college ID image upload and academic credentials.
  * `UserProfileEditForm`: Clean form for profile metadata editing.
* **`accounts/urls.py`**:
  * Defines paths: `/accounts/register/`, `/accounts/login/`, `/accounts/logout/`, `/profile/<username>/`, `/profile/edit/`, `/follow/<username>/`.

---

### 4.3 Posts App (`posts/`)
Powers the social portfolio feed, like counts, and comments.

* **`posts/models.py`**:
  * `Post`: Stores image upload, caption, category, student foreign key, like count, and creation timestamp.
  * `PostLike`: Junction table linking `User` and `Post` to enforce 1-like-per-user with `unique_together`.
  * `PostComment`: Threaded user comments with timestamps.
* **`posts/views.py`**:
  * `feed_view`: Renders the curated feed with algorithmic boosting for verified students.
  * `post_create_view`: Student-restricted view for uploading visual portfolio pieces.
  * `post_detail_view`: Detailed post page with full comment thread.
  * `post_like_view`: AJAX endpoint returning `{ liked: true, count: 12 }` in JSON.
  * `post_comment_view`: Submits comments synchronously or via AJAX.
  * `post_delete_view`: Enforces ownership before deletion.
* **`posts/forms.py`**: Form validation for post image uploads and captions.
* **`posts/urls.py`**: Maps `/feed/`, `/posts/create/`, `/posts/<id>/`, `/posts/<id>/like/`, etc.

---

### 4.4 Services App (`services/`)
Manages student freelance service listings, pricing, and category search.

* **`services/models.py`**:
  * `Service`: Stores `title`, `description`, `price` (in INR ₹), `delivery_time_days`, `category`, `cover_image`, `is_active`, and foreign key to `student`.
* **`services/views.py`**:
  * `service_list_view`: Searchable and filterable catalog by category, price range, and rating.
  * `service_detail_view`: Shows service details, pricing, turnaround time, student credentials, and past client reviews.
  * `service_create_view` & `service_edit_view`: Student-only endpoints to manage offerings.
  * `service_delete_view`: Deactivates or removes a service listing.
* **`services/forms.py`**: Validates pricing (> ₹0) and delivery days (> 0).
* **`services/urls.py`**: Routes `/services/`, `/services/create/`, `/services/<id>/`, etc.

---

### 4.5 Orders App (`orders/`)
Core commerce engine providing end-to-end milestone management.

* **`orders/models.py`**:
  * `Order`: Tracks `order_number` (e.g., `ORD-20261002-XXXX`), `customer`, `student`, `service`, `price`, `requirements`, `status` (`REQUESTED`, `ACCEPTED`, `IN_PROGRESS`, `READY_FOR_REVIEW`, `COMPLETED`, `CANCELLED`), and delivery files.
  * `OrderStatusHistory`: Immutable audit log recording every status change, timestamp, and changing user.
* **`orders/views.py`**:
  * `book_service_view`: Creates new order request with requirements.
  * `order_detail_view`: Visual milestone stepper showing current status, timeline, action buttons, and direct chat link.
  * `order_list_view`: Dashboard of ongoing and historical orders split by role.
  * `update_order_status_view`: State machine view enforcing valid transitions (e.g., only student can accept, only customer can mark completed).
* **`orders/forms.py`**: Form for customer project requirements and deadline dates.
* **`orders/urls.py`**: Routes `/orders/`, `/orders/<id>/`, `/orders/book/<service_id>/`, etc.

---

### 4.6 Chat App (`chat/`)
Provides real-time direct messaging between customers and student freelancers.

* **`chat/models.py`**:
  * `Conversation`: Chat container between two participants (Customer and Student), optionally linked to an `Order`.
  * `Message`: Stores `conversation`, `sender`, `content`, `created_at`, and `is_read`.
* **`chat/views.py`**:
  * `conversation_list_view`: Inbox showing active chats with unread badges.
  * `chat_room_view`: Active messaging interface.
  * `send_message_view`: AJAX endpoint for sending new text messages.
  * `poll_messages_view`: Fast AJAX polling endpoint returning new messages where `id > last_id`.
* **`chat/urls.py`**: Routes `/chat/`, `/chat/<id>/`, `/chat/<id>/poll/`, `/chat/start/<username>/`.

---

### 4.7 Reviews App (`reviews/`)
Enforces verified client ratings and feedback.

* **`reviews/models.py`**:
  * `Review`: Stores `order` (OneToOne constraint ensuring 1 review per completed order), `student`, `customer`, `rating` (1 to 5 stars), and written `comment`.
* **`reviews/views.py`**:
  * `create_review_view`: Restricted strictly to customers of `COMPLETED` orders.
* **`reviews/forms.py`**: Rating dropdown and comment text area.
* **`reviews/urls.py`**: Routes `/reviews/order/<order_id>/create/`.

---

### 4.8 Reports App (`reports/`)
Community safety and moderation subsystem.

* **`reports/models.py`**:
  * `Report`: Stores reporter, reported item type (`USER`, `POST`, `SERVICE`), reason, details, and review status (`PENDING`, `RESOLVED`, `DISMISSED`).
* **`reports/views.py`**:
  * `submit_report_view`: User-facing modal/page to flag offensive content.
* **`reports/urls.py`**: Routes `/reports/submit/`.

---

### 4.9 Notifications App (`notifications/`)
Dispatches real-time alerts for orders, messages, likes, and verifications.

* **`notifications/models.py`**:
  * `Notification`: Stores `recipient`, `sender`, `notification_type`, `title`, `message`, `link`, `is_read`, and helper method `Notification.send(...)`.
* **`notifications/views.py`**:
  * `notification_list_view`: Renders notifications and marks them as read.
* **`notifications/urls.py`**: Routes `/notifications/`.

---

### 4.10 Admin Panel App (`admin_panel/`)
Dedicated campus administrator operations dashboard (distinct from generic Django admin).

* **`admin_panel/views.py`**:
  * `dashboard_view`: Real-time KPI metrics (total users, verified students, active orders, platform revenue).
  * `student_verification_view`: Table of pending students with ID card image modal preview.
  * `approve_student_view` & `reject_student_view`: 1-click decision making with instant notification triggers.
  * `moderation_reports_view`: Resolution queue for reported content.
  * `toggle_user_status_view`: Suspend or reinstate user accounts.
* **`admin_panel/urls.py`**: Routes `/custom-admin/`, `/custom-admin/verifications/`, etc.

---

### 4.11 Core App (`core/`)
Landing pages, global search, and automated test suite.

* **`core/views.py`**:
  * `home_view`: Marketing landing page with hero banner, category grid, top student talent cards, and recent reviews.
  * `search_view`: Global search engine querying across students, posts, and services simultaneously.
* **`core/tests.py`**: Automated unit test suite verifying user creation, verification logic, service creation, and order transitions.
* **`core/urls.py`**: Routes `/` (homepage) and `/search/`.

---

### 4.12 Static Assets (`static/`)
Pure Vanilla CSS and JavaScript files.

* **`static/css/style.css`**: Complete responsive design system:
  * CSS Custom Properties: `--primary: #4F46E5`, `--accent: #06B6D4`, `--success: #10B981`, etc.
  * Responsive Flexbox and Grid layouts.
  * 5-Stage Order Stepper UI styling.
  * Mobile drawer navigation and modal overlays.
* **`static/js/main.js`**:
  * Asynchronous AJAX like button handler with live count updates.
  * Instant comment post submission.
  * Share-to-clipboard functionality with auto-dismissing toast notifications.
  * Cross-Site Request Forgery (CSRF) cookie parser.
* **`static/js/chat.js`**:
  * 3-second background polling engine using `fetch()`.
  * Auto-scrolling chat bubble renderer with formatted timestamps.

---

### 4.13 Templates Architecture (`templates/`)
37 semantic HTML5 templates inheriting from a master template.

* **`templates/base.html`**: Master layout file containing the HTML `<head>`, navigation bar, flash alert banner container, main content block (`{% block content %}`), and footer.
* **Subdirectories**:
  * `templates/core/`: `home.html`, `search.html`.
  * `templates/accounts/`: `login.html`, `register.html`, `profile.html`, `edit_profile.html`.
  * `templates/posts/`: `feed.html`, `post_detail.html`, `post_create.html`.
  * `templates/services/`: `service_list.html`, `service_detail.html`, `service_form.html`.
  * `templates/orders/`: `order_list.html`, `order_detail.html`, `book_service.html`.
  * `templates/chat/`: `inbox.html`, `room.html`.
  * `templates/reviews/`: `create_review.html`.
  * `templates/admin_panel/`: `dashboard.html`, `verifications.html`, `reports.html`, `users.html`.

---

## 5. Syntax & Code Deep Dive

### 5.1 Python & Django Decorators

Decorators wrap a function to extend its behavior without modifying its internal code.

```python
@login_required
@user_passes_test(lambda u: u.is_staff or u.user_type == 'ADMIN')
def student_verification_view(request):
    ...
```

* `@login_required`: Automatically checks `request.user.is_authenticated`. If false, intercepts the request and redirects the visitor to `/accounts/login/?next=...`.
* `@user_passes_test(...)`: Executes a boolean lambda expression. If the user is not an administrator, returns HTTP 403 Forbidden or redirects.

---

### 5.2 Django ORM Syntax & Methods

```python
# 1. Fetching single object with automatic 404 response
service = get_object_or_404(Service, id=service_id, is_active=True)

# 2. Optimized database joins to prevent N+1 query performance penalties
posts = Post.objects.select_related('student', 'category')\
                    .prefetch_related('likes', 'comments')\
                    .order_by('-created_at')

# 3. Two-stage object saving
order = form.save(commit=False) # Creates Python instance without writing to MySQL
order.customer = request.user   # Injects logged-in user
order.save()                    # Commits row to MySQL skillconnect_db
```

* `get_object_or_404(...)`: Replaces verbose `try...except Service.DoesNotExist` blocks.
* `select_related(...)`: Performs an SQL `INNER JOIN` in a single query for foreign keys.
* `commit=False`: Pauses database insertion, allowing developer to attach server-computed attributes before final persistence.

---

### 5.3 Django Template Language (DTL) Syntax

```html
{% extends 'base.html' %}

{% block content %}
  {% if order.status == 'COMPLETED' %}
    <span class="badge badge-success">✓ Completed</span>
  {% elif order.status == 'IN_PROGRESS' %}
    <span class="badge badge-warning">⚙ In Progress</span>
  {% endif %}

  <form method="POST" action="{% url 'cancel_order' order.id %}">
    {% csrf_token %}
    <button type="submit" class="btn btn-danger">Cancel</button>
  </form>
{% endblock %}
```

* `{% extends 'base.html' %}`: Object-oriented template inheritance. Borrows layout, CSS, and navigation from the base template.
* `{% csrf_token %}`: Renders a hidden `<input type="hidden" name="csrfmiddlewaretoken" value="...">` to prevent Cross-Site Request Forgery exploits.
* `{% url 'name' param %}`: Resolves named URL patterns dynamically. Prevents hardcoding broken URLs.

---

### 5.4 Vanilla JavaScript AJAX Syntax

```javascript
// Asynchronous HTTP POST request without page reload
async function toggleLike(postId) {
  const response = await fetch(`/posts/${postId}/like/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
      'X-Requested-With': 'XMLHttpRequest'
    }
  });

  if (response.ok) {
    const data = await response.json(); // Parses { liked: true, count: 5 }
    document.querySelector(`#like-count-${postId}`).textContent = data.count;
  }
}
```

* `async / await`: Clean modern syntax for handling asynchronous HTTP promises.
* `fetch(...)`: Standard browser API replacing third-party Axios or jQuery.
* `getCookie('csrftoken')`: Reads Django's CSRF token from the browser cookie and attaches it to the request header.

---

### 5.5 File Upload Handling

```python
# accounts/views.py
if request.method == 'POST':
    form = StudentProfileForm(request.POST, request.FILES)
    if form.is_valid():
        profile = form.save()
```

* `request.FILES`: Multi-part form uploads (`enctype="multipart/form-data"`) are separated by Django from standard text inputs.
* The physical file is saved into `media/college_ids/filename.jpg`, while the database column `college_id_card` stores the relative path string.

---

## 6. Step-by-Step Functional Workflow

```text
[1. Registration] ──> [2. ID Upload] ──> [3. Admin Verification]
                                                │
                                                ▼ (Earns ✓ Badge)
[6. Completion] <── [5. Stepper] <── [4. Service Booking & Chat]
```

### Step 1: User Registration
* Visitor chooses **Customer** or **Student** role.
* Provides Name, Username, Email, and Password. Passwords are encrypted using PBKDF2-SHA256.

### Step 2: Student ID Card Upload
* Student enters College Name, Degree/Course, Year of Study, and uploads a photograph of their Student ID Card.
* Profile is automatically marked `PENDING`.

### Step 3: Admin Review & Verification
* Platform Admin visits `/custom-admin/verifications/`.
* Admin inspects the uploaded ID card image in a popup lightbox.
* Clicking **Approve** sets status to `VERIFIED`, awards the `✓ Verified Student` badge, and dispatches a notification to the student.

### Step 4: Publishing Posts & Services
* Student creates portfolio posts (e.g., "Graduation Photoshoot") with tags and images.
* Student lists service packages (e.g., "Event Photography - ₹1,500 - 3 Days Delivery").

### Step 5: Customer Discovery & Booking
* Customer browses the feed or filters services by category.
* Customer clicks **Book Service**, inputs project requirements, and submits the order.
* Order status initialized to `REQUESTED`.

### Step 6: Visual Milestone Stepper
* Both parties access `/orders/<order_id>/` featuring a 5-step visual tracking bar:
  1. `REQUESTED`: Waiting for student acceptance.
  2. `ACCEPTED`: Student accepts order.
  3. `IN_PROGRESS`: Student is actively working.
  4. `READY_FOR_REVIEW`: Student submits delivery files.
  5. `COMPLETED`: Customer approves work and closes order.

### Step 7: Real-Time Chat Polling
* Customer and student communicate directly via built-in messaging.
* JavaScript polls Django every 3 seconds for seamless updates.

### Step 8: Verified Customer Review
* Upon completion, the customer rates the student (1 to 5 stars) and writes feedback.
* Average ratings and review counts update immediately on the student's public profile.

---

## 7. MySQL Database Schema & Entity Relationships

The MySQL database `skillconnect_db` contains the following primary relational tables:

| Table Name | Primary Purpose | Key Foreign Keys |
| :--- | :--- | :--- |
| `accounts_user` | Core user identity & roles | None (Root Table) |
| `accounts_category` | Creative skill categories | None |
| `accounts_skill` | Specific skill competencies | `category_id` → `accounts_category` |
| `accounts_studentprofile`| College credentials & verification status | `user_id` (1-to-1) → `accounts_user` |
| `accounts_follow` | Social following graph | `follower_id`, `following_id` → `accounts_user` |
| `posts_post` | Student portfolio posts | `student_id` → `accounts_user`, `category_id` |
| `posts_postlike` | Post like registry (Unique constraint) | `post_id` → `posts_post`, `user_id` |
| `posts_postcomment` | Comments on posts | `post_id` → `posts_post`, `user_id` |
| `services_service` | Freelance service catalog | `student_id` → `accounts_user`, `category_id` |
| `orders_order` | Milestone order tracking | `service_id`, `customer_id`, `student_id` |
| `orders_orderstatushistory` | Audit trail of status changes | `order_id` → `orders_order` |
| `chat_conversation` | 1-to-1 messaging thread | `participant1_id`, `participant2_id`, `order_id` |
| `chat_message` | Chat text messages | `conversation_id`, `sender_id` |
| `reviews_review` | Verified client reviews | `order_id` (1-to-1), `student_id`, `customer_id` |
| `reports_report` | Moderation flags | `reporter_id` → `accounts_user` |
| `notifications_notification`| User alerts | `recipient_id`, `sender_id` → `accounts_user` |

---

## 8. Security Architecture & Best Practices

1. **Password Protection**: Passwords are never stored as plain text. Django hashes all passwords with **PBKDF2 with SHA-256** and a 128-bit cryptographic salt over 720,000 iterations.
2. **Cross-Site Request Forgery (CSRF)**: Every HTTP POST form and AJAX call embeds a cryptographic CSRF token. Requests lacking a matching token are rejected with HTTP 403 Forbidden.
3. **SQL Injection Immunity**: All database queries are executed through Django's parameter-binding ORM. User inputs are never concatenated directly into raw SQL strings.
4. **Cross-Site Scripting (XSS)**: Django Template Language automatically HTML-escapes all dynamic variables (`<script>` tags are neutralized into `&lt;script&gt;`).
5. **Role-Based Access Control (RBAC)**: Sensitive actions (such as student verification or order approval) enforce strict server-side permission checks.
6. **File Upload Security**: File uploads are restricted to image MIME types via Pillow validation.

---

## 9. Viva & Project Evaluation Q&A

### Q1: What architecture pattern does SkillConnect use?
**Answer**: It uses the Django MVT (Model-View-Template) pattern, an evolution of MVC. The Model represents the MySQL database schema, the View manages controller business logic, and the Template renders HTML presentations.

### Q2: Why did you choose MySQL instead of SQLite?
**Answer**: SQLite is a serverless file-based database unsuitable for multi-user production applications. MySQL 8.0 provides true multi-user concurrency, ACID transaction guarantees, robust foreign key constraints, and horizontal scalability.

### Q3: How is student verification handled?
**Answer**: When a student signs up, their profile enters a `PENDING` state. They upload a college ID card. An administrator inspects the ID in the custom admin console and clicks "Approve", which updates the database, awards the `✓ Verified Student` badge, and sends an automated notification.

### Q4: How does the real-time chat work without WebSockets or Node.js?
**Answer**: It uses native Vanilla JavaScript AJAX polling. Every 3 seconds, a lightweight HTTP GET request queries `/chat/<id>/poll/?last_id=X`. Django returns only newly created messages in JSON, which are appended dynamically to the DOM.

### Q5: What prevents a user from rating a student multiple times?
**Answer**: The `Review` model maintains a `OneToOneField` linking to `Order`. Only customers of an order marked `COMPLETED` can submit a review, guaranteeing that every review reflects a verified completed transaction.

### Q6: How do you prevent Cross-Site Scripting (XSS)?
**Answer**: Django's template engine automatically escapes all variable outputs by default. If a user enters malicious JavaScript, it is converted into harmless HTML entities.

### Q7: What is the purpose of `commit=False` in Django forms?
**Answer**: It generates an in-memory model instance without immediately committing it to MySQL. This allows the developer to programmatically attach foreign keys (e.g., `order.customer = request.user`) before saving.

### Q8: How does the platform calculate average student ratings?
**Answer**: When rendering a student profile, Django executes an aggregate query: `Review.objects.filter(student=user).aggregate(Avg('rating'))`.

### Q9: Can a student purchase their own service?
**Answer**: No. The `book_service_view` implements server-side validation: `if service.student == request.user: return redirect(...)` with a warning message.

### Q10: How are uploaded files managed?
**Answer**: Uploaded images are stored on the server's file system inside the `media/` directory. The MySQL database stores only the relative file path string.

---

## 10. Step-by-Step Execution Guide

### Starting the Application:

1. **Verify MySQL Service**:
   Ensure MySQL service (`MySQL80`) is running on port `3306`.

2. **Run Django Development Server**:
   Open Windows PowerShell in the project directory:
   ```powershell
   .\.venv\Scripts\python manage.py runserver
   ```
   Open your browser and navigate to: `http://127.0.0.1:8000/`

3. **Pre-Configured Demo Credentials**:
   * **Admin Console**: `admin` / `admin123` (`http://127.0.0.1:8000/custom-admin/`)
   * **Verified Student (Photography)**: `aarav_patel` / `student123`
   * **Verified Student (Graphic Design)**: `riya_shah` / `student123`
   * **Pending Student (Video Editing)**: `rohan_joshi` / `student123`
   * **Customer (Client)**: `neha_customer` / `customer123`

4. **Running Automated Tests**:
   ```powershell
   .\.venv\Scripts\python manage.py test core
   ```
   *Expected Result*: `OK (Ran 5 tests in ~0.5s)`
