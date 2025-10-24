from pydantic import BaseModel, Field
from typing import Optional, Dict

class Transaction(BaseModel):
    txn_id: str
    amount: float
    merchant_category: str
    device_id: str
    geo_lat: float
    geo_lon: float
    user_id: str
    is_new_device: bool = False
    hour_of_day: int
    past_24h_txn_count: int
    past_7d_chargebacks: int
    velocity_usd_7d: float
    ip_asn_risk: float = 0.0

class RiskResponse(BaseModel):
    risk_vector: Dict[str, float]  # {"behavioral":..,"network":..,"anomaly":..}
    risk_score: float              # optional scalar summary (0..1)
    decision: str                  # "APPROVE" | "STEP_UP" | "REVIEW"
    reasons: Dict[str, float]      # top features (for trust/explain)
