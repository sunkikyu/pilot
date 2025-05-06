# korean_holidays.py
from datetime import date
import holidays

kr_holidays = holidays.KR()

def is_korean_holiday(d: date) -> bool:
    return d in kr_holidays
