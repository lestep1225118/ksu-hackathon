#!/usr/bin/env python3
"""
Data Download Script for Sentinel AI
Downloads the Kaggle fraud dataset and prepares it for training
"""
import kagglehub
import pandas as pd
import os
import json
from pathlib import Path

def download_kaggle_dataset():
    """Download the Kaggle fraud dataset"""
    print("📥 Downloading Kaggle fraud dataset...")
    
    try:
        # Download latest version
        path = kagglehub.dataset_download("computingvictor/transactions-fraud-datasets")
        print(f"✅ Dataset downloaded to: {path}")
        
        # List files in the dataset
        dataset_files = list(Path(path).glob("*"))
        print(f"📁 Dataset contains {len(dataset_files)} files:")
        for file in dataset_files:
            print(f"   - {file.name}")
        
        return path
        
    except Exception as e:
        print(f"❌ Error downloading dataset: {e}")
        return None

def explore_dataset(dataset_path):
    """Explore the downloaded dataset structure"""
    print("\n🔍 Exploring dataset structure...")
    
    dataset_dir = Path(dataset_path)
    
    # Find CSV files
    csv_files = list(dataset_dir.glob("*.csv"))
    print(f"📊 Found {len(csv_files)} CSV files:")
    
    for csv_file in csv_files:
        print(f"\n📄 Analyzing {csv_file.name}:")
        try:
            df = pd.read_csv(csv_file)
            print(f"   Shape: {df.shape}")
            print(f"   Columns: {list(df.columns)}")
            
            # Check for fraud-related columns
            fraud_cols = [col for col in df.columns if 'fraud' in col.lower() or 'label' in col.lower()]
            if fraud_cols:
                print(f"   Fraud columns: {fraud_cols}")
                for col in fraud_cols:
                    print(f"     {col}: {df[col].value_counts().to_dict()}")
            
        except Exception as e:
            print(f"   ❌ Error reading {csv_file.name}: {e}")
    
    return csv_files

def prepare_training_data(dataset_path, output_dir="data"):
    """Prepare the dataset for training"""
    print(f"\n🔄 Preparing training data...")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    dataset_dir = Path(dataset_path)
    csv_files = list(dataset_dir.glob("*.csv"))
    
    if not csv_files:
        print("❌ No CSV files found in dataset")
        return None
    
    # Use the first CSV file (you can modify this logic based on your needs)
    main_file = csv_files[0]
    print(f"📊 Using main dataset: {main_file.name}")
    
    try:
        df = pd.read_csv(main_file)
        print(f"   Loaded {len(df)} rows, {len(df.columns)} columns")
        
        # Save processed data
        processed_file = output_path / "fraud_dataset.csv"
        df.to_csv(processed_file, index=False)
        print(f"✅ Saved processed data to: {processed_file}")
        
        # Create a sample for quick testing
        sample_file = output_path / "fraud_sample.csv"
        sample_df = df.sample(n=min(1000, len(df)), random_state=42)
        sample_df.to_csv(sample_file, index=False)
        print(f"✅ Saved sample data to: {sample_file}")
        
        # Create metadata
        metadata = {
            "dataset_name": "computingvictor/transactions-fraud-datasets",
            "original_file": str(main_file),
            "processed_file": str(processed_file),
            "sample_file": str(sample_file),
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": list(df.columns),
            "shape": df.shape
        }
        
        metadata_file = output_path / "dataset_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✅ Saved metadata to: {metadata_file}")
        
        return processed_file
        
    except Exception as e:
        print(f"❌ Error processing dataset: {e}")
        return None

def main():
    """Main function to download and prepare the dataset"""
    print("🚀 SENTINEL AI - Dataset Download")
    print("=" * 50)
    
    # Download dataset
    dataset_path = download_kaggle_dataset()
    if not dataset_path:
        return
    
    # Explore dataset
    csv_files = explore_dataset(dataset_path)
    
    # Prepare training data
    processed_file = prepare_training_data(dataset_path)
    
    if processed_file:
        print("\n🎉 Dataset preparation complete!")
        print("=" * 50)
        print("✅ Dataset downloaded from Kaggle")
        print("✅ Data explored and analyzed")
        print("✅ Training data prepared")
        print("✅ Sample data created for testing")
        print("\nNext steps:")
        print("• Use the processed data for model training")
        print("• Integrate with your existing training pipeline")
        print("• Update demo.py to use real data")
    else:
        print("\n❌ Dataset preparation failed")

if __name__ == "__main__":
    main()
