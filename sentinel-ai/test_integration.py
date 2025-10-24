#!/usr/bin/env python3
"""
Test script for Kaggle dataset integration
Run this to test the complete pipeline
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}")
    print(f"   Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"   ✅ Success")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e}")
        if e.stderr:
            print(f"   Error output: {e.stderr.strip()}")
        return False

def main():
    """Test the complete Kaggle integration"""
    print("🧪 TESTING KAGGLE DATASET INTEGRATION")
    print("=" * 50)
    
    # Change to the sentinel-ai directory
    os.chdir("/Users/anvitayerramsetty/ksu/ksu-hackathon/sentinel-ai")
    
    # Step 1: Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("❌ Failed to install dependencies")
        return
    
    # Step 2: Download Kaggle dataset
    if not run_command("python download_data.py", "Downloading Kaggle dataset"):
        print("❌ Failed to download dataset")
        return
    
    # Step 3: Bootstrap the model
    if not run_command("python -m services.training.bootstrap_model", "Bootstrapping model"):
        print("❌ Failed to bootstrap model")
        return
    
    # Step 4: Start the API (in background)
    print("\n🔄 Starting API server...")
    try:
        api_process = subprocess.Popen(
            ["uvicorn", "services.risk_api.main:app", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a moment for the server to start
        import time
        time.sleep(3)
        
        # Step 5: Run the demo
        if run_command("python demo.py", "Running demo with Kaggle data"):
            print("\n🎉 INTEGRATION TEST SUCCESSFUL!")
            print("=" * 50)
            print("✅ Kaggle dataset downloaded")
            print("✅ Model trained and loaded")
            print("✅ API server running")
            print("✅ Demo completed successfully")
        else:
            print("\n❌ Demo failed")
        
        # Clean up
        api_process.terminate()
        api_process.wait()
        
    except Exception as e:
        print(f"❌ Error running API: {e}")

if __name__ == "__main__":
    main()
