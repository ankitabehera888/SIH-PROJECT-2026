import pandas as pd

def build_dim_facility(df_staged_facilities: pd.DataFrame) -> pd.DataFrame:
    """Extracts operational healthcare facilities into dim_facility."""
    df = pd.DataFrame()
    
    if df_staged_facilities.empty:
        return pd.DataFrame()
        
    df["facility_id"] = df_staged_facilities["id"].astype(str)
    df["facility_name"] = df_staged_facilities["name"].astype(str)
    df["facility_code"] = df_staged_facilities["facility_code"].astype(str)
    
    tier_col = df_staged_facilities.get("facility_type", df_staged_facilities.get("tier", "PHC"))
    df["facility_tier"] = tier_col.fillna("PHC").astype(str).str.upper()
    df["is_active"] = df_staged_facilities.get("is_active", True).fillna(True).astype(bool)
    
    return df.drop_duplicates(subset=["facility_id"])
