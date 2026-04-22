from datetime import datetime


def utc_now():
    return datetime.utcnow()


def format_datetime(dt, fmt='%Y-%m-%d %H:%M:%S'):
    if dt is None:
        return None
    return dt.strftime(fmt)


def parse_datetime(value, fmt='%Y-%m-%d %H:%M:%S'):
    if not value:
        return None
    return datetime.strptime(value, fmt)