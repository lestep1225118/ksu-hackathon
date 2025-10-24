from fastapi import FastAPI
from services.shared.schemas import Transaction, RiskResponse
from services.shared.features import to_frame, CATEGORICALS, NUMERICS, BINARIES
import joblib, numpy as np
from typing import Literal

app = FastAPI(title="Sentinel AI – Risk API")

# thresholds from PRD: low <0.2, medium 0.2–0.6, high >0.6 (tune later)
LOW_T, HIGH_T = 0.2, 0.6

# Load the bootstrap model
try:
    pipe = joblib.load("models/anomaly_iforest.joblib")
except FileNotFoundError:
    print("Warning: Bootstrap model not found. Run 'python -m services.training.bootstrap_model' first")
    pipe = None

def compute_risk_vector(df):
    # 3 heads (toy): behavioral, network, anomaly
    # you can replace these with dedicated models later
    behavioral = np.tanh(
        0.4*df["past_24h_txn_count"].values[0] +
        0.6*df["velocity_usd_7d"].values[0]/1000.0 +
        0.8*df["is_new_device"].astype(int).values[0]
    )
    network = np.tanh( df["ip_asn_risk"].values[0] + (1 if df["merchant_category"].astype(str).values[0] in ["luxury","gaming"] else 0)*0.3 )
    
    # anomaly via IF: convert score (higher = more normal) → anomaly risk in [0,1]
    if pipe is not None:
        score = pipe.decision_function(df.drop(columns=[]))  # ~ [-0.5..0.5]
        anomaly = np.clip(0.5 - score[0], 0, 1.0)
    else:
        anomaly = 0.1  # fallback if no model

    return {
        "behavioral": float(np.clip(behavioral, 0, 1)),
        "network": float(np.clip(network, 0, 1)),
        "anomaly": float(anomaly)
    }

def summarize(vector):
    # simple learned weights placeholder (later from logistic/CalibratedClassifierCV)
    w = {"behavioral":0.4, "network":0.25, "anomaly":0.35}
    s = sum(w[k]*vector[k] for k in w)
    return float(s)

def decide(risk_score: float):
    if risk_score < LOW_T: return "APPROVE"
    if risk_score < HIGH_T: return "STEP_UP"
    return "REVIEW"

def top_reasons(df):
    # lightweight "explainability" fallback if SHAP not computed
    reasons = {}
    reasons["is_new_device"] = float(df["is_new_device"].astype(int).values[0])
    reasons["velocity_usd_7d"] = float(df["velocity_usd_7d"].values[0])
    reasons["past_24h_txn_count"] = float(df["past_24h_txn_count"].values[0])
    reasons["ip_asn_risk"] = float(df["ip_asn_risk"].values[0])
    return dict(sorted(reasons.items(), key=lambda kv: abs(kv[1]), reverse=True)[:4])

def user_messages(decision, reasons):
    if decision=="STEP_UP":
        return "Extra verification because of a new device and recent high spend."
    if decision=="REVIEW":
        return "We've paused this payment for a quick safety check due to unusual patterns."
    return "Payment approved securely."

@app.post("/score", response_model=RiskResponse)
def score(txn: Transaction):
    df = to_frame(txn.dict())
    vec = compute_risk_vector(df)
    s = summarize(vec)
    decision = decide(s)
    message = user_messages(decision, vec)
    return RiskResponse(
        risk_vector=vec, 
        risk_score=s, 
        decision=decision, 
        reasons=top_reasons(df)
    )

# Feedback for continuous learning
class FeedbackIn(Transaction):
    label: Literal["FRAUD","LEGIT"]

@app.post("/feedback")
def feedback(fb: FeedbackIn):
    # append to training set for retrain job
    import json, os
    os.makedirs("data", exist_ok=True)
    with open("data/labels.jsonl","a") as f:
        rec = fb.dict()
        rec["label"] = 1 if fb.label=="FRAUD" else 0
        f.write(json.dumps(rec)+"\n")
    return {"status":"ok"}

@app.get("/")
def root():
    return {"message": "Sentinel AI Risk API", "status": "running"}
