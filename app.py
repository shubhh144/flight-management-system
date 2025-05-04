from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)

# Database Configuration
DB_NAME = "airline"
DB_USER = "postgres" #Enter the USER_NAME of database management system
DB_PASSWORD = "shubh2131" #Enter the database system password
DB_HOST = "localhost"
DB_PORT = "5432"

# Database Connection
try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()
    print("Connected to PostgreSQL database!")
except Exception as e:
    print("Database connection error:", e)


@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Flight Tracking API"}), 200


# 1. **Get all flights**
@app.route('/flights', methods=['GET'])
def get_flights():
    try:
        cursor.execute("SELECT flight_number, departure_time, arrival_time FROM Flights")
        flights = cursor.fetchall()
        flight_list = [
            {"flight_number": f[0], "departure_time": f[1], "arrival_time": f[2]}
            for f in flights
        ]
        return jsonify(flight_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 2. **Get flight by number**
@app.route('/flights/<string:flight_number>', methods=['GET'])
def get_flight(flight_number):
    try:
        cursor.execute("SELECT * FROM Flights WHERE flight_number = %s", (flight_number,))
        flight = cursor.fetchone()
        if flight:
            flight_data = {
                "flight_number": flight[0],
                "departure_airport_id": flight[1],
                "arrival_airport_id": flight[2],
                "airline_id": flight[3],
                "departure_time": flight[4],
                "arrival_time": flight[5],
                "scheduled_departure_time": flight[6]
            }
            return jsonify(flight_data), 200
        else:
            return jsonify({"message": "Flight not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 3. **Get delayed flights (using your function logic)**
@app.route('/flights/delayed', methods=['GET'])
def get_delayed_flights():
    try:
        cursor.execute("""
            SELECT flight_number, departure_time, scheduled_departure_time, 
                   (departure_time - scheduled_departure_time) AS delay_time
            FROM Flights 
            WHERE (departure_time - scheduled_departure_time) >= INTERVAL '2 hours';
        """)
        delayed_flights = cursor.fetchall()

        if delayed_flights:
            delayed_list = [
                {"flight_number": f[0], "departure_time": f[1], "scheduled_departure_time": f[2], "delay_time": str(f[3])}
                for f in delayed_flights
            ]
            return jsonify(delayed_list), 200
        else:
            return jsonify({"message": "No flights delayed by more than 2 hours"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Run the API
if __name__ == '__main__':
    app.run(debug=True)
