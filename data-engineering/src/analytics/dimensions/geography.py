import pandas as pd

def build_dim_geography() -> pd.DataFrame:
    """Creates regional geography reference dimension for Odisha health facilities."""
    geos = [
        {"district": "Kendrapada", "state": "Odisha", "country": "India", "rural_urban": "rural"},
        {"district": "Cuttack", "state": "Odisha", "country": "India", "rural_urban": "urban"},
        {"district": "Khordha", "state": "Odisha", "country": "India", "rural_urban": "urban"},
        {"district": "Jagatsinghpur", "state": "Odisha", "country": "India", "rural_urban": "rural"},
        {"district": "Jajpur", "state": "Odisha", "country": "India", "rural_urban": "rural"},
        {"district": "Puri", "state": "Odisha", "country": "India", "rural_urban": "semi-urban"},
    ]
    return pd.DataFrame(geos)
