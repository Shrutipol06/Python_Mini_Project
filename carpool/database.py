"""SQLite storage and file logs (Units 2 and 4)."""

import os
import sqlite3
from datetime import datetime, timedelta

from .models import Booking, Ride, make_user

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "carpool.db")
LOG_PATH = os.path.join(DATA_DIR, "activity.log")
DT_FMT = "%Y-%m-%d %H:%M"


class DatabaseError(Exception):
    pass


def ride_datetime(travel_date, travel_time):
    return datetime.strptime(f"{travel_date} {travel_time}", DT_FMT)


def cancel_deadline(travel_date, travel_time):
    return ride_datetime(travel_date, travel_time) - timedelta(hours=24)


def ensure_can_cancel(travel_date, travel_time):
    if datetime.now() > cancel_deadline(travel_date, travel_time):
        raise DatabaseError("Cancellation allowed only before 24 hours of the ride.")


class CarPoolDB:
    def __init__(self, path=DB_PATH):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('driver', 'passenger'))
            );

            CREATE TABLE IF NOT EXISTS rides (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                driver_id INTEGER NOT NULL,
                origin TEXT NOT NULL,
                destination TEXT NOT NULL,
                travel_date TEXT NOT NULL,
                travel_time TEXT NOT NULL,
                seats INTEGER NOT NULL,
                fare REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'open',
                cancelled_at TEXT,
                FOREIGN KEY (driver_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ride_id INTEGER NOT NULL,
                passenger_id INTEGER NOT NULL,
                seats INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'confirmed',
                cancelled_at TEXT,
                FOREIGN KEY (ride_id) REFERENCES rides(id),
                FOREIGN KEY (passenger_id) REFERENCES users(id)
            );
            """
        )
        self.conn.commit()

    def log(self, message):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as handle:
            handle.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M')} | {message}\n")

    def register(self, name, phone, email, password, role):
        try:
            cur = self.conn.execute(
                "INSERT INTO users (name, phone, email, password, role) VALUES (?, ?, ?, ?, ?)",
                (name, phone, email, password, role),
            )
            self.conn.commit()
            self.log(f"New {role} registered: {name}")
            return cur.lastrowid
        except sqlite3.IntegrityError:
            raise DatabaseError("Phone or email already registered.")

    def login(self, phone, password, role):
        row = self.conn.execute(
            """
            SELECT id, name, phone, email, password, role
            FROM users WHERE phone = ? AND password = ? AND role = ?
            """,
            (phone, password, role),
        ).fetchone()
        if not row:
            raise DatabaseError("Invalid phone, password, or login type.")
        return make_user(tuple(row))

    def offer_ride(self, driver_id, origin, destination, travel_date, travel_time, seats, fare):
        when = ride_datetime(travel_date, travel_time)
        if when <= datetime.now():
            raise DatabaseError("Ride date and time must be in the future.")
        cur = self.conn.execute(
            """
            INSERT INTO rides (driver_id, origin, destination, travel_date, travel_time, seats, fare)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (driver_id, origin, destination, travel_date, travel_time, seats, fare),
        )
        self.conn.commit()
        self.log(f"Ride offered by user {driver_id}: {origin} -> {destination}")
        return cur.lastrowid

    def _ride_from_row(self, row):
        booked = row["booked"] if "booked" in row.keys() else 0
        driver_name = row["driver_name"] if "driver_name" in row.keys() else ""
        cancelled_at = row["cancelled_at"] if "cancelled_at" in row.keys() else None
        return Ride(
            row["id"],
            row["driver_id"],
            row["origin"],
            row["destination"],
            row["travel_date"],
            row["travel_time"],
            row["seats"],
            row["fare"],
            row["status"],
            booked or 0,
            driver_name or "",
            cancelled_at or "",
        )

    def _rides_query(self, where="", params=()):
        sql = f"""
            SELECT r.*, u.name AS driver_name,
                   COALESCE((
                       SELECT SUM(b.seats) FROM bookings b
                       WHERE b.ride_id = r.id AND b.status = 'confirmed'
                   ), 0) AS booked
            FROM rides r
            JOIN users u ON u.id = r.driver_id
            {where}
            ORDER BY r.travel_date, r.travel_time
        """
        rows = self.conn.execute(sql, params).fetchall()
        return [self._ride_from_row(row) for row in rows]

    def driver_rides(self, driver_id):
        return self._rides_query("WHERE r.driver_id = ?", (driver_id,))

    def search_rides(self, origin="", destination="", travel_date=""):
        clauses = ["r.status IN ('open', 'full')"]
        params = []
        if origin:
            clauses.append("LOWER(r.origin) LIKE ?")
            params.append(f"%{origin.lower()}%")
        if destination:
            clauses.append("LOWER(r.destination) LIKE ?")
            params.append(f"%{destination.lower()}%")
        if travel_date:
            clauses.append("r.travel_date = ?")
            params.append(travel_date)
        rides = self._rides_query("WHERE " + " AND ".join(clauses), tuple(params))
        return [ride for ride in rides if ride.available > 0 and ride.status == "open"]

    def all_open_rides(self):
        return self.search_rides()

    def get_ride(self, ride_id):
        rides = self._rides_query("WHERE r.id = ?", (ride_id,))
        if not rides:
            raise DatabaseError("Ride not found.")
        return rides[0]

    def book_ride(self, ride_id, passenger_id, seats):
        ride = self.get_ride(ride_id)
        if ride.driver_id == passenger_id:
            raise DatabaseError("You cannot book your own ride.")
        if ride.status != "open":
            raise DatabaseError("This ride is not open.")
        if ride_datetime(ride.travel_date, ride.travel_time) <= datetime.now():
            raise DatabaseError("This ride has already started.")
        if seats > ride.available:
            raise DatabaseError(f"Only {ride.available} seat(s) left.")
        existing = self.conn.execute(
            """
            SELECT id FROM bookings
            WHERE ride_id = ? AND passenger_id = ? AND status = 'confirmed'
            """,
            (ride_id, passenger_id),
        ).fetchone()
        if existing:
            raise DatabaseError("You already booked this ride.")
        cur = self.conn.execute(
            "INSERT INTO bookings (ride_id, passenger_id, seats) VALUES (?, ?, ?)",
            (ride_id, passenger_id, seats),
        )
        ride = self.get_ride(ride_id)
        if ride.available == 0:
            self.conn.execute("UPDATE rides SET status = 'full' WHERE id = ?", (ride_id,))
        self.conn.commit()
        self.log(f"Passenger {passenger_id} booked {seats} seat(s) on ride {ride_id}")
        return cur.lastrowid

    def passenger_bookings(self, passenger_id):
        rows = self.conn.execute(
            """
            SELECT b.id, b.ride_id, b.passenger_id, b.seats, b.status, b.cancelled_at
            FROM bookings b
            JOIN rides r ON r.id = b.ride_id
            WHERE b.passenger_id = ?
            ORDER BY r.travel_date, r.travel_time
            """,
            (passenger_id,),
        ).fetchall()
        bookings = []
        for row in rows:
            booking = Booking(
                row["id"],
                row["ride_id"],
                row["passenger_id"],
                row["seats"],
                row["status"],
                row["cancelled_at"] or "",
            )
            try:
                ride = self.get_ride(row["ride_id"])
            except DatabaseError:
                ride = None
            bookings.append((booking, ride))
        return bookings

    def driver_bookings(self, driver_id):
        rows = self.conn.execute(
            """
            SELECT b.id, b.seats, b.status, b.cancelled_at,
                   u.name, u.phone,
                   r.id AS ride_id, r.origin, r.destination,
                   r.travel_date, r.travel_time, r.status AS ride_status
            FROM bookings b
            JOIN rides r ON r.id = b.ride_id
            JOIN users u ON u.id = b.passenger_id
            WHERE r.driver_id = ?
            ORDER BY r.travel_date, r.travel_time
            """,
            (driver_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def cancel_booking(self, booking_id, passenger_id):
        row = self.conn.execute(
            "SELECT * FROM bookings WHERE id = ? AND passenger_id = ?",
            (booking_id, passenger_id),
        ).fetchone()
        if not row:
            raise DatabaseError("Booking not found.")
        if row["status"] != "confirmed":
            raise DatabaseError("Booking is already cancelled.")
        ride = self.get_ride(row["ride_id"])
        ensure_can_cancel(ride.travel_date, ride.travel_time)
        now = datetime.now().strftime(DT_FMT)
        self.conn.execute(
            "UPDATE bookings SET status = 'cancelled', cancelled_at = ? WHERE id = ?",
            (now, booking_id),
        )
        self.conn.execute(
            "UPDATE rides SET status = 'open' WHERE id = ? AND status = 'full'",
            (row["ride_id"],),
        )
        self.conn.commit()
        self.log(f"Booking {booking_id} cancelled by passenger {passenger_id}")

    def cancel_ride(self, ride_id, driver_id):
        ride = self.get_ride(ride_id)
        if ride.driver_id != driver_id:
            raise DatabaseError("You can cancel only your own rides.")
        if ride.status == "cancelled":
            raise DatabaseError("Ride is already cancelled.")
        ensure_can_cancel(ride.travel_date, ride.travel_time)
        now = datetime.now().strftime(DT_FMT)
        self.conn.execute(
            "UPDATE rides SET status = 'cancelled', cancelled_at = ? WHERE id = ?",
            (now, ride_id),
        )
        self.conn.execute(
            """
            UPDATE bookings
            SET status = 'cancelled', cancelled_at = ?
            WHERE ride_id = ? AND status = 'confirmed'
            """,
            (now, ride_id),
        )
        self.conn.commit()
        self.log(f"Ride {ride_id} cancelled by driver {driver_id}")

    def close(self):
        self.conn.close()
