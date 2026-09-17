# cinefare-main
## 🎬 CineFare – Movie Ticket Booking System

Welcome to **CineFare**, a Django-based movie ticket booking application that allows users to browse movies, explore showtimes, select seats, and securely book tickets online.

## ✨ Features

### 📍 Location-Based Movie Selection

Users can select their preferred location, after which available movies and showtimes are filtered according to the selected location.

### 🔐 User Registration & Authentication

Users can create an account using their username, email, and password. Registered users can securely log in to access the booking system.

### 🎥 Movie Selection & Information

* Browse currently available movies.
* View trending trailers and recommended movies based on location.
* Explore all movies available in local theatres.
* Filter movies based on **language** and **genre**.
* Select a preferred date and showtime.
* View showtimes based on **price and timing**.
* Use color indicators to identify seat availability.
* Find theatre locations using **Google Maps**.

### 💺 Seat Reservation & Selection

Users can interact with a visual representation of the theatre seating layout. Seats are organized into rows and columns and are visually distinguished based on their availability, selected status, or occupancy.

### 💳 Secure Payment & Ticket Generation

Users can complete their booking through **Razorpay** using supported payment methods. After successful payment, users can download their booking ticket in **PDF format**.

---

## 🛠️ Tech Stack

| Component           | Technology            |
| ------------------- | --------------------- |
| Frontend            | HTML, CSS, JavaScript |
| Backend             | Django                |
| Database            | SQLite                |
| Payment Integration | Razorpay              |
| Maps                | Google Maps           |

---

## 🚀 How to Run

### Prerequisites

Make sure the following are installed:

* Python 3.6+
* pip
* Django

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/saipranaydeep/CineFare_MovieBooking.git
cd CineFare_MovieBooking
```

**2. Create a virtual environment**

```bash
python -m venv venv
```

**3. Activate the virtual environment**

On Windows:

```bash
venv\Scripts\activate
```

**4. Install dependencies**

```bash
pip install -r requirements.txt
```

**5. Run database migrations**

```bash
python manage.py migrate
```

**6. Create a superuser**

```bash
python manage.py createsuperuser
```

**7. Start the development server**

```bash
python manage.py runserver
```

Open your browser and visit:

```text
http://localhost:8000
```

---

## 🗄️ Database Schema

CineFare uses **SQLite** as its database.

The major Django models include:

* User
* Movie
* MovieComment
* MovieRating
* Theatre
* Booked_Seats

The database configuration in `settings.py` uses:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / "db.sqlite3",
    }
}
```

The database can be managed through the Django Admin interface:

```text
http://localhost:8000/admin/
```

Use the superuser credentials created during installation to access the admin panel.

---

## 📖 Usage

1. Register for a CineFare account or log in.
2. Select your preferred location.
3. Browse available movies and showtimes.
4. Select a movie and preferred theatre/show.
5. Choose your seats using the interactive seating layout.
6. Proceed to the payment page.
7. Complete the payment through Razorpay.
8. Confirm your booking.
9. Download your movie ticket in PDF format.

---

## 👩‍💻👨‍💻 Team Members

* **G Yochana Mythri**
* **Aryan**

---

## 🎯 Project Objective

The objective of CineFare is to provide a convenient and user-friendly platform for discovering movies, checking theatre showtimes, selecting seats, making online payments, and generating digital movie tickets through a single web application.

