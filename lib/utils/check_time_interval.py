from datetime import datetime, time

from lib.database import Database


def check_time_interval(start_time, end_time):
    now = datetime.now().time()  # 08:00

    # Handle overnight interval (23:00-08:00)
    if start_time > end_time:
        return now >= start_time or now <= end_time
    # For normal daytime intervals (when start < end)
    else:
        return start_time <= now <= end_time


def is_night(db: Database):
    return check_time_interval(*db.night_interval)
