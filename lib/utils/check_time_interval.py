from datetime import datetime, time, timedelta

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
    return check_time_interval(*db.params.night_interval)


def next_datetime_from_time(target_time: time) -> datetime:
    now = datetime.now()
    candidate = datetime.combine(now.date(), target_time)

    # if that time has already passed today, shift to tomorrow
    if candidate <= now:
        candidate += timedelta(days=1)

    return candidate
