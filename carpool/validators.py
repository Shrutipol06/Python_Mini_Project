"""Input checks using regular expressions (Unit 3)."""

import re


PHONE_PATTERN = re.compile(r"^[6-9]\d{9}$")
EMAIL_PATTERN = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$")
NAME_PATTERN = re.compile(r"^[A-Za-z ]{3,40}$")
PLACE_PATTERN = re.compile(r"^[A-Za-z0-9 ,\-]{2,40}$")
TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def check_name(value):
    if not NAME_PATTERN.match(value.strip()):
        raise ValueError("Name must be 3-40 letters only.")
    return value.strip().title()


def check_phone(value):
    value = value.strip()
    if not PHONE_PATTERN.match(value):
        raise ValueError("Phone must be 10 digits and start with 6-9.")
    return value


def check_email(value):
    value = value.strip().lower()
    if not EMAIL_PATTERN.match(value):
        raise ValueError("Enter a valid email address.")
    return value


def check_password(value):
    if len(value) < 4:
        raise ValueError("Password must be at least 4 characters.")
    return value


def check_place(value, field="Place"):
    value = value.strip().title()
    if not PLACE_PATTERN.match(value):
        raise ValueError(f"{field} must be 2-40 letters or numbers.")
    return value


def check_date(value):
    value = value.strip()
    if not DATE_PATTERN.match(value):
        raise ValueError("Date must be YYYY-MM-DD.")
    return value


def check_time(value):
    value = value.strip()
    if not TIME_PATTERN.match(value):
        raise ValueError("Time must be HH:MM in 24-hour format.")
    return value


def check_seats(value, maximum=8):
    try:
        seats = int(value)
    except (TypeError, ValueError):
        raise ValueError("Seats must be a number.")
    if seats < 1 or seats > maximum:
        raise ValueError(f"Seats must be between 1 and {maximum}.")
    return seats


def check_fare(value):
    try:
        fare = float(value)
    except (TypeError, ValueError):
        raise ValueError("Fare must be a number.")
    if fare < 0:
        raise ValueError("Fare cannot be negative.")
    return round(fare, 2)
