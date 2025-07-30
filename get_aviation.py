# get_aviation.py
import psycopg2
import requests
import time
import os
from dotenv import load_dotenv
load_dotenv()

# Database config
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Main fetch + insert logic in a function
def fetch_and_insert_data():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()
        print("Connected to PostgreSQL!")

        # Define reusable INSERT functions (same as yours)
        # --- (Same insert_airport, insert_airline, etc.)

        def insert_airport(iata_code, name, icao_code, country, city, latitude, longitude):
            if iata_code:
                cursor.execute("""
                    INSERT INTO Airport (IATA_code, name, ICAO_code, country, city, latitude, longitude)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (IATA_code) DO NOTHING;
                """, (iata_code, name, icao_code, country, city, latitude, longitude))

        def insert_airline(name, code):
            if code:
                cursor.execute("""
                    INSERT INTO Airlines (name, code)
                    VALUES (%s, %s)
                    ON CONFLICT (code) DO NOTHING;
                """, (name, code))

        def insert_flight_status(status_name):
            if status_name:
                cursor.execute("""
                    INSERT INTO FlightStatus (status_name)
                    VALUES (%s)
                    ON CONFLICT (status_name) DO NOTHING;
                """, (status_name,))

        def insert_or_update_flight(flight_number, dep_iata, arr_iata, airline_code,
                                    dep_time, arr_time, scheduled_dep_time, status_name):
            cursor.execute("""
                INSERT INTO Flights (
                    flight_number, departure_airport_id, arrival_airport_id, airline_id,
                    departure_time, arrival_time, scheduled_departure_time, status_id
                )
                VALUES (
                    %s,
                    (SELECT airport_id FROM Airport WHERE IATA_code = %s),
                    (SELECT airport_id FROM Airport WHERE IATA_code = %s),
                    (SELECT airline_id FROM Airlines WHERE code = %s),
                    %s, %s, %s,
                    (SELECT status_id FROM FlightStatus WHERE status_name = %s)
                )
                ON CONFLICT (flight_number) DO UPDATE
                SET status_id = (SELECT status_id FROM FlightStatus WHERE status_name = %s),
                    scheduled_departure_time = EXCLUDED.scheduled_departure_time;
            """, (flight_number, dep_iata, arr_iata, airline_code,
                  dep_time, arr_time, scheduled_dep_time, status_name, status_name))

        # Loop to continuously fetch data every 5 mins
        API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
        while True:
            print("Fetching flight data...")
            try:
                response = requests.get(
                    f"http://api.aviationstack.com/v1/flights?access_key={API_KEY}"
                )
                response.raise_for_status()
                data = response.json()

                if "data" in data:
                    for flight in data["data"]:
                        flight_number = flight.get("flight", {}).get("iata")
                        dep_airport = flight.get("departure", {})
                        arr_airport = flight.get("arrival", {})
                        airline = flight.get("airline", {})
                        status = flight.get("flight_status")

                        dep_iata = dep_airport.get("iata")
                        arr_iata = arr_airport.get("iata")
                        dep_name = dep_airport.get("airport")
                        dep_icao = dep_airport.get("icao")
                        dep_country = dep_airport.get("country")
                        dep_city = dep_airport.get("city")
                        dep_lat = dep_airport.get("latitude")
                        dep_long = dep_airport.get("longitude")
                        arr_name = arr_airport.get("airport")
                        arr_icao = arr_airport.get("icao")
                        arr_country = arr_airport.get("country")
                        arr_city = arr_airport.get("city")
                        arr_lat = arr_airport.get("latitude")
                        arr_long = arr_airport.get("longitude")
                        airline_name = airline.get("name")
                        airline_code = airline.get("iata")
                        departure_time = dep_airport.get("estimated")
                        scheduled_dep_time = dep_airport.get("scheduled")
                        arrival_time = arr_airport.get("estimated") or arr_airport.get("scheduled")

                        if all([dep_iata, arr_iata, airline_code, flight_number, departure_time, arrival_time]):
                            insert_airport(dep_iata, dep_name, dep_icao, dep_country, dep_city, dep_lat, dep_long)
                            insert_airport(arr_iata, arr_name, arr_icao, arr_country, arr_city, arr_lat, arr_long)
                            insert_airline(airline_name, airline_code)
                            insert_flight_status(status)
                            insert_or_update_flight(flight_number, dep_iata, arr_iata, airline_code,
                                                    departure_time, arrival_time, scheduled_dep_time, status)
                    conn.commit()
                    print("Flight data inserted/updated successfully!")

            except Exception as e:
                print("Error fetching/inserting:", e)

            # Wait 5 minutes before fetching again
            time.sleep(300)

    except Exception as e:
        print("Database error:", e)
