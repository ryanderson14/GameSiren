import time
import datetime

def seconds_until(target_time):
    """Return the number of seconds from now until the target_time. If the target time has already passed, return 0"""
    now = datetime.datetime.now().astimezone()
    delta = target_time - now
    return max(delta.total_seconds(), 0)


def sleep_until(target_time):
    """Sleep until the target_time is reached."""
    seconds = seconds_until(target_time)
    if seconds > 0:
        time.sleep(seconds)


def sleep_until_6am():
    current_dt = datetime.datetime.now().astimezone()
    # Determine next 6am. If current time is before 6am, use today; otherwise, tomorrow.
    if current_dt.hour < 6:
        next_6am = current_dt.replace(hour=6, minute=0, second=0, microsecond=0)
    else:
        next_6am = (current_dt + datetime.timedelta(days=1)).replace(hour=6, minute=0, second=0, microsecond=0)

    sleep_time = (next_6am - current_dt).total_seconds()
    print(f"Sleeping until 6am (in {sleep_time:.0f} seconds).")
    time.sleep(sleep_time)