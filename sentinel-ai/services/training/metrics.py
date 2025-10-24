from fastapi import FastAPI
from typing import Dict, Any
import time
import os

app = FastAPI(title="Sentinel AI – Metrics API")

# Simple metrics storage (in production, use proper metrics DB)
metrics_store = {
    "latency_ms": [],
    "decisions": {"APPROVE": 0, "STEP_UP": 0, "REVIEW": 0},
    "feedback_count": 0,
    "model_accuracy": 0.0
}

@app.get("/metrics")
def get_metrics() -> Dict[str, Any]:
    """Get current model performance metrics"""
    avg_latency = sum(metrics_store["latency_ms"]) / len(metrics_store["latency_ms"]) if metrics_store["latency_ms"] else 0
    
    return {
        "average_latency_ms": avg_latency,
        "decision_counts": metrics_store["decisions"],
        "total_feedback_samples": metrics_store["feedback_count"],
        "model_accuracy": metrics_store["model_accuracy"],
        "models_available": {
            "anomaly_iforest": os.path.exists("models/anomaly_iforest.joblib"),
            "behavioral_gb": os.path.exists("models/behavioral_gb.joblib"),
            "behavioral_global_fl": os.path.exists("models/behavioral_global_fl.joblib")
        }
    }

@app.post("/metrics/latency")
def record_latency(latency_ms: float):
    """Record API latency for monitoring"""
    metrics_store["latency_ms"].append(latency_ms)
    # Keep only last 1000 measurements
    if len(metrics_store["latency_ms"]) > 1000:
        metrics_store["latency_ms"] = metrics_store["latency_ms"][-1000:]
    return {"status": "recorded"}

@app.post("/metrics/decision")
def record_decision(decision: str):
    """Record decision for analytics"""
    if decision in metrics_store["decisions"]:
        metrics_store["decisions"][decision] += 1
    return {"status": "recorded"}

@app.post("/metrics/feedback")
def record_feedback():
    """Record feedback submission"""
    metrics_store["feedback_count"] += 1
    return {"status": "recorded"}
