import pandas as pd

def build_dim_provider(df_raw_users: pd.DataFrame) -> pd.DataFrame:
    """Extracts clinical healthcare providers into dim_provider."""
    df = pd.DataFrame()
    
    if df_raw_users.empty:
        # Fallback default provider
        return pd.DataFrame([{
            "provider_id": 1,
            "role": "doctor",
            "is_active": True,
        }])
        
    df["provider_id"] = df_raw_users["id"].astype(int)
    df["role"] = df_raw_users.get("role", "doctor").fillna("doctor").astype(str).str.lower()
    df["is_active"] = df_raw_users.get("is_active", True).fillna(True).astype(bool)
    
    # Filter to unique provider_ids
    return df.drop_duplicates(subset=["provider_id"])
