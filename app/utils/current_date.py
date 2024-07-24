import datetime


def get_current_date() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d")
