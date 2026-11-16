"""
Working-time arithmetic for turnaround time.

A ticket assigned at 17:50 and completed at 09:10 next morning took 20 working
minutes, not 15 hours. The working day and week come from settings so each
installation can set its own.
"""
from datetime import timedelta

from django.conf import settings

# The app displays times at a fixed offset from UTC (see Ticket.get_created_at);
# the working day is defined on that same clock.
DISPLAY_OFFSET = timedelta(hours=5, minutes=30)


def working_seconds(start, end):
    """Seconds between two UTC datetimes that fall inside working hours."""
    if not start or not end or end <= start:
        return 0
    open_hour = getattr(settings, 'WORK_START_HOUR', 9)
    close_hour = getattr(settings, 'WORK_END_HOUR', 18)
    work_days = getattr(settings, 'WORK_DAYS', (0, 1, 2, 3, 4))   # Monday is 0

    start, end = start + DISPLAY_OFFSET, end + DISPLAY_OFFSET
    total = 0
    day = start.replace(hour=0, minute=0, second=0, microsecond=0)
    while day <= end:
        if day.weekday() in work_days:
            window_start = max(start, day + timedelta(hours=open_hour))
            window_end = min(end, day + timedelta(hours=close_hour))
            if window_end > window_start:
                total += (window_end - window_start).total_seconds()
        day += timedelta(days=1)
    return int(total)


def duration_text(seconds):
    """'10 min', '2 h 15 min', '3 h'. Under a minute reads as 'under 1 min'."""
    minutes = int(seconds // 60)
    if minutes < 1:
        return 'under 1 min'
    hours, minutes = divmod(minutes, 60)
    if not hours:
        return f'{minutes} min'
    return f'{hours} h {minutes} min' if minutes else f'{hours} h'
