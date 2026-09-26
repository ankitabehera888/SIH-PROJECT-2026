from datetime import date, timedelta
import pandas as pd

def build_dim_date(start_year: int = 2020, end_year: int = 2030) -> pd.DataFrame:
    """Generates a complete calendar date dimension table spanning start_year to end_year."""
    start_date = date(start_year, 1, 1)
    end_date = date(end_year, 12, 31)
    
    date_records = []
    curr = start_date
    one_day = timedelta(days=1)
    
    while curr <= end_date:
        date_key = curr.year * 10000 + curr.month * 100 + curr.day
        is_weekend = curr.weekday() in (5, 6)
        quarter = f"Q{(curr.month - 1) // 3 + 1}"
        
        date_records.append({
            "date_key": date_key,
            "full_date": curr,
            "day": curr.day,
            "day_of_week": curr.strftime("%A"),
            "day_of_week_num": curr.isoweekday(),
            "week": curr.isocalendar()[1],
            "month": curr.month,
            "month_name": curr.strftime("%B"),
            "quarter": quarter,
            "year": curr.year,
            "is_weekend": is_weekend,
        })
        curr += one_day
        
    return pd.DataFrame(date_records)
