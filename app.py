# app.py
from flask import Flask, jsonify, render_template
import psycopg2
import threading
from get_aviation import fetch_and_insert_data  # Import fetch function
from dotenv import load_dotenv
import os
app = Flask(__name__, template_folder="templates", static_folder="static")



load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = True
    cursor = conn.cursor()
    print("Connected to DB")
except Exception as e:
    print("DB error:", e)

@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/api/flights', methods=['GET'])
def get_flights():
    try:
        cursor.execute("SELECT flight_number, departure_time, arrival_time FROM Flights")
        flights = cursor.fetchall()
        return jsonify([
            {"flight_number": f[0], "departure_time": f[1], "arrival_time": f[2]}
            for f in flights
        ]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/flights/<string:flight_number>', methods=['GET'])
def get_flight(flight_number):
    try:
        cursor.execute("SELECT * FROM Flights WHERE flight_number = %s", (flight_number,))
        flight = cursor.fetchone()
        if flight:
            return jsonify({
                "flight_number": flight[0],
                "departure_airport_id": flight[1],
                "arrival_airport_id": flight[2],
                "airline_id": flight[3],
                "departure_time": flight[4],
                "arrival_time": flight[5],
                "scheduled_departure_time": flight[6]
            }), 200
        else:
            return jsonify({"message": "Flight not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/flights/delayed', methods=['GET'])
def get_delayed_flights():
    try:
        cursor.execute("""
            SELECT flight_number, departure_time, scheduled_departure_time,
                   (departure_time - scheduled_departure_time) AS delay
            FROM Flights
            WHERE (departure_time - scheduled_departure_time) >= INTERVAL '2 hours'
        """)
        delays = cursor.fetchall()
        return jsonify([
            {"flight_number": d[0], "departure_time": d[1], "scheduled": d[2], "delay_time": str(d[3])}
            for d in delays
        ]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/flights/delete', methods=['DELETE'])
def delete_all_flights():
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Flights")
            conn.commit()
        return jsonify({"message": "All flight records deleted"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

# Start background thread when Flask app starts
if __name__ == '__main__':
    threading.Thread(target=fetch_and_insert_data, daemon=True).start()
    app.run(debug=True)
