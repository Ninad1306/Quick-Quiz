from app.constants import *
import datetime

def get_current_semester_and_year():
    now = datetime.datetime.now()
    year = now.year

    if 1 <= now.month <= 6:
        semester = f"Spring_{year}"
    else:
        semester = f"Fall_{year}"
    
    return semester, str(year)