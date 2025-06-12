import socket
import sqlite3
import json
from threading import Thread
import os

project_dir = os.path.dirname(__file__)
db = os.path.join(project_dir, "cinema.db")

class CinemaServer:
    def __init__(self, host='localhost', port=12345):
        # Initialize the server with a host, port, and database connection, populate the database with necessary tables
        self.host = host
        self.port = port
        self.conn = sqlite3.connect(db, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print("Server started on ", self.host, ":", str(self.port))

    def create_tables(self):
        # Create the necessary tables in the database if they do not exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Movies (
                movie_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                cinema_room INTEGER CHECK (8 > cinema_room > 0),
                release_date TEXT,
                end_date TEXT,
                tickets_available INTEGER,
                ticket_price REAL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Sales (
                sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_id INTEGER,
                customer_name TEXT,
                number_of_tickets INTEGER CHECK (number_of_tickets > 0),
                total_price REAL,
                FOREIGN KEY (movie_id) REFERENCES Movies(movie_id)
            ) 
        """)
        self.conn.commit()

    def handle_client(self, client_socket):
        # Handle incoming client requests in a separate thread
        while True:
            try:
                request = client_socket.recv(4096).decode()
                if not request:
                    break
                print("Received request: ", str(request))
                response = self.process_request(request)
                client_socket.sendall(response.encode())
            except Exception as e:
                print("Error:", str(e))
                break
        client_socket.close()

    def process_request(self, request):
        # determine the action based on the request and call the appropriate function
        try:
            data = json.loads(request)
            movie_data = data.get('movie')
            action = data.get('action')

            if action == 'add_movie':
                print("Movie data received:", movie_data)
                return self.add_movie(movie_data)
            elif action == 'get_movies':
                return self.get_movies()
            elif action == 'book_ticket':
                return self.book_ticket(data)
            elif action == 'remove_movie':
                return self.remove_movie(data)
            elif action == 'update_movie':
                return self.update_movie(movie_data)
            else:
                return json.dumps({"status": "error", "message": "Unknown action"})
        except json.JSONDecodeError:
            return json.dumps({"status": "error", "message": "Invalid JSON format"})
        
    def add_movie(self, data):
        # Add a new movie to the database
        try:
            self.cursor.execute("""
                INSERT INTO Movies (title, cinema_room, release_date, end_date, tickets_available, ticket_price)
                VALUES (?, ?, ?, ?, ?, ?)""", (data['title'], data['cinema_room'], data['release_date'], data['end_date'], data['tickets_available'], data['ticket_price']))
            self.conn.commit()
            return json.dumps({"status": "success", "message": "Movie added successfully"})
        except sqlite3.Error as e:
            return json.dumps({"status": "error", "message": str(e)})

    def get_movies(self):
        # Fetch the list of movies from the database
        try:
            self.cursor.execute("SELECT * FROM Movies")
            movies = self.cursor.fetchall()
            return json.dumps({"status": "success", "movies": movies})
        except sqlite3.Error as e:
            return json.dumps({"status": "error", "message": str(e)})

    def book_ticket(self, data):
        # Book a ticket for a movie and update the database accordingly
        try:
            self.cursor.execute("""
                INSERT INTO Sales (movie_id, customer_name, number_of_tickets, total_price)
                VALUES (?, ?, ?, ?)""", (data['movie_id'], data['customer_name'], data['number_of_tickets'], data['number_of_tickets'] * data['ticket_price']))
            self.cursor.execute("UPDATE Movies SET tickets_available = tickets_available - ? WHERE movie_id = ?", (data['number_of_tickets'], data['movie_id']))
            self.conn.commit()
            return json.dumps({"status": "success", "message": "Ticket booked successfully"})
        except sqlite3.Error as e:
            return json.dumps({"status": "error", "message": str(e)})

    def remove_movie(self, data):
        # Remove a movie from the database
        try:
            self.cursor.execute("DELETE FROM Movies WHERE movie_id = ?", (data['movie_id'],))
            self.conn.commit()
            return json.dumps({"status": "success", "message": "Movie removed successfully"})
        except sqlite3.Error as e:
            return json.dumps({"status": "error", "message": str(e)})
        
    def update_movie(self, data):
        # Update an existing movie in the database
        try:
            self.cursor.execute("""
                UPDATE Movies SET title = ?, cinema_room = ?, release_date = ?, end_date = ?, tickets_available = ?, ticket_price = ?
                WHERE movie_id = ?""", (data['title'], data['cinema_room'], data['release_date'], data['end_date'], data['tickets_available'], data['ticket_price'], data['movie_id']))
            self.conn.commit()
            return json.dumps({"status": "success", "message": "Movie updated successfully"})
        except sqlite3.Error as e:
            return json.dumps({"status": "error", "message": str(e)})
        
def start_server():
    # Start the cinema server and listen for incoming connections
    server = CinemaServer()
    while True:
        client_socket, addr = server.server_socket.accept()
        print("Accepted connection from ", addr)
        client_handler = Thread(target=server.handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    start_server()
