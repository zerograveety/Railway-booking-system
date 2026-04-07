# 🚉 New Rail: Modern Railway Booking System

[![Flask](https://img.shields.io/badge/Flask-2.0+-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red?style=for-the-badge)](https://www.sqlalchemy.org/)

**New Rail** is a premium, glassmorphic web application designed to streamline the railway ticket reservation process. Built with Flask and PostgreSQL, it offers a seamless end-to-end experience from searching for trains to managing bookings and cancellations.

## ✨ Features

- 🔐 **Secure Authentication**: User registration and login system with hashed passwords using Werkzeug.
- 🔍 **Smart Search**: Dynamic station search with auto-suggestions and real-time train availability across various routes.
- 💺 **Interactive Seat Selection**: Choose your preferred seat (Window, Aisle, Middle) with instant price calculation.
- 📅 **Real-time Bookings**: Instant ticket generation and confirmation for scheduled journeys.
- 📋 **User Dashboard**: A centralized hub to view active bookings, journey history, and ticket statuses.
- ❌ **Easy Cancellations**: One-click cancellation for future journeys with automatic seat release.
- 💎 **Premium UI**: Modern glassmorphic design with smooth transitions and responsive layouts.

## 🛠️ Tech Stack

- **Backend**: Python 3.x, Flask
- **Database**: PostgreSQL (Relational Database Management)
- **ORM**: Flask-SQLAlchemy
- **Frontend**: HTML5, CSS3 (Vanilla), JavaScript (ES6+)
- **Security**: Flask-Login, Werkzeug Security, Flask-WTF

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL installed and running

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/zerograveety/Railway-booking-system.git
   cd Railway-booking-system
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**:
   Create a PostgreSQL database named `railway` and update the `DATABASE_URL` in `app.py` or set it as an environment variable:
   ```bash
   export DATABASE_URL="postgresql://username:password@localhost/railway"
   ```

5. **Run the Application**:
   ```bash
   python app.py
   ```
   The app will be available at `http://127.0.0.1:5001`.

## 📁 Project Structure

```text
.
├── app.py              # Main Flask application & routes
├── import_stations.py  # Utility to seed station data
├── static/             # Assets (CSS, JS, Images, Models)
│   ├── css/
│   ├── js/
│   └── images/
├── templates/          # Jinja2 HTML templates
├── requirements.txt    # Project dependencies
└── README.md           # Project documentation
```

## 🛤️ Future Roadmap

- [ ] Integration with real-time Train APIs.
- [ ] PNR status tracking and live train location.
- [ ] Payment gateway integration for ticket purchases.
- [ ] E-ticket download in PDF format.
- [ ] Support for multiple languages.

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---
Developed with ❤️ by [Harshvardhan Kamble](https://github.com/zerograveety)
