import numpy as np
import pandas as pd

CATEGORICALS = ["merchant_category"]
NUMERICS = ["amount","geo_lat","geo_lon","hour_of_day","past_24h_txn_count",
            "past_7d_chargebacks","velocity_usd_7d","ip_asn_risk"]
BINARIES = ["is_new_device"]

def to_frame(txn_dict):
    df = pd.DataFrame([txn_dict])
    # simple encodings (replace later with sklearn ColumnTransformer pipeline)
    for b in BINARIES:
        df[b] = df[b].astype(int)
    for c in CATEGORICALS:
        df[c] = df[c].astype("category")
    return df
