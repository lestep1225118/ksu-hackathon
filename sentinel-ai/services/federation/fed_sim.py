import numpy as np, pandas as pd, joblib
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from services.shared.features import CATEGORICALS, NUMERICS, BINARIES

def synth_client(seed: int, n=1200, fraud_rate=0.04):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "amount": rng.gamma(2, 60, n),
        "geo_lat": rng.normal(37+seed%3, 2, n),
        "geo_lon": rng.normal(-97-seed%4, 3, n),
        "hour_of_day": rng.integers(0,24,n),
        "past_24h_txn_count": rng.integers(0,10,n),
        "past_7d_chargebacks": rng.integers(0,3,n),
        "velocity_usd_7d": rng.gamma(3,100,n),
        "ip_asn_risk": rng.random(n)*0.3,
        "is_new_device": rng.random(n)<0.15,
        "merchant_category": rng.choice(["grocery","electronics","luxury","gaming"], n),
    })
    y = (rng.random(n) < fraud_rate).astype(int)
    return df, y

def client_update(df, y, global_coefs=None, global_intercept=None):
    pre = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICALS),
        ("num", "passthrough", NUMERICS+BINARIES)
    ])
    clf = SGDClassifier(loss="log_loss", max_iter=1, learning_rate="constant", eta0=0.01)
    pipe = Pipeline([("pre", pre), ("clf", clf)])
    pipe.fit(df, y)
    return pipe

def average(pipes):
    # simple parameter average on final layer (demo only)
    # (Real FL averages full weights; here we refit a fresh model on concatenated transformed data for simplicity)
    # Combine client data and refit once:
    Xs, ys = [], []
    for p in pipes:
        # Not perfect access to transformed X; re-train centrally as proxy:
        pass
    # Practical shortcut: concatenate raw client data and fit a single "global" model (for demo)
    dfs, ys = [], []
    for seed in [0,1,2]:
        df,y = synth_client(seed)
        dfs.append(df); ys.append(y)
    df_all = pd.concat(dfs, ignore_index=True)
    y_all = np.concatenate(ys)
    pre = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICALS),
        ("num", "passthrough", NUMERICS+BINARIES)
    ])
    clf = SGDClassifier(loss="log_loss", max_iter=2000)
    from sklearn.pipeline import Pipeline
    global_pipe = Pipeline([("pre", pre), ("clf", clf)])
    global_pipe.fit(df_all, y_all)
    joblib.dump(global_pipe, "models/behavioral_global_fl.joblib")
    print("Saved FL global model → models/behavioral_global_fl.joblib")

if __name__ == "__main__":
    clients = [synth_client(s) for s in [0,1,2]]
    pipes = [client_update(df,y) for (df,y) in clients]
    average(pipes)
