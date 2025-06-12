import json
import socket
import tkinter as tk
from tkinter import ttk, messagebox
import os

# Define the project directory and server address
project_dir = os.path.dirname(__file__)
server_address = ('localhost', 12345)

class CinemaClient:

    def __init__(self, root):
        # Initialize the main window and its components in tkinter
        self.root = root
        self.root.title("NewLine Cinema Ticket System")

        self.movies = []
        self.selected_movie_id = None

        tk.Label(root, text="Select a Movie:").pack(pady=1)

        self.dropdown = ttk.Combobox(root, state="readonly")
        self.dropdown.pack(pady=10)
        self.dropdown.bind("<<ComboboxSelected>>", self.on_movie_select)

        self.status_label = tk.Label(root, text="")
        self.status_label.pack()

        tk.Label(root, text="Customer Name:").pack(pady=5)
        self.customer_name_entry = tk.Entry(root)
        self.customer_name_entry.pack(pady=5)

        tk.Label(root, text="Number of Tickets:").pack(pady=5)
        self.ticket_qty_entry = tk.Entry(root)
        self.ticket_qty_entry.pack(pady=5)

        self.buy_btn = tk.Button(root, text="Buy Ticket", command=self.buy_ticket)
        self.buy_btn.pack(pady=3)
        self.add_btn = tk.Button(root, text="Add Movie", command=self.open_add_movie_window)
        self.add_btn.pack(pady=3)
        self.update_btn = tk.Button(root, text="Update Movie", command=self.open_update_movie_window)
        self.update_btn.pack(pady=3)
        self.remove_btn = tk.Button(root, text="Remove Movie", command=self.remove_movie)
        self.remove_btn.pack(pady=3)

        self.refresh_movies()

    def open_add_movie_window(self):
        # add a new movie pop up window to enter movie details

        popup = tk.Toplevel(self.root)
        popup.title("Add New Movie")

        tk.Label(popup, text="Title").pack()
        title_entry = tk.Entry(popup)
        title_entry.pack()

        tk.Label(popup, text="Cinema Room (1-7)").pack()
        room_entry = tk.Entry(popup)
        room_entry.pack()

        tk.Label(popup, text="Release Date").pack()
        release_entry = tk.Entry(popup)
        release_entry.pack()

        tk.Label(popup, text="End Date").pack()
        end_entry = tk.Entry(popup)
        end_entry.pack()

        tk.Label(popup, text="Tickets Available").pack()
        tickets_entry = tk.Entry(popup)
        tickets_entry.pack()

        tk.Label(popup, text="Ticket Price").pack()
        price_entry = tk.Entry(popup)
        price_entry.pack()

        def add_movie():
            # Validate and send the movie data to the server
            try:
                data = {
                    "title": title_entry.get(),
                    "cinema_room": int(room_entry.get()),
                    "release_date": release_entry.get(),
                    "end_date": end_entry.get(),
                    "tickets_available": int(tickets_entry.get()),
                    "ticket_price": float(price_entry.get())
                }
                response = send_request({"action": "add_movie", "movie": data})
                if response["status"] == "success":
                    messagebox.showinfo("Success", "Movie added.")
                    self.refresh_movies()
                    popup.destroy()
                else:
                    messagebox.showerror("Error", response["message"])
            except ValueError:
                messagebox.showerror("Input Error", "Data entered incorrectly.")

        tk.Button(popup, text="Submit", command=add_movie).pack(pady=10)
        self.refresh_movies

    def open_update_movie_window(self):
        # Open a window to update movie details
        if not self.selected_movie_id:
            messagebox.showwarning("Warning", "Please select a movie first.")
            return

        popup = tk.Toplevel(self.root)
        popup.title("Update Movie")

        tk.Label(popup, text="Title").pack()
        title_entry = tk.Entry(popup)
        title_entry.pack()

        tk.Label(popup, text="Cinema Room (1-7)").pack()
        room_entry = tk.Entry(popup)
        room_entry.pack()

        tk.Label(popup, text="Release Date (YYYY-MM-DD)").pack()
        release_entry = tk.Entry(popup)
        release_entry.pack()

        tk.Label(popup, text="End Date (YYYY-MM-DD)").pack()
        end_entry = tk.Entry(popup)
        end_entry.pack()

        tk.Label(popup, text="Tickets Available").pack()
        tickets_entry = tk.Entry(popup)
        tickets_entry.pack()

        tk.Label(popup, text="Ticket Price").pack()
        price_entry = tk.Entry(popup)
        price_entry.pack()

        def update_movie():
            # Validate and send the updated movie data to the server
            try:
                data = {
                    "movie_id": self.selected_movie_id,
                    "title": title_entry.get(),
                    "cinema_room": int(room_entry.get()),
                    "release_date": release_entry.get(),
                    "end_date": end_entry.get(),
                    "tickets_available": int(tickets_entry.get()),
                    "ticket_price": float(price_entry.get())
                }
                response = send_request({"action": "update_movie", "movie": data})
                if response["status"] == "success":
                    messagebox.showinfo("Success", "Movie updated.")
                    self.refresh_movies()
                    popup.destroy()
                else:
                    messagebox.showerror("Error", response["message"])
            except ValueError:
                messagebox.showerror("Input Error", "Data entered incorrectly.")

        tk.Button(popup, text="Submit", command=update_movie).pack(pady=10)

    def refresh_movies(self):
        # Fetch the list of movies from the server and update the dropdown
        response = send_request({"action": "get_movies"})
        if response["status"] == "success":
            self.movies = response["movies"]
            self.dropdown['values'] = [f"{m[0]} - {m[1]}" for m in self.movies]
        else:
            messagebox.showerror("Error", response["message"])

    def on_movie_select(self, event):
        # Update the selected movie information when a movie is selected from the dropdown
        selected = self.dropdown.get()
        if selected:
            movie_id = int(selected.split(" - ")[0])
            self.selected_movie_id = movie_id
            for movie in self.movies:
                if movie[0] == movie_id:
                    self.selected_movie = movie
                    self.status_label.config(
                        text=f"Movie Title: {movie[1]}\n"
                             f"Cinema Room: {movie[2]}\n"
                             f"Release Date: {movie[3]}\n"
                             f"End Date: {movie[4]}\n"
                             f"Tickets Available: {movie[5]}\n"
                             f"Ticket Price: R{movie[6]}")
                    break

    def buy_ticket(self):
        # Handle the ticket booking process
        if not self.selected_movie_id:
            # If no movie is selected, show a warning
            messagebox.showwarning("Warning", "Please select a movie first.")
            return

        try:
            # gather ticket quantity and customer name from the input fields and selected movie
            ticket_qty = int(self.ticket_qty_entry.get())
            customer_name = self.customer_name_entry.get().strip()
            ticket_price = self.selected_movie[6]
            total_price = ticket_qty * ticket_price
            movie_id = self.selected_movie_id

            if ticket_qty <= 0 or not customer_name:
                raise ValueError("Invalid input")

            request = {
                "action": "book_ticket",
                "movie_id": self.selected_movie_id,
                "customer_name": customer_name,
                "number_of_tickets": ticket_qty,
                "ticket_price": ticket_price
            }
            response = send_request(request)
            self.refresh_movies()

            if response["status"] == "success":
                messagebox.showinfo("Success", response["message"])
                # Create a receipt file
                receipt = f"Receipt:\nMovie id: {movie_id}\nCustomer: {customer_name}\nTickets: {ticket_qty}\nTotal Price: R{total_price}"
                filename = os.path.join(project_dir, f"receipts/receipt_{customer_name}_{movie_id}.txt")

                with open(filename, "w") as file:
                    file.write(receipt)
            else:
                messagebox.showerror("Error", response["message"])

        except ValueError as e:
            messagebox.showerror("Error", "invalid input. Please enter a valid number of tickets and customer name.")
    
    def remove_movie(self):
        # Handle the movie removal process
        if not self.selected_movie_id:
            messagebox.showwarning("Warning", "Please select a movie first.")
            return

        request = {
            "action": "remove_movie",
            "movie_id": self.selected_movie_id
        }
        response = send_request(request)

        if response["status"] == "success":
            messagebox.showinfo("Success", response["message"])
            self.refresh_movies()
        else:
            messagebox.showerror("Error", response["message"])

def send_request(request):
    # Send a request to the server and return the response
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(server_address)
        sock.sendall(json.dumps(request).encode())
        response = sock.recv(4096).decode()
        return json.loads(response)
    
if __name__ == "__main__":
    # Create the main application window and start the client
    root = tk.Tk()
    client = CinemaClient(root)
    root.mainloop()
    
