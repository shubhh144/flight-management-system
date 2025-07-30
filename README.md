# ✈️ Flight Tracker Web App

A Flask-based web application that displays real-time flight data using the [AviationStack API](https://aviationstack.com/) and PostgreSQL. The app provides APIs to retrieve flight information and serves a dynamic frontend to view ongoing flights.

---

## 📌 Features

- Real-time flight tracking from AviationStack API
- PostgreSQL-based relational database for storing:
  - Airports, Airlines, Flights, Passengers
- **Automatic Delay Recognition**: identifies flights delayed by 2 hours or more
- REST API for accessing flight data
- Frontend interface displaying selected flight info
- Environment variables managed via `.env`

---

## 🗃️ Tech Stack

- **Backend**: Flask
- **Database**: PostgreSQL
- **API**: AviationStack
- **Frontend**: HTML, JavaScript, CSS
- **Secrets Management**: `python-dotenv`

---

## 🔧 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/flight-tracker.git
   cd flight-tracker
