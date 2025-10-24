import joblib, numpy as np, pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import sys; import os; sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); from shared.features import CATEGORICALS, NUMERICS, BINARIES

def bootstrap():
    # synth data to start (replace with real/simulated)
    n=2000
    rng = np.random.default_rng(42)
    df = pd.DataFrame({
        "amount": rng.gamma(2, 60, n),
        "geo_lat": rng.normal(37, 2, n),
        "geo_lon": rng.normal(-97, 3, n),
        "hour_of_day": rng.integers(0,24,n),
        "past_24h_txn_count": rng.integers(0,10,n),
        "past_7d_chargebacks": rng.integers(0,3,n),
        "velocity_usd_7d": rng.gamma(3,100,n),
        "ip_asn_risk": rng.random(n)*0.3,
        "is_new_device": rng.random(n)<0.15,
        "merchant_category": rng.choice(["grocery","electronics","luxury","gaming"], n),
        "label": rng.random(n) < 0.04  # ~4% fraud rate (toy)
    })

    # pipeline
    pre = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICALS),
        ("num", "passthrough", NUMERICS+BINARIES)
    ])
    iso = IsolationForest(n_estimators=100, random_state=0, contamination=0.04)
    pipe = Pipeline([("pre", pre), ("iso", iso)])
    pipe.fit(df.drop(columns=["label"]))

    joblib.dump(pipe, "models/anomaly_iforest.joblib")

if __name__ == "__main__":
    bootstrap()
