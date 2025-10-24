# Sentinel AI - Risk Scoring Prototype

A real-time risk-scoring API with adaptive friction, continuous learning, and federated intelligence.

## Quick Start

1. **Bootstrap the model:**
   ```bash
   python -m services.training.bootstrap_model
   ```

2. **Start the API:**
   ```bash
   uvicorn services.risk_api.main:app --reload --port 8000
   ```

3. **Test scoring:**
   ```bash
   curl -X POST http://localhost:8000/score -H "Content-Type: application/json" -d '{
     "txn_id":"t1","amount":899.0,"merchant_category":"electronics",
     "device_id":"D123","geo_lat":37.7,"geo_lon":-122.4,"user_id":"U1",
     "is_new_device":true,"hour_of_day":2,"past_24h_txn_count":6,
     "past_7d_chargebacks":1,"velocity_usd_7d":4200,"ip_asn_risk":0.25
   }'
   ```

4. **Send feedback:**
   ```bash
   curl -X POST http://localhost:8000/feedback -H "Content-Type: application/json" -d '{
     "txn_id":"t1","amount":899.0,"merchant_category":"electronics",
     "device_id":"D123","geo_lat":37.7,"geo_lon":-122.4,"user_id":"U1",
     "is_new_device":true,"hour_of_day":2,"past_24h_txn_count":6,
     "past_7d_chargebacks":1,"velocity_usd_7d":4200,"ip_asn_risk":0.25,
     "label":"FRAUD"
   }'
   ```

5. **Retrain with feedback:**
   ```bash
   python -m services.training.retrain
   ```

6. **Run federated simulation:**
   ```bash
   python -m services.federation.fed_sim
   ```

## Architecture

- **Risk API**: Real-time scoring with adaptive friction decisions
- **Continuous Learning**: Nightly retrain with analyst feedback
- **Federated Learning**: Multi-bank intelligence without data sharing
- **Trust Layer**: Explainable decisions with user-friendly messages

## API Endpoints

- `POST /score` - Score a transaction
- `POST /feedback` - Submit analyst feedback
- `GET /` - Health check

## Models

- `anomaly_iforest.joblib` - Bootstrap anomaly detection
- `behavioral_gb.joblib` - Continuous learning model
- `behavioral_global_fl.joblib` - Federated learning model
