import sqlite3
from datetime import datetime
import getpass  # For secure password input

class BusReservationSystem:
    def __init__(self):
        self.conn = sqlite3.connect('bus_reservation.db')
        self.create_tables()
        
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Create buses table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS buses (
            bus_id TEXT PRIMARY KEY,
            bus_name TEXT NOT NULL,
            source TEXT NOT NULL,
            destination TEXT NOT NULL,
            departure_time TEXT NOT NULL,
            arrival_time TEXT NOT NULL,
            total_seats INTEGER NOT NULL,
            available_seats INTEGER NOT NULL,
            fare REAL NOT NULL
        )
        ''')
        
        # Create bookings table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id TEXT PRIMARY KEY,
            bus_id TEXT NOT NULL,
            passenger_name TEXT NOT NULL,
            passenger_age INTEGER NOT NULL,
            passenger_gender TEXT NOT NULL,
            seats_booked INTEGER NOT NULL,
            contact_number TEXT NOT NULL,
            total_fare REAL NOT NULL,
            booking_date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (bus_id) REFERENCES buses (bus_id)
        )
        ''')
        
        # Create admin table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
        ''')
        
        # Insert default admin if not exists
        cursor.execute("SELECT COUNT(*) FROM admin")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO admin VALUES (?, ?)", ('admin', 'admin123'))
        
        self.conn.commit()
    
    def add_bus(self):
        print("\n--- Add New Bus ---")
        bus_id = input("Enter Bus ID: ")
        
        # Check if bus already exists
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM buses WHERE bus_id = ?", (bus_id,))
        if cursor.fetchone()[0] > 0:
            print("Bus ID already exists!")
            return
        
        bus_name = input("Enter Bus Name: ")
        source = input("Enter Source: ")
        destination = input("Enter Destination: ")
        departure_time = input("Enter Departure Time (HH:MM): ")
        arrival_time = input("Enter Arrival Time (HH:MM): ")
        total_seats = int(input("Enter Total Seats: "))
        fare = float(input("Enter Fare per Seat: "))
        
        try:
            cursor.execute('''
            INSERT INTO buses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (bus_id, bus_name, source, destination, departure_time, 
                 arrival_time, total_seats, total_seats, fare))
            self.conn.commit()
            print(f"\nBus {bus_id} added successfully!")
        except sqlite3.Error as e:
            print(f"Error adding bus: {e}")
    
    def display_buses(self):
        print("\n--- Available Buses ---")
        print("{:<10} {:<15} {:<15} {:<15} {:<10} {:<10} {:<10} {:<10}".format(
            "Bus ID", "Bus Name", "Source", "Destination", "Departure", "Arrival", "Seats", "Fare"
        ))
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM buses")
        buses = cursor.fetchall()
        
        for bus in buses:
            print("{:<10} {:<15} {:<15} {:<15} {:<10} {:<10} {:<10} ₹{:<10}".format(
                bus[0], bus[1], bus[2], bus[3], bus[4], bus[5], 
                f"{bus[7]}/{bus[6]}", bus[8]
            ))
    
    def search_buses(self):
        print("\n--- Search Buses ---")
        source = input("Enter Source: ").lower()
        destination = input("Enter Destination: ").lower()
        date = input("Enter Date of Travel (DD-MM-YYYY): ")
        
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT * FROM buses 
        WHERE LOWER(source) = ? AND LOWER(destination) = ?
        ''', (source, destination))
        
        found_buses = cursor.fetchall()
        
        if found_buses:
            print("\n--- Available Buses ---")
            print("{:<10} {:<15} {:<15} {:<15} {:<10} {:<10} {:<10} {:<10}".format(
                "Bus ID", "Bus Name", "Source", "Destination", "Departure", "Arrival", "Seats", "Fare"
            ))
            for bus in found_buses:
                print("{:<10} {:<15} {:<15} {:<15} {:<10} {:<10} {:<10} ₹{:<10}".format(
                    bus[0], bus[1], bus[2], bus[3], bus[4], bus[5], 
                    f"{bus[7]}/{bus[6]}", bus[8]
                ))
        else:
            print("\nNo buses found for the given route.")
    
    def book_ticket(self):
        print("\n--- Book Ticket ---")
        bus_id = input("Enter Bus ID: ")
        
        # Check bus availability
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM buses WHERE bus_id = ?", (bus_id,))
        bus = cursor.fetchone()
        
        if not bus:
            print("Invalid Bus ID!")
            return
        
        passenger_name = input("Enter Passenger Name: ")
        passenger_age = int(input("Enter Passenger Age: "))
        passenger_gender = input("Enter Passenger Gender (M/F/O): ").upper()
        seats = int(input("Enter Number of Seats to Book: "))
        contact_number = input("Enter Contact Number: ")
        
        if bus[7] < seats:  # available_seats
            print(f"Only {bus[7]} seats available!")
            return
        
        # Generate booking ID
        booking_id = f"RB{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Calculate total fare
        total_fare = seats * bus[8]  # fare
        
        try:
            # Add booking
            cursor.execute('''
            INSERT INTO bookings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (booking_id, bus_id, passenger_name, passenger_age, passenger_gender,
                 seats, contact_number, total_fare, 
                 datetime.now().strftime("%d-%m-%Y %H:%M:%S"), 'Confirmed'))
            
            # Update available seats
            cursor.execute('''
            UPDATE buses SET available_seats = available_seats - ? 
            WHERE bus_id = ?
            ''', (seats, bus_id))
            
            self.conn.commit()
            
            print("\n--- Booking Confirmed ---")
            print(f"Booking ID: {booking_id}")
            print(f"Bus: {bus[1]} ({bus_id})")
            print(f"Route: {bus[2]} to {bus[3]}")
            print(f"Passenger: {passenger_name} ({passenger_age}/{passenger_gender})")
            print(f"Seats Booked: {seats}")
            print(f"Total Fare: ₹{total_fare}")
            print(f"Status: Confirmed")
        except sqlite3.Error as e:
            print(f"Error during booking: {e}")
    
    def view_booking(self):
        print("\n--- View Booking ---")
        booking_id = input("Enter Booking ID: ")
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM bookings WHERE booking_id = ?", (booking_id,))
        booking = cursor.fetchone()
        
        if not booking:
            print("Invalid Booking ID!")
            return
        
        cursor.execute("SELECT * FROM buses WHERE bus_id = ?", (booking[1],))
        bus = cursor.fetchone()
        
        print("\n--- Booking Details ---")
        print(f"Booking ID: {booking[0]}")
        print(f"Booking Date: {booking[8]}")
        print(f"Bus: {bus[1]} ({bus[0]})")
        print(f"Route: {bus[2]} to {bus[3]}")
        print(f"Departure: {bus[4]} on {booking[8].split()[0]}")
        print(f"Passenger: {booking[2]} ({booking[3]}/{booking[4]})")
        print(f"Seats Booked: {booking[5]}")
        print(f"Total Fare: ₹{booking[7]}")
        print(f"Status: {booking[9]}")
        print(f"Contact: {booking[6]}")
    
    def cancel_booking(self):
        print("\n--- Cancel Booking ---")
        booking_id = input("Enter Booking ID: ")
        
        cursor = self.conn.cursor()
        
        # Get booking details
        cursor.execute("SELECT * FROM bookings WHERE booking_id = ?", (booking_id,))
        booking = cursor.fetchone()
        
        if not booking:
            print("Invalid Booking ID!")
            return
        
        if booking[9] == 'Cancelled':  # status
            print("Booking is already cancelled!")
            return
        
        try:
            # Update available seats
            cursor.execute('''
            UPDATE buses SET available_seats = available_seats + ? 
            WHERE bus_id = ?
            ''', (booking[5], booking[1]))  # seats_booked, bus_id
            
            # Update booking status
            cursor.execute('''
            UPDATE bookings SET status = 'Cancelled' 
            WHERE booking_id = ?
            ''', (booking_id,))
            
            self.conn.commit()
            
            print("\nBooking has been cancelled successfully!")
            print(f"Booking ID: {booking_id}")
            print(f"Refund Amount: ₹{booking[7]} (if applicable)")
        except sqlite3.Error as e:
            print(f"Error during cancellation: {e}")
    
    def admin_menu(self):
        while True:
            print("\n--- Admin Menu ---")
            print("1. Add New Bus")
            print("2. View All Buses")
            print("3. View All Bookings")
            print("4. Add New Admin")
            print("5. Back to Main Menu")
            
            choice = input("Enter your choice: ")
            
            if choice == '1':
                self.add_bus()
            elif choice == '2':
                self.display_buses()
            elif choice == '3':
                print("\n--- All Bookings ---")
                cursor = self.conn.cursor()
                cursor.execute("SELECT * FROM bookings")
                bookings = cursor.fetchall()
                for booking in bookings:
                    print(f"{booking[0]} - {booking[2]} - {booking[1]} - {booking[9]}")
            elif choice == '4':
                self.add_admin()
            elif choice == '5':
                break
            else:
                print("Invalid choice!")
    
    def add_admin(self):
        print("\n--- Add New Admin ---")
        username = input("Enter new admin username: ")
        password = getpass.getpass("Enter new admin password: ")
        confirm_password = getpass.getpass("Confirm password: ")
        
        if password != confirm_password:
            print("Passwords don't match!")
            return
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO admin VALUES (?, ?)", (username, password))
            self.conn.commit()
            print("Admin added successfully!")
        except sqlite3.IntegrityError:
            print("Username already exists!")
        except sqlite3.Error as e:
            print(f"Error adding admin: {e}")
    
    def user_menu(self):
        while True:
            print("\n--- User Menu ---")
            print("1. Search Buses")
            print("2. Book Ticket")
            print("3. View Booking")
            print("4. Cancel Booking")
            print("5. Back to Main Menu")
            
            choice = input("Enter your choice: ")
            
            if choice == '1':
                self.search_buses()
            elif choice == '2':
                self.book_ticket()
            elif choice == '3':
                self.view_booking()
            elif choice == '4':
                self.cancel_booking()
            elif choice == '5':
                break
            else:
                print("Invalid choice!")
    
    def admin_login(self):
        username = input("Enter admin username: ")
        password = getpass.getpass("Enter admin password: ")
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM admin WHERE username = ? AND password = ?", 
                      (username, password))
        if cursor.fetchone():
            return True
        return False
    
    def run(self):
        while True:
            print("\n=== Bus Reservation System ===")
            print("1. User Menu")
            print("2. Admin Login")
            print("3. Exit")
            
            choice = input("Enter your choice: ")
            
            if choice == '1':
                self.user_menu()
            elif choice == '2':
                if self.admin_login():
                    self.admin_menu()
                else:
                    print("Invalid credentials!")
            elif choice == '3':
                print("Thank you for using Bus Reservation System!")
                self.conn.close()
                break
            else:
                print("Invalid choice!")

if __name__ == "__main__":
    system = BusReservationSystem()
    system.run()