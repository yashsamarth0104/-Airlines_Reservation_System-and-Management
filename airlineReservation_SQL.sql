--Create the Database
CREATE DATABASE airline;

--Specify to Use the airline Database
USE airline;

--Create the Relations
--Passenger Information Relation
CREATE TABLE passenger_info
	(
	Airline_ID INT NOT NULL AUTO_INCREMENT,
    Passenger_ID VARCHAR(100) NOT NULL,
    Name VARCHAR(100) NOT NULL,
    Address VARCHAR(200) NOT NULL,
	Phone_Number Int(10) NOT NULL,
    Email VARCHAR(100) NOT NULL,
	Gender CHAR(1) NOT NUll,
    Nationality VARCHAR(100) NOT NULL,
    Age INT NOT NULL,
	Luggage_Count CHAR(1) NOT NUll,
    UNIQUE KEY (Name, Address,Age),
    PRIMARY KEY (Passenger_ID)
    );

--Seat Relation
CREATE TABLE seats
	(
	class VARCHAR(100) NOT NULL,
    seatNumber VARCHAR(10) NOT NULL,
    PRIMARY KEY (seatNumber)
    );

--Airports Relation
CREATE TABLE airports
	(
	airportID CHAR(3) NOT NULL,  --(IATA code is a unique ID given to all the airports.)
    PRIMARY KEY (airportID)
	);

--Flights Relation
CREATE TABLE flights
	(
	Airline_ID INT NOT NULL AUTO_INCREMENT,
	Airline_name VARCHAR(100) NOT NULL,
	Departure_Destination VARCHAR(100) NOT NULL,
	Departure DATETIME NOT NULL,
	Arrival_Destination VARCHAR(100) NOT NULL,
	Arrival DATETIME NOT NULL,
	Duration Int(2) NOT NULL,
	Total_Seats Int(3) NOT NULL,
    Status VARCHAR(100) NOT NULL,
    PRIMARY KEY (Airline_ID),
    UNIQUE KEY (Departure, Departure_Destination, Arrival_Destination),
    FOREIGN KEY (Departure_Destination) REFERENCES airports(airline_ID),
    FOREIGN KEY (Arrival_Destination) REFERENCES airports(airline_ID)
    );

--Reservation Relation
CREATE TABLE reservations
	(
	Airline_ID VARCHAR(100) NOT NULL,AUTO_INCREMENT,
	Ticket_NO VARCHAR(100) NOT NULL,
	Seat_No INT NOT NULL,
    Meal_Status CHAR(3) NOT NULL,
	Category VARCHAR(100) NOT NULL,
    Departure DATETIME NOT NULL,
	originAirport CHAR(3) NOT NULL,
    Departure_Destination CHAR(3) NOT NULL,
    Arrival DATETIME NOT NULL,
    Arrival_Destination CHAR(3) NOT NULL,
	Luggage_Count CHAR(1) NOT NUll,
	Gate INT(2) NOT NULL,
    PRIMARY KEY (Airline_ID),
    FOREIGN KEY (Ticket_No) REFERENCES passenger_info(passengerID),
    FOREIGN KEY (AirlineID) REFERENCES flights(Airline_ID),
	FOREIGN KEY (Departure_Destination) REFERENCES airports(airportID),
    FOREIGN KEY (Arrival_Destination) REFERENCES airports(airportID)
	);


# SQL QUERIES
----------------------------------------------------------------------
(Q1) Show the flight schedule between two airports in any two dates
 (i.e.:- Between Indira Gandhi International Airport (New Delhi) and Chhatrapati Shivaji Maharaj International Airport (Mumbai) on Jan. 1, 2021 and Jan. 2, 2021)

SELECT Departure_Destination, destinationAirport, Departure 
	FROM flights 
	WHERE ( (Departure_Destination = 'DEL') OR (Departure_Destination = 'BOM') ) 
	AND ( (Arrival_Destination = 'DEL') OR (Arrival_Destination = 'BOM') )
	AND ( (Departure LIKE '2021-01-01%') OR (Departure LIKE '2021-01-02%') );

-----------------------------------------------------------------------
    
(Q2) Rank top 3 {source, destination} airports based on the booking requests for a week.
	(i.e.:- Between Jan. 1, 2021 and Jan. 7, 2021)

SELECT Departure_Destination, Arrival_Destination, COUNT(Seats) AS bokRequests
FROM checkIn
WHERE (departureTime LIKE '2021-01-01%') OR (departureTime LIKE '2021-01-02%') OR (departureTime LIKE '2021-01-03%')
		OR (departureTime LIKE '2021-01-04%') OR (departureTime LIKE '2021-01-05%') OR (departureTime LIKE '2021-01-06%')
			OR (departureTime LIKE '2021-01-07%')
GROUP BY Departure_Destination, Arrival_Destination
ORDER BY bokRequests DESC
LIMIT 3;

-------------------------------------------------------------------------

(Q3) Next available (has seats) flight between given airports.
     (i.e.:-From Swami Vivekananda Airport (Raipur) to Indira Gandhi International Airport (New Delhi)

SELECT seats_on_flights.flightID, flights.Departure_Destination, flights.Arrival_Destination, 
			flights.departureTime, COUNT(seats_on_flights.flightID) AS remainingSeats
FROM seats_on_flights
JOIN flights ON seats_on_flights.flightID = flights.flightID
WHERE Departure_Destination = 'RPR'
AND Arrival_Destination = 'DEL'
AND passenger = 0
GROUP BY flightID
ORDER BY departureTime
LIMIT 1;

-------------------------------------------------------------------------

(Q4) Average occupancy rate (%full) for all flights between two cities.
   (i.e.:- Between Chhatrapati Shivaji Maharaj International Airport (Mumbai) and London Heathrow International Airport)

SELECT Departure_Destination, Arrival_Destination, (COUNT(Seats)/(COUNT(DISTINCT Airline_ID)*300))*100 AS '%full' 
FROM checkIn 
WHERE ( (Departure_Destination = 'BOM') OR (Departure_Destination = 'LHR') ) AND ( (Arrival_Destination = 'BOM') OR (Arrival_Destination = 'LHR') )
GROUP BY Departure_Destination;

-------------------------------------------------------------------------