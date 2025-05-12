"""
Script to validate the Okinawa tourism dataset against requirements locally.
"""
import os
import pandas as pd

def validate_dataset():
    """Validate the dataset against the requirements."""
    print("Validating Okinawa tourism dataset against requirements...")
    
    final_csv = "okinawa_tourism_20250422.csv"
    latest_csv = os.path.join("data", final_csv)
    
    if not os.path.exists(latest_csv):
        print(f"ERROR: Final CSV file not found: {latest_csv}")
        return False
    print(f"Using dataset: {latest_csv}")
    
    try:
        df = pd.read_csv(latest_csv)
    except Exception as e:
        print(f"ERROR: Failed to read CSV file: {str(e)}")
        return False
    
    num_rows = len(df)
    print(f"Number of rows: {num_rows}")
    if num_rows >= 120:
        print("✅ Dataset contains at least 120 rows")
    else:
        print(f"❌ Dataset contains only {num_rows} rows, expected at least 120")
        return False
    
    unknown_visitors = df[df["annual_visitors"] == "Unknown"].shape[0]
    missing_rate = (unknown_visitors / num_rows) * 100
    print(f"Missing rate for annual visitors: {missing_rate:.2f}%")
    if missing_rate < 40:
        print("✅ Missing rate for annual visitors is less than 40%")
    else:
        print(f"❌ Missing rate for annual visitors is {missing_rate:.2f}%, expected less than 40%")
        return False
    
    total_reviews = df["google_maps_reviews"].sum() + df["tripadvisor_reviews"].sum() + df["tabelog_reviews"].sum()
    print(f"Total number of reviews: {total_reviews}")
    if total_reviews >= 1000:
        print("✅ Total number of reviews is at least 1,000")
    else:
        print(f"❌ Total number of reviews is only {total_reviews}, expected at least 1,000")
        return False
    
    if not os.path.exists("README.md"):
        print("❌ README.md file not found")
        return False
    
    with open("README.md", "r") as f:
        readme_content = f.read()
    
    if "Data Acquisition Process" in readme_content:
        print("✅ README describes the data acquisition process")
    else:
        print("❌ README does not describe the data acquisition process")
        return False
    
    if "License" in readme_content:
        print("✅ README includes license information")
    else:
        print("❌ README does not include license information")
        return False
    
    required_columns = [
        "name_en", "name_jp", "location", "address", "lat", "lng",
        "opening_hours_Monday", "opening_hours_Tuesday", "opening_hours_Wednesday",
        "opening_hours_Thursday", "opening_hours_Friday", "opening_hours_Saturday",
        "opening_hours_Sunday", "closing_days",
        "annual_visitors", "visitor_source_url",
        "google_maps_reviews", "google_maps_rating",
        "tripadvisor_reviews", "tripadvisor_rating",
        "twitter_hashtags",
        "tabelog_reviews", "tabelog_rating",
        "positive_keywords", "negative_keywords",
        "main_highlights", "last_updated_date"
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if not missing_columns:
        print("✅ Dataset contains all required columns")
    else:
        print(f"❌ Dataset is missing the following required columns: {missing_columns}")
        return False
    
    print("\n✅ SUCCESS: Dataset meets all requirements!")
    return True

if __name__ == "__main__":
    validate_dataset()
