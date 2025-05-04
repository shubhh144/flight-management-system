import psycopg2  
import requests  

# Database Configuration
DB_NAME = "airline"
DB_USER = "USER_NAME" #Enter the USER_NAME of database management system
DB_PASSWORD = "PASSWORD" #Enter the database system password
DB_HOST = "localhost"  # If running locally
DB_PORT = "5432"   

try:
    # Establish connection to PostgreSQL database
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()

    # Test connection by retrieving database version
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    print("Connected to PostgreSQL Database:", db_version)

    # Function to insert airport details into the database
    def insert_airport(iata_code, name, icao_code, country, city, latitude, longitude):
        """Insert airport data if not already present."""
        if iata_code:  # Ensure IATA code is not None
            cursor.execute("""
                INSERT INTO Airport (IATA_code, name, ICAO_code, country, city, latitude, longitude)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (IATA_code) DO NOTHING;
            """, (iata_code, name, icao_code, country, city, latitude, longitude))

    # Function to insert airline details
    def insert_airline(name, code):
        """Insert airline if not present."""
        if code:  # Ensure airline code is not None
            cursor.execute("""
                INSERT INTO Airlines (name, code)
                VALUES (%s, %s)
                ON CONFLICT (code) DO NOTHING;
            """, (name, code))

    # Function to insert flight status
    def insert_flight_status(status_name):
        """Insert flight status if not present."""
        if status_name:
            cursor.execute("""
                INSERT INTO FlightStatus (status_name)
                VALUES (%s)
                ON CONFLICT (status_name) DO NOTHING;
            """, (status_name,))

    # Function to insert or update flight details
    def insert_or_update_flight(flight_number, dep_iata, arr_iata, airline_code, dep_time, arr_time, scheduled_dep_time, status_name):
        """Insert a new flight if it doesn't exist, or update the status and scheduled time if it does."""
        cursor.execute("""
            INSERT INTO Flights (flight_number, departure_airport_id, arrival_airport_id, airline_id, 
                                departure_time, arrival_time, scheduled_departure_time, status_id)
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
        """, (flight_number, dep_iata, arr_iata, airline_code, dep_time, arr_time, scheduled_dep_time, status_name, status_name))

    # Fetch real-time flight data from AviationStack API
    api = "YOUR_API_KEY" #Enter your API key of aviationstack
    response = requests.get(f"https://api.aviationstack.com/v1/flights?access_key={api}")
    response.raise_for_status()
    data = response.json()

    # Process the flight data
    if "data" in data:
        for flight in data["data"]:
            # Extract relevant attributes
            flight_number = flight.get("flight", {}).get("iata")
            dep_airport = flight.get("departure", {})
            arr_airport = flight.get("arrival", {})
            airline = flight.get("airline", {})
            status = flight.get("flight_status")

            print("Processing Flight:", flight_number)

            # Extract Departure Airport Details
            dep_iata = dep_airport.get("iata")
            dep_name = dep_airport.get("airport")
            dep_icao = dep_airport.get("icao")
            dep_country = dep_airport.get("country")
            dep_city = dep_airport.get("city")
            dep_lat = dep_airport.get("latitude")
            dep_long = dep_airport.get("longitude")

            # Extract Arrival Airport Details
            arr_iata = arr_airport.get("iata")
            arr_name = arr_airport.get("airport")
            arr_icao = arr_airport.get("icao")
            arr_country = arr_airport.get("country")
            arr_city = arr_airport.get("city")
            arr_lat = arr_airport.get("latitude")
            arr_long = arr_airport.get("longitude")

            # Extract Airline Details
            airline_name = airline.get("name")
            airline_code = airline.get("iata")

            # Extract Flight Timings
            departure_time = dep_airport.get("estimated")
            scheduled_departure_time = dep_airport.get("scheduled")
            arrival_time = arr_airport.get("estimated") or arr_airport.get("scheduled")

            # Insert Data into Database
            if all([dep_iata, arr_iata, airline_code, flight_number, departure_time, arrival_time]):
                insert_airport(dep_iata, dep_name, dep_icao, dep_country, dep_city, dep_lat, dep_long)
                insert_airport(arr_iata, arr_name, arr_icao, arr_country, arr_city, arr_lat, arr_long)
                insert_airline(airline_name, airline_code)
                insert_flight_status(status)
                insert_or_update_flight(flight_number, dep_iata, arr_iata, airline_code, departure_time, arrival_time, scheduled_departure_time, status)
    print("Data successfully inserted into PostgreSQL!")
    # Function to retrieve flights delayed by more than 2 hours
    def get_delayed_flights():
        """Retrieve all flights delayed by more than 2 hours."""
        cursor.execute("""
            SELECT flight_number, departure_time, scheduled_departure_time, (departure_time - scheduled_departure_time) AS delay_time
            FROM Flights 
            WHERE (departure_time - scheduled_departure_time) >= INTERVAL '2 hours';
        """)
        
        delayed_flights = cursor.fetchall()
        
        if delayed_flights:
            print("Flights delayed by more than 2 hours:")
            for flight in delayed_flights:
                print(f"Flight {flight[0]} delayed by {flight[3]}")
        else:
            print("No flights delayed by more than 2 hours.")

    # Call the function to get delayed flights
    get_delayed_flights()
    
    # Commit changes and close database connection
    conn.commit()
    cursor.close()
    conn.close()
    

except Exception as e:
    print("Error connecting to database:", e)

