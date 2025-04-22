"""
Test file to validate the Okinawa tourism dataset against requirements.
"""
import os
import pandas as pd
import pytest

def test_dataset_rows():
    """Test that the dataset contains at least 120 rows."""
    csv_files = [f for f in os.listdir("data") if f.startswith("okinawa_tourism_") and f.endswith(".csv")]
    csv_files.sort(reverse=True)
    
    assert len(csv_files) > 0, "No CSV files found in data directory"
    
    latest_csv = os.path.join("data", csv_files[0])
    df = pd.read_csv(latest_csv)
    
    assert len(df) >= 120, f"Dataset contains {len(df)} rows, expected at least 120"
    print(f"Dataset contains {len(df)} rows, which meets the requirement of at least 120")

def test_missing_rate():
    """Test that the missing rate in the 'Annual Visitors' column is less than 40%."""
    csv_files = [f for f in os.listdir("data") if f.startswith("okinawa_tourism_") and f.endswith(".csv")]
    csv_files.sort(reverse=True)
    
    assert len(csv_files) > 0, "No CSV files found in data directory"
    
    latest_csv = os.path.join("data", csv_files[0])
    df = pd.read_csv(latest_csv)
    
    unknown_visitors = df[df["annual_visitors"] == "Unknown"].shape[0]
    missing_rate = (unknown_visitors / len(df)) * 100
    
    assert missing_rate < 40, f"Missing rate for annual visitors is {missing_rate:.2f}%, expected less than 40%"
    print(f"Missing rate for annual visitors is {missing_rate:.2f}%, which meets the requirement of less than 40%")

def test_review_count():
    """Test that the total number of reviews collected is at least 1,000."""
    csv_files = [f for f in os.listdir("data") if f.startswith("okinawa_tourism_") and f.endswith(".csv")]
    csv_files.sort(reverse=True)
    
    assert len(csv_files) > 0, "No CSV files found in data directory"
    
    latest_csv = os.path.join("data", csv_files[0])
    df = pd.read_csv(latest_csv)
    
    total_reviews = df["google_maps_reviews"].sum() + df["tripadvisor_reviews"].sum() + df["tabelog_reviews"].sum()
    
    assert total_reviews >= 1000, f"Total number of reviews is {total_reviews}, expected at least 1,000"
    print(f"Total number of reviews is {total_reviews}, which meets the requirement of at least 1,000")

def test_readme_content():
    """Test that the README file describes the data acquisition process and includes license information."""
    assert os.path.exists("README.md"), "README.md file not found"
    
    with open("README.md", "r") as f:
        readme_content = f.read()
    
    assert "Data Acquisition Process" in readme_content, "README does not describe the data acquisition process"
    
    assert "License" in readme_content, "README does not include license information"
    
    print("README file describes the data acquisition process and includes license information")

if __name__ == "__main__":
    test_dataset_rows()
    test_missing_rate()
    test_review_count()
    test_readme_content()
