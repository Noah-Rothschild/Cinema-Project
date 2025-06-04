import json
import socket
import tkinter as tk
from tkinter import ttk, messagebox

server_address = ('localhost', 12345)
class CinemaClient:

    def __init__(self, root):
        self.root = root
        self.root.title("NewLine Cinema Ticket System")

        self.movies = []
        self.selected_movie_id = None

        self.dropdown = ttk.Combobox(root, state="readonly")
        self.dropdown.pack(pady=10)
        self.dropdown.bind("<<ComboboxSelected>>", self.on_movie_select)

        self.status_label = tk.Label(root, text="")
        self.status_label.pack()

        self.ticket_qty_entry = tk.Entry(root)
        self.ticket_qty_entry.pack(pady=5)
        self.customer_name_entry = tk.Entry(root)
        self.customer_name_entry.pack(pady=5)

        self.buy_btn = tk.Button(root, text="Buy Ticket", command=self.buy_ticket)
        self.buy_btn.pack(pady=5)
        self.add_btn = tk.Button(root, text="Add Movie", command=self.open_add_movie_window)
        self.add_btn.pack(pady=5)

        self.refresh_movies()

    def open_add_movie_window(self):
        popup = tk.Toplevel(self.root)
        popup.title("Add New Movie")

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

        def submit():
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
                messagebox.showerror("Input Error", "Please enter valid data.")

        tk.Button(popup, text="Submit", command=submit).pack(pady=10)

    def refresh_movies(self):
        response = send_request({"action": "get_movies"})
        if response["status"] == "success":
            self.movies = response["movies"]
            self.dropdown['values'] = [f"{m[0]} - {m[1]}" for m in self.movies]
        else:
            messagebox.showerror("Error", response["message"])

    def on_movie_select(self, event):
        selected = self.dropdown.get()
        if selected:
            movie_id = int(selected.split(" - ")[0])
            self.selected_movie_id = movie_id
            for movie in self.movies:
                if movie[0] == movie_id:
                    self.status_label.config(text=f"Movie Title: {movie[1]}\nTickets Available: {movie[5]}\nTicket Price: R{movie[6]}")
                    break

    def buy_ticket(self):
        if not self.selected_movie_id:
            messagebox.showwarning("Warning", "Please select a movie first.")
            return

        try:
            ticket_qty = int(self.ticket_qty_entry.get())
            customer_name = self.customer_name_entry.get().strip()
            if ticket_qty <= 0 or not customer_name:
                raise ValueError("Invalid input")

            request = {
                "action": "buy_ticket",
                "movie_id": self.selected_movie_id,
                "customer_name": customer_name,
                "number_of_tickets": ticket_qty
            }
            response = send_request(request)

            if response["status"] == "success":
                messagebox.showinfo("Success", response["message"])
                self.refresh_movies()
            else:
                messagebox.showerror("Error", response["message"])

        except ValueError as e:
            messagebox.showerror("Error", "invalid input. Please enter a valid number of tickets and customer name.")
    
    def remove_movie(self):
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

    def add_movie(self, title, cinema_room, release_date, end_date, tickets_available, ticket_price):
        request = {
            "action": "add_movie",
            "title": title,
            "cinema_room": cinema_room,
            "release_date": release_date,
            "end_date": end_date,
            "tickets_available": tickets_available,
            "ticket_price": ticket_price
        }
        response = send_request(request)

        if response["status"] == "success":
            messagebox.showinfo("Success", response["message"])
            self.refresh_movies()
        else:
            messagebox.showerror("Error", response["message"])

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
    
