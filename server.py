import socket
import sqlite3
import json
from threading import Thread

db = 'cinema.db'

class CinemaServer:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.conn = sqlite3.connect(db)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server started on {self.host}:{self.port}")

    def create_tables(self):
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
                movie_id INTEGER FOREIGN KEY REFERENCES Movies(movie_id),
                customer_name TEXT,
                number_of_tickets INTEGER CHECK (number_of_tickets > 0),
                total_price REAL
            ) 
        """)
        self.conn.commit()

    def handle_client(self, client_socket):
        while True:
            try:
                request = client_socket.recv(1024).decode('utf-8')
                if not request:
                    break
                print("Received request: {request}")
                response = self.process_request(request)
                client_socket.sendall(response.encode('utf-8'))
            except Exception as e:
                print("Error: {e}")
                break
        client_socket.close()