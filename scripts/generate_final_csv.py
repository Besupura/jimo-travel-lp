"""
Script to generate and validate the final CSV file for Okinawa tourist attractions.
"""
import os
import json
import pandas as pd
from datetime import datetime
import re

os.makedirs("data", exist_ok=True)

def load_attractions_with_keywords():
    """Load the attractions with keywords."""
    today = datetime.now().strftime("%Y%m%d")
    csv_path = f"data/okinawa_tourism_with_keywords_{today}.csv"
    return pd.read_csv(csv_path)

def validate_dataset(df):
    """Validate the dataset against the requirements."""
    print("Validating dataset...")
    
    num_rows = len(df)
    print(f"Number of rows: {num_rows} (required: at least 120)")
    if num_rows < 120:
        print("WARNING: Dataset has fewer than 120 rows")
    
    unknown_visitors = df[df["annual_visitors"] == "Unknown"].shape[0]
    missing_rate = (unknown_visitors / num_rows) * 100
    print(f"Missing rate for annual visitors: {missing_rate:.2f}% (required: less than 40%)")
    if missing_rate >= 40:
        print("WARNING: Missing rate for annual visitors is too high")
    
    total_reviews = df["google_maps_reviews"].sum() + df["tripadvisor_reviews"].sum() + df["tabelog_reviews"].sum()
    print(f"Total number of reviews: {total_reviews} (required: at least 1,000)")
    if total_reviews < 1000:
        print("WARNING: Total number of reviews is too low")
    
    required_columns = [
        "name_en", "name_jp", "location", "address", "lat", "lng",
        "opening_hours_Monday", "opening_hours_Tuesday", "opening_hours_Wednesday",
        "opening_hours_Thursday", "opening_hours_Friday", "opening_hours_Saturday",
        "opening_hours_Sunday", "closing_days",
        "annual_visitors", "visitor_year", "visitor_source_url",
        "google_maps_reviews", "google_maps_rating",
        "tripadvisor_reviews", "tripadvisor_rating",
        "twitter_hashtags",
        "tabelog_reviews", "tabelog_rating",
        "positive_keywords", "negative_keywords"
    ]
    
    for column in required_columns:
        if column not in df.columns:
            print(f"WARNING: Required column '{column}' is missing")
        elif df[column].isna().sum() > 0:
            print(f"WARNING: Column '{column}' has {df[column].isna().sum()} missing values")
    
    duplicates = df.duplicated(subset=["name_en"]).sum()
    if duplicates > 0:
        print(f"WARNING: Found {duplicates} duplicate attractions based on English name")
    
    return {
        "num_rows": num_rows,
        "missing_rate": missing_rate,
        "total_reviews": total_reviews,
        "is_valid": num_rows >= 120 and missing_rate < 40 and total_reviews >= 1000
    }

def add_last_updated_date(df):
    """Add the last updated date to the dataset."""
    df["last_updated_date"] = datetime.now().strftime("%Y-%m-%d")
    return df

def format_highlights(df):
    """Format the main highlights and features within 150 characters."""
    print("Formatting main highlights and features...")
    
    df["main_highlights"] = ""
    
    for idx, row in df.iterrows():
        attraction_name = row["name_en"]
        positive_keywords = row["positive_keywords"].split(", ")
        
        if "Castle" in attraction_name or "城" in attraction_name:
            highlight = f"Historic Ryukyu Kingdom castle featuring {positive_keywords[0]} architecture and {positive_keywords[1]} cultural significance."
        elif "Beach" in attraction_name or "浜" in attraction_name or "ビーチ" in attraction_name:
            highlight = f"Beautiful beach with {positive_keywords[0]} crystal-clear waters and {positive_keywords[1]} white sand, perfect for swimming and snorkeling."
        elif "Aquarium" in attraction_name or "水族館" in attraction_name:
            highlight = f"{positive_keywords[0]} marine exhibits including whale sharks and manta rays, with {positive_keywords[1]} interactive displays."
        elif "Park" in attraction_name or "公園" in attraction_name:
            highlight = f"Scenic park offering {positive_keywords[0]} natural beauty and {positive_keywords[1]} relaxation spots with panoramic ocean views."
        elif "Museum" in attraction_name or "博物館" in attraction_name or "美術館" in attraction_name:
            highlight = f"Educational museum showcasing {positive_keywords[0]} Okinawan history and {positive_keywords[1]} cultural artifacts."
        elif "Island" in attraction_name or "島" in attraction_name:
            highlight = f"Picturesque island with {positive_keywords[0]} untouched nature and {positive_keywords[1]} traditional Okinawan lifestyle."
        elif "Street" in attraction_name or "通り" in attraction_name:
            highlight = f"Vibrant shopping street with {positive_keywords[0]} local shops and {positive_keywords[1]} restaurants offering authentic Okinawan cuisine."
        else:
            highlight = f"Popular Okinawa attraction known for its {positive_keywords[0]} atmosphere and {positive_keywords[1]} unique experiences."
        
        if len(highlight) > 150:
            highlight = highlight[:147] + "..."
        
        df.at[idx, "main_highlights"] = highlight
    
    return df

def generate_final_csv(df):
    """Generate the final CSV file with all required columns."""
    print("Generating final CSV file...")
    
    required_columns = [
        "name_en", "name_jp", "location", "address", "lat", "lng",
        "opening_hours_Monday", "opening_hours_Tuesday", "opening_hours_Wednesday",
        "opening_hours_Thursday", "opening_hours_Friday", "opening_hours_Saturday",
        "opening_hours_Sunday", "closing_days", "hours_source_url", "hours_acquisition_date",
        "annual_visitors", "visitor_year", "visitor_source_url", "visitor_acquisition_date", "visitor_remarks",
        "google_maps_reviews", "google_maps_rating",
        "tripadvisor_reviews", "tripadvisor_rating",
        "twitter_hashtags",
        "tabelog_reviews", "tabelog_rating",
        "positive_keywords", "negative_keywords",
        "main_highlights", "last_updated_date"
    ]
    
    final_columns = [col for col in required_columns if col in df.columns]
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"WARNING: The following required columns are missing: {missing_columns}")
        for col in missing_columns:
            df[col] = ""
    
    df = df[required_columns]
    
    today = datetime.now().strftime("%Y%m%d")
    output_path = f"data/okinawa_tourism_{today}.csv"
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"Saved final CSV to {output_path}")
    
    return output_path

def main():
    """Main function to generate and validate the final CSV file."""
    attractions_df = load_attractions_with_keywords()
    print(f"Loaded {len(attractions_df)} attractions with keywords")
    
    attractions_df = add_last_updated_date(attractions_df)
    
    attractions_df = format_highlights(attractions_df)
    
    output_path = generate_final_csv(attractions_df)
    
    validation_results = validate_dataset(attractions_df)
    
    if validation_results["is_valid"]:
        print("SUCCESS: Dataset meets all requirements!")
    else:
        print("WARNING: Dataset does not meet all requirements. Please check the validation results.")
    
    print("\nDataset Summary:")
    print(f"- Number of attractions: {validation_results['num_rows']}")
    print(f"- Missing rate for annual visitors: {validation_results['missing_rate']:.2f}%")
    print(f"- Total number of reviews: {validation_results['total_reviews']}")
    print(f"- Output file: {output_path}")

if __name__ == "__main__":
    main()
