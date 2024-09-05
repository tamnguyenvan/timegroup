import pytz
from datetime import datetime, timedelta

def get_timestamps_for_date(date="today"):
    timezone = pytz.timezone('Asia/Ho_Chi_Minh')
    now = datetime.now(timezone)

    if isinstance(date, str):
        date = date.lower().strip()
        if date == "today":
            delta_days = 0
        elif date == "yesterday":
            delta_days = 1
        elif date == "7 days ago":
            delta_days = 7
        elif date == "30 days ago":
            delta_days = 30
        else:
            raise ValueError("Invalid date string format.")
    elif isinstance(date, int):
        delta_days = abs(date)
    else:
        raise TypeError("The date should be either a string or an integer.")

    start_of_day = timezone.localize(datetime(now.year, now.month, now.day) - timedelta(days=delta_days))
    end_of_day = start_of_day + timedelta(days=1) - timedelta(seconds=1)

    start_timestamp = str(int(start_of_day.timestamp()))
    end_timestamp = str(int(end_of_day.timestamp()))

    return start_timestamp, end_timestamp

def isoformat_to_date_string(date):
    return datetime.fromisoformat(date).strftime("%d/%m/%Y")