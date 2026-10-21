# ShareRide

ShareRide is a desktop carpooling application built with Python and Tkinter. Drivers can post rides and manage bookings, while passengers can search for rides and book available seats.

## Features

- Register and log in as a driver or passenger
- Post rides with a route, date, time, available seats, and fare per seat
- Search open rides by route and date
- Book seats and view booking history
- View offered rides and passenger bookings
- Cancel rides or bookings, subject to the app's 24-hour cancellation rule
- Store application data in a local SQLite database and record activity in a log

## Requirements

- Python 3
- Tkinter, which is included with most standard Python installations

The application uses only Python's standard library; no additional packages are required.

## Run

Open a terminal in the project folder and run:

```powershell
py main.py
```

If the `py` launcher is unavailable, use:

```powershell
python main.py
```

## Project structure

```text
main.py             Application entry point
carpool/
  database.py       SQLite persistence and application operations
  gui.py            Tkinter user interface
  models.py         User, ride, and booking models
  validators.py     Input validation
data/
  carpool.db        Local SQLite database
  activity.log      Activity log
```

The database and log are stored in `data/`. Keep `data/carpool.db` to retain locally stored accounts, rides, and bookings.
