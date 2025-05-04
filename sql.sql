-- Create the Airport table to store airport details
CREATE TABLE Airport(
    airport_id SERIAL PRIMARY KEY,  -- Unique identifier for each airport
    name VARCHAR(100),  -- Name of the airport
    IATA_code CHAR(3) UNIQUE,  -- 3-letter IATA airport code (e.g., JFK)
    ICAO_code CHAR(4) UNIQUE,  -- 4-letter ICAO airport code (e.g., KJFK)
    country VARCHAR(100),  -- Country where the airport is located
    city VARCHAR(100),  -- City where the airport is located
    latitude DECIMAL(9,6),  -- Geographic latitude of the airport
    longitude DECIMAL(9,6)  -- Geographic longitude of the airport
);

-- Create the Airlines table to store airline information
CREATE TABLE Airlines (
    airline_id SERIAL PRIMARY KEY,  -- Unique identifier for each airline
    name VARCHAR(255),  -- Airline name
    code VARCHAR(10) UNIQUE  -- Unique airline code (e.g., LH for Lufthansa)
);

-- Create the FlightStatus table to track flight statuses
CREATE TABLE FlightStatus (
    status_id SERIAL PRIMARY KEY,  -- Unique identifier for each status
    status_name VARCHAR(50)  -- Status name (e.g., "On Time", "Delayed", "Cancelled")
);

-- Create the Flights table to store flight details
CREATE TABLE Flights (
    flight_id SERIAL PRIMARY KEY,  -- Unique identifier for each flight
    flight_number VARCHAR(20) UNIQUE,  -- Unique flight number (e.g., LH123)
    departure_airport_id INT REFERENCES Airport(airport_id),  -- Foreign key referencing the departure airport
    arrival_airport_id INT REFERENCES Airport(airport_id),  -- Foreign key referencing the arrival airport
    airline_id INT REFERENCES Airlines(airline_id),  -- Foreign key referencing the airline
    departure_time TIMESTAMP,  -- Scheduled departure time
    arrival_time TIMESTAMP,  -- Scheduled arrival time
    status_id INT REFERENCES FlightStatus(status_id)  -- Foreign key referencing flight status
);

-- Create the Passengers table to store passenger details
CREATE TABLE Passengers (
    passenger_id SERIAL PRIMARY KEY,  -- Unique identifier for each passenger
    name VARCHAR(255),  -- Passenger name
    email VARCHAR(255) UNIQUE,  -- Unique email address for each passenger
    phone VARCHAR(15),  -- Contact phone number
    flight_id INT REFERENCES Flights(flight_id)  -- Foreign key referencing the flight the passenger is booked on
);

-- Insert sample data into the Airport table
INSERT INTO Airport (name, IATA_code, ICAO_code, country, city, latitude, longitude)
VALUES 
('Frankfurt Airport', 'FRA', 'EDDF', 'Germany', 'Frankfurt', 50.0333, 8.5706),
('Munich Airport', 'MUC', 'EDDM', 'Germany', 'Munich', 48.3538, 11.7861),
('Berlin Brandenburg Airport', 'BER', 'EDDB', 'Germany', 'Berlin', 52.3667, 13.5033),
('Hamburg Airport', 'HAM', 'EDDH', 'Germany', 'Hamburg', 53.6304, 9.9882),
('Düsseldorf Airport', 'DUS', 'EDDL', 'Germany', 'Düsseldorf', 51.2895, 6.7668);

-- Insert sample data into the Airlines table
INSERT INTO Airlines (name, code)
VALUES 
('Lufthansa', 'LH'),
('Eurowings', 'EW'),
('Ryanair', 'FR'),
('easyJet', 'U2'),
('British Airways', 'BA');

-- Insert sample data into the FlightStatus table
INSERT INTO FlightStatus (status_name)
VALUES 
('On Time'),
('Delayed'),
('Cancelled');

-- Insert sample flight data into the Flights table
INSERT INTO Flights (flight_number, departure_airport_id, arrival_airport_id, airline_id, departure_time, arrival_time, status_id)
VALUES 
('LH123', 1, 2, 1, '2025-03-20 08:30:00', '2025-03-20 10:45:00', 1),
('EW456', 2, 3, 2, '2025-03-20 12:15:00', '2025-03-20 14:30:00', 2),
('FR789', 3, 4, 3, '2025-03-20 16:45:00', '2025-03-20 18:00:00', 1),
('U2123', 4, 5, 4, '2025-03-20 09:00:00', '2025-03-20 11:10:00', 3),
('BA567', 5, 1, 5, '2025-03-20 13:50:00', '2025-03-20 16:00:00', 2),
('LH789', 1, 3, 1, '2025-03-20 14:00:00', '2025-03-20 16:30:00', 1),
('EW890', 2, 4, 2, '2025-03-20 17:30:00', '2025-03-20 19:45:00', 1),
('FR345', 3, 5, 3, '2025-03-20 20:00:00', '2025-03-20 22:10:00', 2),
('U2789', 4, 1, 4, '2025-03-20 06:15:00', '2025-03-20 08:25:00', 1),
('BA678', 5, 2, 5, '2025-03-20 11:45:00', '2025-03-20 14:00:00', 1);

-- Insert sample passenger data into the Passengers table
INSERT INTO Passengers (name, email, phone, flight_id)
VALUES 
('Max Müller', 'max.muller@email.com', '49123456789', 1),
('Anna Schmidt', 'anna.schmidt@email.com', '49111223344', 2),
('Lukas Weber', 'lukas.weber@email.com', '49155667788', 3),
('Sophia Fischer', 'sophia.fischer@email.com', '49199887766', 4),
('Leon Becker', 'leon.becker@email.com', '49122334455', 5),
('Emma Wagner', 'emma.wagner@email.com', '49133445566', 6),
('Noah Hoffmann', 'noah.hoffmann@email.com', '49177889900', 7),
('Mia Schmitz', 'mia.schmitz@email.com', '49166778899', 8),
('Felix Klein', 'felix.klein@email.com', '49188990011', 9),
('Hannah Schulz', 'hannah.schulz@email.com', '49155667788', 10);


--SQL Queries 
--Query 1: Retrieve all flights from a specific airport (e.g., Frankfurt - FRA)
SELECT * FROM Flights 
WHERE departure_airport_id = (SELECT airport_id FROM Airport WHERE IATA_code = 'FRA');


-- Query 2: Identify flights delayed by more than 2 hours
SELECT * FROM Flights 
WHERE status_id = (SELECT status_id FROM FlightStatus WHERE status_name = 'Delayed');


--Query 3: Fetch flight details using the flight number
SELECT * FROM Flights 
WHERE flight_number = 'LH123';
