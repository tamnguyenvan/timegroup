import pytz
from datetime import datetime, timedelta

timezone = pytz.timezone('Asia/Ho_Chi_Minh')

def get_time_frame(date_term):
    now = datetime.now(timezone)

    if date_term == "today":
        start_date = timezone.localize(datetime(now.year, now.month, now.day))
        end_date = start_date + timedelta(days=1) - timedelta(seconds=1)

    elif date_term == "yesterday":
        start_date = timezone.localize(datetime(now.year, now.month, now.day) - timedelta(days=1))
        end_date = start_date + timedelta(days=1) - timedelta(seconds=1)

    elif date_term == "last_month":
        # Handle cases where we need to roll back to the previous year (if we're in January)
        if now.month == 1:
            start_date = timezone.localize(datetime(now.year - 1, 12, 1))
        else:
            start_date = timezone.localize(datetime(now.year, now.month - 1, 1))

        # Calculate the end date for last month
        next_month = start_date.month % 12 + 1
        year_of_next_month = start_date.year if next_month > 1 else start_date.year + 1
        end_date = timezone.localize(datetime(year_of_next_month, next_month, 1)) - timedelta(seconds=1)

    elif date_term == "last_month_and_current_month":
        # Start from the first day of the last month
        if now.month == 1:
            start_date = timezone.localize(datetime(now.year - 1, 12, 1))
        else:
            start_date = timezone.localize(datetime(now.year, now.month - 1, 1))

        # End at the current end of the day
        end_date = timezone.localize(datetime(now.year, now.month, now.day)) + timedelta(days=1) - timedelta(seconds=1)

    else:
        raise ValueError("Invalid date_term provided.")

    start_timestamp = str(int(start_date.timestamp()))
    end_timestamp = str(int(end_date.timestamp()))

    return start_timestamp, end_timestamp

def isoformat_to_date_string(date):
    return datetime.fromisoformat(date).strftime("%d/%m/%Y")