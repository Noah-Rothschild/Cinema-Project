import json
import socket
import tkinter as tk
from tkinter import ttk, messagebox

server_address = ('localhost', 12345)
class CinemaClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Cinema Ticket Booking System")
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.root, text="Movie Title:").grid(row=0, column=0, padx=10, pady=5)
        self.title_entry = ttk.Entry(self.root)
        self.title_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(self.root, text="Cinema Room:").grid(row=1, column=0, padx=10, pady=5)
        self.room_entry = ttk.Entry(self.root)
        self.room_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(self.root, text="Release Date:").grid(row=2, column=0, padx=10, pady=5)
        self.release_date_entry = ttk.Entry(self.root)
        self.release_date_entry.grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(self.root, text="End Date:").grid(row=3, column=0, padx=10, pady=5)
        self.end_date_entry = ttk.Entry(self.root)
        self.end_date_entry.grid(row=3, column=1, padx=10, pady=5)

        ttk.Label(self.root, text="Tickets Available:").grid(row=4, column=0, padx=10, pady=5)
        self.tickets_entry = ttk.Entry(self.root)
        self.tickets_entry.grid(row=4, column=1, padx=10, pady=5)

        ttk.Label(self.root, text="Ticket Price:").grid(row=5, column=0, padx=10, pady=5)
        self.price_entry = ttk.Entry(self.root)
        self.price_entry.grid(row=5, column=1, padx=10, pady=5)

        ttk.Button(self.root, text="Add Movie", command=self.add_movie).grid(row=6, columnspan=2)



    def add_movie(self):
        request = {
            'action': 'add_movie',
            'title': self.title_entry.get(),
            'cinema_room': int(self.room_entry.get()),
            'release_date': self.release_date_entry.get(),
            'end_date': self.end_date_entry.get(),
            'tickets_available': int(self.tickets_entry.get()),
            'ticket_price': float(self.price_entry.get())
        }

        response = send_request(request)
        if response.get("status") == "success":
            messagebox.showinfo("Success", "Movie added successfully!")
        else:
            messagebox.showerror("Error", response.get("message", "Unknown error"))

    def get_movies(self):
        request = {'action': 'get_movies'}
        response = send_request(request)
        if response.get("status") == "success":
            movies = response.get("movies", [])
            self.show_movies(movies)
        else:
            messagebox.showerror("Error", response.get("message", "Unknown error"))

    def book_ticket(self):
        request = {
            'action': 'book_ticket',
            'movie_id': int(self.movie_id_entry.get()),
            'customer_name': self.customer_name_entry.get(),
            'number_of_tickets': int(self.number_of_tickets_entry.get())
        }

        response = send_request(request)
        if response.get("status") == "success":
            messagebox.showinfo("Success", "Ticket booked successfully!")
        else:
            messagebox.showerror("Error", response.get("message", "Unknown error"))

    def remove_movie(self):
        request = {
            'action': 'remove_movie',
            'movie_id': int(self.movie_id_entry.get())
        }

        response = send_request(request)
        if response.get("status") == "success":
            messagebox.showinfo("Success", "Movie removed successfully!")
        else:
            messagebox.showerror("Error", response.get("message", "Unknown error"))

def send_request(request):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(server_address)
        sock.sendall(json.dumps(request).encode())
        response = sock.recv(4096).decode()
        return json.loads(response)
    
if __name__ == "__main__":
    root = tk.Tk()
    client = CinemaClient(root)
    root.mainloop()
    
