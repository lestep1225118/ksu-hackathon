import json, joblib, pandas as pd
from pathlib import Path
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.features import CATEGORICALS, NUMERICS, BINARIES

LABELS = Path("data/labels.jsonl")

def load_feedback():
    if not LABELS.exists(): return pd.DataFrame()
    rows = [json.loads(l) for l in LABELS.read_text().splitlines() if l.strip()]
    return pd.DataFrame(rows)

def train():
    df = load_feedback()
    if df.empty: 
        print("No feedback yet; skipping."); return
    y = df["label"].astype(int)
    X = df.drop(columns=["label"])
    pre = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICALS),
        ("num", "passthrough", NUMERICS+BINARIES)
    ])
    clf = GradientBoostingClassifier()
    pipe = Pipeline([("pre", pre), ("clf", clf)])
    pipe.fit(X, y)
    joblib.dump(pipe, "models/behavioral_gb.joblib")
    print(f"Trained model on {len(df)} feedback samples")

if __name__ == "__main__":
    train()
