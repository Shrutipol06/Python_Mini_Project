"""Simple tkinter interface for ShareRide (Unit 4)."""

import tkinter as tk
from tkinter import messagebox, ttk

from . import APP_NAME
from .database import CarPoolDB, DatabaseError, cancel_deadline
from .validators import (
    check_date,
    check_email,
    check_fare,
    check_name,
    check_password,
    check_phone,
    check_place,
    check_seats,
    check_time,
)

BG = "#f4f7fb"
CARD = "#ffffff"
NAVY = "#1f4e79"
TEAL = "#1a7f6a"
AMBER = "#c47b17"
RED = "#b42318"
TEXT = "#1d2433"
MUTED = "#5b6573"


class ShareRideApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("980x640")
        self.minsize(900, 580)
        self.configure(bg=BG)
        self.db = CarPoolDB()
        self.user = None
        self.container = tk.Frame(self, bg=BG)
        self.container.pack(fill="both", expand=True)
        self.show_home()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def clear(self):
        for child in self.container.winfo_children():
            child.destroy()

    def button(self, parent, text, command, color=NAVY, width=28):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            width=width,
            cursor="hand2",
            activebackground=color,
            activeforeground="white",
            pady=6,
        )
        btn.pack(pady=8)
        return btn

    def labeled_entry(self, parent, label, show=None):
        box = tk.Frame(parent, bg=CARD)
        box.pack(fill="x", pady=6, padx=40)
        tk.Label(box, text=label, font=("Segoe UI", 10), fg=TEXT, bg=CARD, anchor="w").pack(fill="x")
        entry = tk.Entry(box, font=("Segoe UI", 11), show=show or "", relief="solid", bd=1)
        entry.pack(fill="x", ipady=4)
        return entry

    def show_home(self):
        self.user = None
        self.clear()
        wrap = tk.Frame(self.container, bg=BG)
        wrap.pack(fill="both", expand=True, padx=28, pady=24)

        hero = tk.Frame(wrap, bg=NAVY)
        hero.pack(side="left", fill="both", expand=True, padx=(0, 16))
        tk.Label(hero, text=APP_NAME, font=("Segoe UI", 32, "bold"), fg="white", bg=NAVY).pack(
            pady=(70, 8), padx=32, anchor="w"
        )
        tk.Label(
            hero,
            text="Share rides. Save time.\nLog in with your email to offer\nor book a seat.",
            font=("Segoe UI", 13),
            fg="#d7e4f5",
            bg=NAVY,
            justify="left",
        ).pack(padx=32, anchor="w")
        tk.Label(
            hero,
            text="Use the email and password you registered with.",
            font=("Segoe UI", 10),
            fg="#9db4ce",
            bg=NAVY,
            justify="left",
        ).pack(padx=32, pady=(18, 0), anchor="w")

        card = tk.Frame(wrap, bg=CARD, highlightbackground="#d5deea", highlightthickness=1)
        card.pack(side="right", fill="both", expand=True)
        tk.Label(card, text="Welcome back", font=("Segoe UI", 20, "bold"), fg=NAVY, bg=CARD).pack(
            pady=(22, 4)
        )
        tk.Label(card, text="Sign in with email and password", font=("Segoe UI", 10), fg=MUTED, bg=CARD).pack()

        notebook = ttk.Notebook(card)
        notebook.pack(fill="both", expand=True, padx=18, pady=(14, 18))

        offer_tab = tk.Frame(notebook, bg=CARD)
        book_tab = tk.Frame(notebook, bg=CARD)
        register_tab = tk.Frame(notebook, bg=CARD)
        notebook.add(offer_tab, text="Offer Ride")
        notebook.add(book_tab, text="Book Ride")
        notebook.add(register_tab, text="Register")

        self._login_form(offer_tab, "driver")
        self._login_form(book_tab, "passenger")
        self._register_form(register_tab)

    def _login_form(self, parent, role):
        heading = "Driver login" if role == "driver" else "Passenger login"
        tk.Label(parent, text=heading, font=("Segoe UI", 12, "bold"), fg=TEXT, bg=CARD).pack(pady=(16, 4))
        email = self.labeled_entry(parent, "Email")
        password = self.labeled_entry(parent, "Password", show="*")
        color = TEAL if role == "driver" else NAVY

        def do_login():
            try:
                self.user = self.db.login(check_email(email.get()), password.get(), role)
                if role == "driver":
                    self.show_driver()
                else:
                    self.show_passenger()
            except (ValueError, DatabaseError) as err:
                messagebox.showerror("Login failed", str(err))

        self.button(parent, "Login", do_login, color)

    def _register_form(self, parent):
        name = self.labeled_entry(parent, "Full name")
        phone = self.labeled_entry(parent, "Phone (10 digits)")
        email = self.labeled_entry(parent, "Email")
        password = self.labeled_entry(parent, "Password", show="*")
        role_var = tk.StringVar(value="passenger")
        role_row = tk.Frame(parent, bg=CARD)
        role_row.pack(pady=8)
        tk.Radiobutton(role_row, text="Offer Ride", variable=role_var, value="driver", bg=CARD).pack(
            side="left", padx=8
        )
        tk.Radiobutton(role_row, text="Book Ride", variable=role_var, value="passenger", bg=CARD).pack(
            side="left", padx=8
        )

        def save():
            try:
                self.db.register(
                    check_name(name.get()),
                    check_phone(phone.get()),
                    check_email(email.get()),
                    check_password(password.get()),
                    role_var.get(),
                )
                messagebox.showinfo("Registered", "Account created. Please login.")
                name.delete(0, "end")
                phone.delete(0, "end")
                email.delete(0, "end")
                password.delete(0, "end")
            except (ValueError, DatabaseError) as err:
                messagebox.showerror("Cannot register", str(err))

        self.button(parent, "Register", save, AMBER)

    def header(self, parent, title):
        bar = tk.Frame(parent, bg=NAVY)
        bar.pack(fill="x")
        tk.Label(bar, text=title, font=("Segoe UI", 14, "bold"), fg="white", bg=NAVY).pack(
            side="left", padx=16, pady=10
        )
        tk.Button(
            bar,
            text="Logout",
            command=self.show_home,
            bg="#14375a",
            fg="white",
            relief="flat",
            cursor="hand2",
        ).pack(side="right", padx=12, pady=8)

    def sidebar(self, parent, items):
        side = tk.Frame(parent, bg="#e8eef6", width=200)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)
        tk.Label(
            side,
            text=self.user.name,
            wraplength=180,
            font=("Segoe UI", 10, "bold"),
            bg="#e8eef6",
            fg=NAVY,
        ).pack(padx=10, pady=16)
        for text, command in items:
            tk.Button(
                side,
                text=text,
                command=command,
                bg="#e8eef6",
                fg=TEXT,
                relief="flat",
                anchor="w",
                font=("Segoe UI", 10),
                cursor="hand2",
            ).pack(fill="x", padx=8, pady=2)

    def work_area(self, parent):
        area = tk.Frame(parent, bg=BG)
        area.pack(side="left", fill="both", expand=True, padx=16, pady=16)
        return area

    def show_driver(self):
        self.clear()
        self.header(self.container, f"{APP_NAME}  |  {self.user.name}")
        content = tk.Frame(self.container, bg=BG)
        content.pack(fill="both", expand=True)
        self.sidebar(
            content,
            [
                ("Offer Ride", self.driver_offer),
                ("Offered Rides", self.driver_rides),
                ("Bookings", self.driver_bookings),
            ],
        )
        self.area = self.work_area(content)
        self.driver_offer()

    def show_passenger(self):
        self.clear()
        self.header(self.container, f"{APP_NAME}  |  {self.user.name}")
        content = tk.Frame(self.container, bg=BG)
        content.pack(fill="both", expand=True)
        self.sidebar(
            content,
            [
                ("View Rides", self.passenger_search),
                ("Booking History", self.passenger_bookings),
            ],
        )
        self.area = self.work_area(content)
        self.passenger_search()

    def reset_area(self, title):
        for child in self.area.winfo_children():
            child.destroy()
        tk.Label(self.area, text=title, font=("Segoe UI", 16, "bold"), fg=NAVY, bg=BG).pack(anchor="w")

    def driver_offer(self):
        self.reset_area("Offer Ride")
        form = tk.Frame(self.area, bg=BG)
        form.pack(anchor="nw", pady=12)
        origin = self._field(form, "From city")
        dest = self._field(form, "To city")
        travel_date = self._field(form, "Date (YYYY-MM-DD)")
        travel_time = self._field(form, "Time (HH:MM)")
        seats = self._field(form, "Seats (1-8)")
        fare = self._field(form, "Fare per seat (Rs)")

        def save():
            try:
                self.db.offer_ride(
                    self.user.user_id,
                    check_place(origin.get(), "From city"),
                    check_place(dest.get(), "To city"),
                    check_date(travel_date.get()),
                    check_time(travel_time.get()),
                    check_seats(seats.get()),
                    check_fare(fare.get()),
                )
                messagebox.showinfo("Ride posted", "Ride offered.")
                self.driver_rides()
            except (ValueError, DatabaseError) as err:
                messagebox.showerror("Cannot post ride", str(err))

        tk.Button(form, text="Post Ride", command=save, bg=TEAL, fg="white", relief="flat", padx=16, pady=6).grid(
            row=6, column=1, sticky="w", pady=12
        )

    def _field(self, parent, label):
        if not hasattr(parent, "_row"):
            parent._row = 0
        r = parent._row
        parent._row += 1
        tk.Label(parent, text=label, bg=BG, fg=TEXT, font=("Segoe UI", 10)).grid(row=r, column=0, sticky="w", pady=5)
        entry = tk.Entry(parent, font=("Segoe UI", 11), width=28, relief="solid", bd=1)
        entry.grid(row=r, column=1, padx=10, pady=5, ipady=3)
        return entry

    def _tree(self, parent, columns, headings, height=12):
        style = ttk.Style()
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=26)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=height)
        for col, head, width in headings:
            tree.heading(col, text=head)
            tree.column(col, width=width, anchor="center")
        scroll = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True, pady=10)
        scroll.pack(side="right", fill="y", pady=10)
        return tree

    def driver_rides(self):
        self.reset_area("Offered Rides")
        box = tk.Frame(self.area, bg=BG)
        box.pack(fill="both", expand=True)
        tree = self._tree(
            box,
            ("id", "route", "when", "seats", "fare", "status", "cancel_by"),
            [
                ("id", "ID", 50),
                ("route", "Route", 170),
                ("when", "Date / Time", 130),
                ("seats", "Seats", 80),
                ("fare", "Fare", 70),
                ("status", "Status", 90),
                ("cancel_by", "Cancel before", 130),
            ],
        )
        for ride in self.db.driver_rides(self.user.user_id):
            deadline = cancel_deadline(ride.travel_date, ride.travel_time).strftime("%Y-%m-%d %H:%M")
            tree.insert(
                "",
                "end",
                values=(
                    ride.ride_id,
                    ride.route(),
                    f"{ride.travel_date} {ride.travel_time}",
                    f"{ride.available}/{ride.seats}",
                    f"Rs {ride.fare:.0f}",
                    ride.status,
                    ride.cancelled_at or deadline,
                ),
            )

        def cancel():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select a ride", "Click a ride first.")
                return
            ride_id = int(tree.item(selected[0], "values")[0])
            if not messagebox.askyesno("Cancel ride", "Cancel this ride and its bookings?"):
                return
            try:
                self.db.cancel_ride(ride_id, self.user.user_id)
                messagebox.showinfo("Cancelled", "Ride cancelled.")
                self.driver_rides()
            except DatabaseError as err:
                messagebox.showerror("Cannot cancel", str(err))

        tk.Button(self.area, text="Cancel Selected Ride", command=cancel, bg=RED, fg="white", relief="flat").pack(
            anchor="w"
        )

    def driver_bookings(self):
        self.reset_area("Bookings")
        box = tk.Frame(self.area, bg=BG)
        box.pack(fill="both", expand=True)
        tree = self._tree(
            box,
            ("when", "route", "name", "phone", "seats", "status", "cancelled"),
            [
                ("when", "Date / Time", 130),
                ("route", "Route", 160),
                ("name", "Passenger", 120),
                ("phone", "Phone", 110),
                ("seats", "Seats", 60),
                ("status", "Status", 90),
                ("cancelled", "Cancelled at", 130),
            ],
        )
        for booking in self.db.driver_bookings(self.user.user_id):
            tree.insert(
                "",
                "end",
                values=(
                    f"{booking['travel_date']} {booking['travel_time']}",
                    f"{booking['origin']} -> {booking['destination']}",
                    booking["name"],
                    booking["phone"],
                    booking["seats"],
                    booking["status"],
                    booking["cancelled_at"] or "-",
                ),
            )

    def passenger_search(self):
        self.reset_area("View Rides")
        filters = tk.Frame(self.area, bg=BG)
        filters.pack(anchor="w", pady=8)
        tk.Label(filters, text="From", bg=BG).grid(row=0, column=0)
        origin = tk.Entry(filters, width=16)
        origin.grid(row=0, column=1, padx=6)
        tk.Label(filters, text="To", bg=BG).grid(row=0, column=2)
        dest = tk.Entry(filters, width=16)
        dest.grid(row=0, column=3, padx=6)
        tk.Label(filters, text="Date YYYY-MM-DD", bg=BG).grid(row=0, column=4)
        travel_date = tk.Entry(filters, width=14)
        travel_date.grid(row=0, column=5, padx=6)
        tk.Label(filters, text="Seats", bg=BG).grid(row=0, column=6)
        seats_box = tk.Entry(filters, width=6)
        seats_box.insert(0, "1")
        seats_box.grid(row=0, column=7, padx=6)

        box = tk.Frame(self.area, bg=BG)
        box.pack(fill="both", expand=True)
        tree = self._tree(
            box,
            ("id", "driver", "route", "when", "seats", "fare"),
            [
                ("id", "ID", 50),
                ("driver", "Driver", 130),
                ("route", "Route", 180),
                ("when", "Date / Time", 140),
                ("seats", "Left", 70),
                ("fare", "Fare", 80),
            ],
        )

        def fill(rides):
            tree.delete(*tree.get_children())
            for ride in rides:
                tree.insert(
                    "",
                    "end",
                    values=(
                        ride.ride_id,
                        ride.driver_name,
                        ride.route(),
                        f"{ride.travel_date} {ride.travel_time}",
                        ride.available,
                        f"Rs {ride.fare:.0f}",
                    ),
                )

        def search():
            date_value = travel_date.get().strip()
            try:
                if date_value:
                    date_value = check_date(date_value)
                fill(self.db.search_rides(origin.get().strip(), dest.get().strip(), date_value))
            except ValueError as err:
                messagebox.showerror("Invalid filter", str(err))

        def book():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select a ride", "Click a ride first.")
                return
            try:
                seats = check_seats(seats_box.get())
                ride_id = int(tree.item(selected[0], "values")[0])
                self.db.book_ride(ride_id, self.user.user_id, seats)
                messagebox.showinfo("Booked", "Ride booked.")
                search()
            except (ValueError, DatabaseError) as err:
                messagebox.showerror("Cannot book", str(err))

        tk.Button(filters, text="Search", command=search, bg=NAVY, fg="white", relief="flat").grid(
            row=0, column=8, padx=6
        )
        tk.Button(self.area, text="Book Selected Ride", command=book, bg=TEAL, fg="white", relief="flat").pack(
            anchor="w"
        )
        fill(self.db.all_open_rides())

    def passenger_bookings(self):
        self.reset_area("Booking History")
        box = tk.Frame(self.area, bg=BG)
        box.pack(fill="both", expand=True)
        tree = self._tree(
            box,
            ("id", "route", "when", "seats", "fare", "status", "cancelled"),
            [
                ("id", "ID", 50),
                ("route", "Route", 170),
                ("when", "Date / Time", 130),
                ("seats", "Seats", 70),
                ("fare", "Total", 80),
                ("status", "Status", 90),
                ("cancelled", "Cancelled at", 130),
            ],
        )
        for booking, ride in self.db.passenger_bookings(self.user.user_id):
            route = ride.route() if ride else "-"
            when = f"{ride.travel_date} {ride.travel_time}" if ride else "-"
            total = f"Rs {ride.fare * booking.seats:.0f}" if ride else "-"
            tree.insert(
                "",
                "end",
                values=(
                    booking.booking_id,
                    route,
                    when,
                    booking.seats,
                    total,
                    booking.status,
                    booking.cancelled_at or "-",
                ),
            )

        def cancel():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select a booking", "Click a booking first.")
                return
            booking_id = int(tree.item(selected[0], "values")[0])
            if not messagebox.askyesno("Cancel booking", "Cancel this booking?"):
                return
            try:
                self.db.cancel_booking(booking_id, self.user.user_id)
                messagebox.showinfo("Cancelled", "Booking cancelled.")
                self.passenger_bookings()
            except DatabaseError as err:
                messagebox.showerror("Cannot cancel", str(err))

        tk.Button(self.area, text="Cancel Selected Booking", command=cancel, bg=RED, fg="white", relief="flat").pack(
            anchor="w"
        )

    def on_close(self):
        self.db.close()
        self.destroy()
