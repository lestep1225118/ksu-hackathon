#!/usr/bin/env python3
"""
Test script for Sentinel AI Risk API
"""
import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_score_transaction():
    """Test the risk scoring endpoint"""
    print("Testing risk scoring...")
    
    # Test case 1: Low risk transaction
    low_risk_txn = {
        "txn_id": "test_001",
        "amount": 25.50,
        "merchant_category": "grocery",
        "device_id": "D123",
        "geo_lat": 37.7749,
        "geo_lon": -122.4194,
        "user_id": "U001",
        "is_new_device": False,
        "hour_of_day": 14,
        "past_24h_txn_count": 1,
        "past_7d_chargebacks": 0,
        "velocity_usd_7d": 150.0,
        "ip_asn_risk": 0.05
    }
    
    # Test case 2: High risk transaction
    high_risk_txn = {
        "txn_id": "test_002",
        "amount": 2500.0,
        "merchant_category": "luxury",
        "device_id": "D456",
        "geo_lat": 37.7749,
        "geo_lon": -122.4194,
        "user_id": "U002",
        "is_new_device": True,
        "hour_of_day": 3,
        "past_24h_txn_count": 8,
        "past_7d_chargebacks": 2,
        "velocity_usd_7d": 15000.0,
        "ip_asn_risk": 0.8
    }
    
    for i, txn in enumerate([low_risk_txn, high_risk_txn], 1):
        print(f"\nTest Case {i}:")
        print(f"Transaction: ${txn['amount']} at {txn['merchant_category']}")
        print(f"New device: {txn['is_new_device']}, Velocity: ${txn['velocity_usd_7d']}")
        
        try:
            response = requests.post(f"{API_BASE}/score", json=txn)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Risk Score: {result['risk_score']:.3f}")
                print(f"✅ Decision: {result['decision']}")
                print(f"✅ Risk Vector: {result['risk_vector']}")
                print(f"✅ Top Reasons: {result['reasons']}")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Make sure the API is running on port 8000")
            return False
    
    return True

def test_feedback():
    """Test the feedback endpoint"""
    print("\nTesting feedback submission...")
    
    feedback_data = {
        "txn_id": "test_feedback_001",
        "amount": 899.0,
        "merchant_category": "electronics",
        "device_id": "D789",
        "geo_lat": 37.7,
        "geo_lon": -122.4,
        "user_id": "U003",
        "is_new_device": True,
        "hour_of_day": 2,
        "past_24h_txn_count": 6,
        "past_7d_chargebacks": 1,
        "velocity_usd_7d": 4200,
        "ip_asn_risk": 0.25,
        "label": "FRAUD"
    }
    
    try:
        response = requests.post(f"{API_BASE}/feedback", json=feedback_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Feedback submitted: {result}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API is running on port 8000")
        return False
    
    return True

def test_health():
    """Test the health endpoint"""
    print("Testing health endpoint...")
    
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API Health: {result}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API is running on port 8000")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Sentinel AI Risk API Test Suite")
    print("=" * 50)
    
    # Test health first
    if not test_health():
        print("\n❌ API is not running. Start it with:")
        print("uvicorn services.risk_api.main:app --reload --port 8000")
        exit(1)
    
    # Test scoring
    test_score_transaction()
    
    # Test feedback
    test_feedback()
    
    print("\n✅ All tests completed!")
    print("\nNext steps:")
    print("1. Run: python -m services.training.retrain")
    print("2. Run: python -m services.federation.fed_sim")
