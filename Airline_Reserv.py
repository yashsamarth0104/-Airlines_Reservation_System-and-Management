import xml.etree.ElementTree as ElemTree
import pandas as pd
import csv
import mysql.connector
from collections import defaultdict

# Load the IATA File Into the airports Table
airports_list = list()
iata_file = open('iata.txt', 'r')

for airport in iata_file:
    airports_list.append(airport.strip())

# Connect to the SQL Server
mydb = mysql.connector.connect(host="localhost", user="root", passwd="Violin2007!", database="airline")
mycursor = mydb.cursor()

# Populate the airports Relation
for airport in airports_list:
    mycursor.execute("INSERT INTO airline.airports(airportID) VALUES('" + airport + "')")

# Close the Connection
mydb.commit()
mycursor.close()

# Collect the Data From the PNR File

# Create a Default Values List
## [firstName, lastName, address, age, origin, dest, travelDate, class, bookingTime, npass]
default_values = ['AAAAA', 'AAAAA', 'AAAAA', 0, '***', '***', '0000-00-00', 'economy', '99:99:99', -1]

# Create a List of the Passenger Information Lists
passengers_full_list = list()

# Define the Tag Label Indicators
ss = "urn:schemas-microsoft-com:office:spreadsheet"
worksheet_label = '{%s}Worksheet' % ss
table_label = '{%s}Table' % ss
row_label = '{%s}Row' % ss
cell_label = '{%s}Cell' % ss
data_label = '{%s}Data' % ss
S
tree = ElemTree.parse("PNR.xml")
root = tree.getroot()

for worksheet in root.findall(worksheet_label):
    # Verify Only Taking Data From Worksheet 1
    if worksheet.attrib["{" + ss + "}Name"] != "Sheet1":
        continue
    else:
        # Go Through Each Passenger in PNR.xml
        for table in worksheet.findall(table_label):
            for row in table.findall(row_label):
                # Create a List to Store All Details for One Passenger
                passenger_info_list = list()

                # Create a Counter for the Details
                detail = 0

                for cell in row.findall(cell_label):
                    # Check for an Empty Cell
                    if "{" + ss + "}Index" in cell.attrib:
                        # Add the Default Value for That Detail to passenger_info
                        passenger_info_list.append(default_values[detail])

                        # Increase the Detail Counter
                        detail += 1

                    for data in cell.findall(data_label):
                        # Add the Detail Data to passenger_info
                        passenger_info_list.append(data.text.strip())

                    # Increase the Detail Counter
                    detail += 1

                # Add the Completed passenger_info List to the Full List of Passenger Information
                passengers_full_list.append(passenger_info_list)

# Make the passengers_full_list a DataFrame
passengers_df = pd.DataFrame(passengers_full_list[1:],
                             columns=["firstName", "lastName", "address", "age", "origin", "dest",
                                      "travelDate", "flightClass", "bookingTime", "npass"])
# Ensure bookingTime Values Have the Correct Format
index = 0
for time in passengers_df.bookingTime:
    # If Missing Second Digit for Seconds
    if time[-2] == ":":
        passengers_df.bookingTime[index] = passengers_df.bookingTime[index][:-1] + "0" + \
                                           passengers_df.bookingTime[index][-1]
    index += 1

index = 0
for time in passengers_df.bookingTime:
    # If Missing Second Digit for Minutes
    if time[-5] == ":":
        passengers_df.bookingTime[index] = passengers_df.bookingTime[index][:-4] + "0" + passengers_df.bookingTime[
                                                                                             index][-4:]
    index += 1

index = 0
for time in passengers_df.bookingTime:
    # If Missing Second Digit for Hours
    if time[1] == ":":
        passengers_df.bookingTime[index] = "0" + passengers_df.bookingTime[index]
    index += 1

# Modify the Columns' Data Types to Reflect the Data
passengers_df.age = passengers_df.age.astype('int')
passengers_df.npass = passengers_df.npass.astype('int')

# Create a New DataFrame to Remove Rows Missing origin, dest, travelDate, and/or npass Values
passengers_df_final = passengers_df[(passengers_df.origin != "***") & (passengers_df.dest != "***") &
                                    (passengers_df.travelDate != "0000-00-00") & (passengers_df.npass != -1)]

# Add a Column for the Total Number of Passengers on a Reservation
passengers_df_final["totalPass"] = passengers_df_final["npass"].transform(lambda x: x + 1)

# Populate the passenger_info Relation
# Connect to the SQL Server
mydb = mysql.connector.connect(host="localhost", user="root", passwd="Violin2007!", database="airline")
mycursor = mydb.cursor()

# Create a Dictionary for Passenger IDs
passengerID_dict = dict()
idNum = 1

for row in passengers_df_final.itertuples():
    mycursor.execute("INSERT INTO airline.passenger_info(firstName, lastName, address, age) VALUES(%s, %s, %s, %s)",
                     (row[1], row[2], row[3], row[4]))
    passengerID_dict[(row[1], row[2], row[3], row[4])] = idNum
    idNum += 1

# Create Index for passenger_info Relation
mycursor.execute("CREATE INDEX passInfo ON airline.passenger_info(firstName, lastName, address, age)")

# Close the Connection
mydb.commit()
mycursor.close()

# Create Seats for Flights
## First Class
first_class = list()

letters = ['A', 'D', 'G', 'K']

for i in range(1, 14):
    for letter in letters:
        if len(first_class) < 49:
            first_class.append(str(i) + letter)
        elif len(first_class) == 49:
            first_class.append(str(i) + 'K')

# Business Class
business_class = list()

even_letters = ['A', 'D', 'F', 'H']
odd_letters = ['C', 'E', 'G', 'K']

for i in range(14, 39):
    if i % 2 == 0:
        for letter in even_letters:
            if len(business_class) < 100:
                business_class.append(str(i) + letter)
    else:
        for letter in odd_letters:
            if len(business_class) < 100:
                business_class.append(str(i) + letter)

# Economy Class
economy_class = list()

letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K']

for i in range(39, 54):
    for letter in letters:
        if len(economy_class) < 150:
            economy_class.append(str(i) + letter)

# Populate the seats Relation
# Connect to the SQL Server
mydb = mysql.connector.connect(host="localhost", user="root", passwd="Violin2007!", database="airline")
mycursor = mydb.cursor()

# First Class
for seat in first_class:
    mycursor.execute("INSERT INTO airline.seats(class, seatNumber) VALUES(%s, %s)",
                     ('first', seat))

# Business Class
for seat in business_class:
    mycursor.execute("INSERT INTO airline.seats(class, seatNumber) VALUES(%s, %s)",
                     ('business', seat))

# Economy Class
for seat in economy_class:
    mycursor.execute("INSERT INTO airline.seats(class, seatNumber) VALUES(%s, %s)",
                     ('economy', seat))

# Close the Connection
mydb.commit()
mycursor.close()


# Create Flights
# Function to Reserve an Available Seat on the Flight
def reserve_seat(flight_class, class_index):
    if flight_class == "first":
        index = 50 - class_index["first"]
        seat = first_class[index]

    elif flight_class == "business":
        index = 100 - class_index["business"]
        seat = business_class[index]

    else:
        index = 150 - class_index["economy"]
        seat = economy_class[index]

    return seat


# Create a List of All Possible Flight Times
flight_times = ['23:00:00', '22:00:00', '21:00:00', '20:00:00', '19:00:00', '18:00:00', '17:00:00', '16:00:00',
                '15:00:00',
                '14:00:00', '13:00:00', '12:00:00', '11:00:00', '10:00:00', '9:00:00', '8:00:00', '7:00:00', '6:00:00']

# Obtain the Airports in the Dataset
airports = passengers_df_final.origin.unique()
airports.sort()

# Obtain the Travel Dates in the Dataset
travel_dates = passengers_df_final.travelDate.unique()
travel_dates.sort()

# Create a List of All Flights
flights_list = list()
# Create a List of All Reservations
reservations_list = list()
# Create a List of All Booked Seats with Corresponding PassengerID
passengers_seats_list = list()

for date in travel_dates:
    # Create a DataFrame for Each Date
    date_df = passengers_df_final[passengers_df_final.travelDate == date]
    for origin_airport in airports:
        for destination_airport in airports:
            if origin_airport != destination_airport:
                # Create a Dictionary for the Number of Remaining Seats by Class
                class_index_dict = {"first": 50, "business": 100, "economy": 150}

                # Create a DataFrame for the Route
                reservations_df = date_df[(date_df.origin == origin_airport) & (date_df.dest == destination_airport)]
                # Sort the DataFrame by bookingTime to Reserve Seats by First Book First Serve
                reservations_df = reservations_df.sort_values(by="bookingTime")

                # Create a Variable for the Number of Passengers Who Still Need a Seat
                remaining_passengers = reservations_df.totalPass.sum()
                # Create a Variable for the Number of Available Seats Open on the Flight
                remaining_seats = 300
                # Create a Variable for the Number of Flights Created for the Route
                nflights = 0

                # Format departure to Contain Both Flight Data and Time
                departure = date + " " + flight_times[nflights]

                # Add the Flight to the flights Relation
                flights_list.append((departure, origin_airport, destination_airport))

                # Iterate Through Each Reservation in the Route
                for row in reservations_df.itertuples():
                    passenger = 0
                    # Number of Seats Required for the Reservation
                    reservation_total_pass = row.totalPass
                    # Requested Seating Class
                    seat_class = row.flightClass

                    # Not Enough Passengers to Warrant an Additional Plane
                    if (remaining_seats - reservation_total_pass < 0) & (remaining_passengers < 150):
                        # Cancel Reservation
                        continue

                    # Enough Passengers to Warrant an Additional Plane
                    elif (remaining_seats - reservation_total_pass < 0) & (remaining_passengers > 150):
                        # Create an Additional Flight for the Route
                        flight_index += 1
                        nflights += 1
                        remaining_seats = 300
                        class_index_dict = {"first": 50, "business": 100, "economy": 150}
                        departure = date + " " + flight_times[nflights]

                        # Add the Flight to the flights Relation
                        flights_list.append((departure, origin_airport, destination_airport))

                    # Add Passenger's Reservation to the reservations_list
                    reservations_list.append((passengerID_dict[(row[1], row[2], row[3], row[4])], len(flights_list),
                                              origin_airport, destination_airport, departure, row[8], row[9], row[10]))

                    # Reserve a Seat for Each Passenger on the Reservation
                    while passenger < reservation_total_pass:
                        # Attempt to Assign Seat in Requested Class
                        if class_index_dict[seat_class] - 1 >= 0:
                            seat = reserve_seat(seat_class, class_index_dict)
                            class_index_dict[seat_class] -= 1

                        # Assign Seat in a Class with an Available Seat
                        elif class_index_dict["first"] - 1 >= 0:
                            seat = reserve_seat("first", class_index_dict)
                            class_index_dict["first"] -= 1

                        elif class_index_dict["business"] - 1 >= 0:
                            seat = reserve_seat("business", class_index_dict)
                            class_index_dict["business"] -= 1

                        else:
                            seat = reserve_seat("economy", class_index_dict)
                            class_index_dict["economy"] -= 1

                        # Add Tuple of passengerID, flightID, and Reserved Seat to passengers_seats_list
                        passengers_seats_list.append(
                            (passengerID_dict[(row[1], row[2], row[3], row[4])], len(flights_list), seat))

                        passenger += 1
                        remaining_seats -= 1
                        remaining_passengers -= 1

# Populate the Flights Relation
# Connect to the SQL Server
mydb = mysql.connector.connect(host="localhost", user="root", passwd="Violin2007!", database="airline")
mycursor = mydb.cursor()

# Populate the flights Relation
for flight in flights_list:
    mycursor.execute("INSERT INTO airline.flights(departureTime, originAirport, destinationAirport) VALUES(%s, %s, %s)",
                     (flight[0], flight[1], flight[2]))

# Create Index for flights Relation
mycursor.execute("CREATE INDEX flightsInfo ON flights(departureTime, originAirport, destinationAirport)")

# Populate the Reservations Relation
for reservation in reservations_list:
    mycursor.execute(
        "INSERT INTO airline.reservations(passengerID, flightID, originAirport, destinationAirport, departure, class, bookingTime, npass) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",
        (reservation[0], reservation[1], reservation[2], reservation[3], reservation[4],
         reservation[5], reservation[6], reservation[7]))

# Create the Derived Table seats_on_flights
mycursor.execute(
    "CREATE TABLE seats_on_flights AS SELECT airline.flights.flightID, airline.seats.class, airline.seats.seatNumber FROM flights, seats")

# Add passenger Column
mycursor.execute("ALTER TABLE seats_on_flights ADD COLUMN passenger INT NOT NULL DEFAULT 0 AFTER seatNumber")
# Add Primary Key
mycursor.execute("ALTER TABLE seats_on_flights ADD PRIMARY KEY (flightID, seatNumber)")
# Add Foreign Key
mycursor.execute("ALTER TABLE seats_on_flights ADD FOREIGN KEY (flightID) REFERENCES flights(flightID)")
# Add Another Foreign Key
mycursor.execute("ALTER TABLE seats_on_flights ADD FOREIGN KEY (seatNumber) REFERENCES seats(seatNumber)")
# Create Index
mycursor.execute("CREATE INDEX flightSeat ON seats_on_flights(flightID,seatNumber)")

# Update seats_on_flights with Corresponding passengerID
for passengerSeat in passengers_seats_list:
    mycursor.execute("UPDATE airline.seats_on_flights SET passenger = " + str(passengerSeat[0]) +
                     " WHERE flightID = '" + str(passengerSeat[1]) + "' AND seatNumber = '" + passengerSeat[2] + "'")

# Create the Derived Table checkIn
mycursor.execute(
    "CREATE TABLE checkIn AS SELECT airline.seats_on_flights.passenger, airline.seats_on_flights.flightID, airline.seats_on_flights.seatNumber, airline.flights.departureTime, airline.flights.originAirport, airline.flights.destinationAirport FROM airline.seats_on_flights, airline.flights WHERE airline.seats_on_flights.flightID = airline.flights.flightID")

# Remove Any Seats Unassigned to a Passenger
mycursor.execute("DELETE FROM airline.checkIn WHERE passenger = 0")
# Add checkedIn Flag Column
mycursor.execute("ALTER TABLE checkIn ADD COLUMN checkedIn INT NOT NULL DEFAULT 0 AFTER destinationAirport")
# Add Primary Key
mycursor.execute(
    "ALTER TABLE checkIn ADD PRIMARY KEY (flightID, seatNumber, departureTime, originAirport, destinationAirport)")
# Create Index
mycursor.execute("CREATE INDEX checkInID ON airline.checkIn(passenger,flightID)")

# Close the Connection
mydb.commit()
mycursor.close()


# Create a checkIn Function
def checkIn_passenger(passengerID, flightID):
    # Connect to the SQL Server
    mydb = mysql.connector.connect(host="localhost", user="root", passwd="Violin2007!", database="airline")
    mycursor = mydb.cursor()

    # Check In All Seats Connected to Passenger ID
    mycursor.execute("UPDATE airline.checkIn SET checkedIn = 1 WHERE passenger = '" + str(passengerID) +
                     "' AND flightID = '" + str(flightID) + "'")

    mydb.commit()
    mycursor.close()

    return
