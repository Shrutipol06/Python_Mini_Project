"""OOP models: inheritance, polymorphism, and simple overloading."""


class User:
    """Base user for both driver and passenger."""

    def __init__(self, user_id, name, phone, email, role):
        self.user_id = user_id
        self.name = name
        self.phone = phone
        self.email = email
        self.role = role

    def display(self):
        return f"{self.name} ({self.role})"

    def profile_lines(self):
        return [
            f"Name  : {self.name}",
            f"Phone : {self.phone}",
            f"Email : {self.email}",
            f"Role  : {self.role.title()}",
        ]


class Driver(User):
    def __init__(self, user_id, name, phone, email, vehicle="Car"):
        super().__init__(user_id, name, phone, email, "driver")
        self.vehicle = vehicle

    def display(self):
        return f"Driver {self.name} | {self.vehicle} | {self.phone}"


class Passenger(User):
    def __init__(self, user_id, name, phone, email):
        super().__init__(user_id, name, phone, email, "passenger")

    def display(self):
        return f"Passenger {self.name} | {self.phone}"


class Ride:
    def __init__(
        self,
        ride_id,
        driver_id,
        origin,
        destination,
        travel_date,
        travel_time,
        seats,
        fare,
        status="open",
        booked=0,
        driver_name="",
        cancelled_at="",
    ):
        self.ride_id = ride_id
        self.driver_id = driver_id
        self.origin = origin
        self.destination = destination
        self.travel_date = travel_date
        self.travel_time = travel_time
        self.seats = seats
        self.fare = fare
        self.status = status
        self.booked = booked
        self.driver_name = driver_name
        self.cancelled_at = cancelled_at

    @property
    def available(self):
        return max(self.seats - self.booked, 0)

    def route(self):
        return f"{self.origin} -> {self.destination}"

    def summary(self):
        return (
            f"#{self.ride_id}  {self.route()}  |  {self.travel_date} {self.travel_time}  |  "
            f"Rs {self.fare:.0f}  |  {self.available}/{self.seats} seats  |  {self.status}"
        )


class Booking:
    def __init__(self, booking_id, ride_id, passenger_id, seats, status="confirmed", cancelled_at=""):
        self.booking_id = booking_id
        self.ride_id = ride_id
        self.passenger_id = passenger_id
        self.seats = seats
        self.status = status
        self.cancelled_at = cancelled_at

    def summary(self, ride=None):
        extra = f"  {ride.route()}  {ride.travel_date}" if ride else ""
        return f"Booking #{self.booking_id}{extra}  |  {self.seats} seat(s)  |  {self.status}"


def make_user(row):
    """Polymorphic factory: same function, different subclass."""
    user_id, name, phone, email, _password, role = row
    if role == "driver":
        return Driver(user_id, name, phone, email)
    return Passenger(user_id, name, phone, email)
