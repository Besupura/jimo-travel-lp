"""
Script to extract keywords from reviews for Okinawa tourist attractions.
Simulates Japanese morphological analysis and TF-IDF calculation.
"""
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
import random

os.makedirs("raw", exist_ok=True)

def load_attractions_with_reviews():
    """Load the attractions with review data."""
    today = datetime.now().strftime("%Y%m%d")
    csv_path = f"data/okinawa_tourism_with_reviews_{today}.csv"
    return pd.read_csv(csv_path)

def simulate_review_text_generation(attraction_name, platform, rating):
    """
    Simulate generating review text based on attraction name and rating.
    In a real implementation, this would use actual review text from APIs.
    """
    positive_words = [
        "素晴らしい", "美しい", "最高", "楽しい", "綺麗", "おすすめ", "良い", "素敵", "満足", "快適",
        "親切", "美味しい", "便利", "リラックス", "癒される", "感動", "魅力的", "優れた", "豊か", "贅沢",
        "清潔", "静か", "のどか", "活気", "新鮮", "伝統的", "文化的", "歴史的", "自然", "景色",
        "眺め", "雰囲気", "サービス", "価値", "体験", "思い出", "リーズナブル", "フレンドリー", "安全", "充実"
    ]
    
    negative_words = [
        "残念", "悪い", "混雑", "高い", "不便", "汚い", "騒がしい", "不満", "期待外れ", "疲れる",
        "不親切", "不快", "古い", "狭い", "遠い", "退屈", "面倒", "不足", "不十分", "不安",
        "危険", "迷う", "分かりにくい", "不明瞭", "不適切", "不調", "故障", "壊れている", "閉鎖", "工事中",
        "雨", "暑い", "寒い", "湿気", "虫", "観光客", "行列", "待ち時間", "駐車場", "交通"
    ]
    
    is_positive = rating >= 4.0 if rating else random.random() > 0.3
    
    if is_positive:
        selected_words = random.sample(positive_words, min(15, len(positive_words)))
        selected_words += random.sample(negative_words, min(3, len(negative_words)))
    else:
        selected_words = random.sample(negative_words, min(15, len(negative_words)))
        selected_words += random.sample(positive_words, min(3, len(positive_words)))
    
    if "Castle" in attraction_name or "城" in attraction_name:
        selected_words.extend(["城", "歴史", "琉球", "王国", "文化財"])
    elif "Beach" in attraction_name or "浜" in attraction_name or "ビーチ" in attraction_name:
        selected_words.extend(["海", "砂浜", "波", "サンゴ", "シュノーケル", "マリンスポーツ"])
    elif "Aquarium" in attraction_name or "水族館" in attraction_name:
        selected_words.extend(["魚", "イルカ", "ジンベエザメ", "展示", "ショー"])
    elif "Park" in attraction_name or "公園" in attraction_name:
        selected_words.extend(["緑", "自然", "散歩", "広い", "遊具"])
    elif "Museum" in attraction_name or "博物館" in attraction_name or "美術館" in attraction_name:
        selected_words.extend(["展示", "芸術", "学ぶ", "歴史", "文化"])
    elif "Island" in attraction_name or "島" in attraction_name:
        selected_words.extend(["島", "フェリー", "離島", "のんびり", "自然"])
    elif "Street" in attraction_name or "通り" in attraction_name:
        selected_words.extend(["買い物", "お土産", "食べ歩き", "賑やか", "店舗"])
    
    random.shuffle(selected_words)
    
    filler_texts = [
        "とても{}でした。{}も良かったです。{}は特に印象的でした。",
        "{}が素晴らしかったです。ただ、{}は少し{}かなと思いました。",
        "{}に行ってきました。{}で{}な体験ができました。",
        "{}は期待通りでした。{}が{}で満足しています。",
        "{}に家族で訪れました。{}で子供たちも{}と喜んでいました。"
    ]
    
    review_template = random.choice(filler_texts)
    review = review_template.format(
        random.choice(selected_words),
        random.choice(selected_words),
        random.choice(selected_words)
    )
    
    if random.random() > 0.5:
        additional_template = random.choice(filler_texts)
        review += " " + additional_template.format(
            random.choice(selected_words),
            random.choice(selected_words),
            random.choice(selected_words)
        )
    
    return {
        "text": review,
        "words": selected_words,
        "is_positive": is_positive
    }

def simulate_mecab_analysis(review_text):
    """
    Simulate MeCab morphological analysis.
    In a real implementation, this would use MeCab-ipadic-NEologd.
    """
    words = []
    for word in review_text.split():
        word = word.strip("。、！？.!?")
        if word:
            words.append(word)
    
    return words

def simulate_tfidf_calculation(all_reviews_for_attraction):
    """
    Simulate TF-IDF calculation to extract important keywords.
    In a real implementation, this would use scikit-learn or a similar library.
    """
    all_words = []
    for review in all_reviews_for_attraction:
        all_words.extend(review["words"])
    
    word_counts = {}
    for word in all_words:
        word_counts[word] = word_counts.get(word, 0) + 1
    
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    
    positive_words = []
    negative_words = []
    
    for review in all_reviews_for_attraction:
        for word in review["words"]:
            if review["is_positive"] and word not in positive_words:
                positive_words.append(word)
            elif not review["is_positive"] and word not in negative_words:
                negative_words.append(word)
    
    top_positive = positive_words[:min(5, len(positive_words))]
    top_negative = negative_words[:min(5, len(negative_words))]
    
    generic_positive = ["素晴らしい", "美しい", "最高", "楽しい", "綺麗"]
    generic_negative = ["残念", "混雑", "高い", "不便", "騒がしい"]
    
    while len(top_positive) < 5:
        for word in generic_positive:
            if word not in top_positive:
                top_positive.append(word)
                break
    
    while len(top_negative) < 5:
        for word in generic_negative:
            if word not in top_negative:
                top_negative.append(word)
                break
    
    return {
        "top_positive": top_positive[:5],
        "top_negative": top_negative[:5]
    }

def extract_keywords(attractions_df):
    """Extract keywords from reviews for each attraction."""
    print("Extracting keywords from reviews...")
    
    attractions_df["positive_keywords"] = ""
    attractions_df["negative_keywords"] = ""
    
    for idx, row in attractions_df.iterrows():
        attraction_name = row["name_en"]
        print(f"Processing {idx+1}/{len(attractions_df)}: {attraction_name}")
        
        google_rating = row["google_maps_rating"]
        tripadvisor_rating = row["tripadvisor_rating"]
        tabelog_rating = row["tabelog_rating"]
        
        num_reviews = min(50, max(5, int((row["google_maps_reviews"] + row["tripadvisor_reviews"] + row["tabelog_reviews"]) / 100)))
        
        all_reviews = []
        
        for _ in range(int(num_reviews * 0.5)):
            review = simulate_review_text_generation(attraction_name, "google_maps", google_rating)
            all_reviews.append(review)
        
        for _ in range(int(num_reviews * 0.3)):
            review = simulate_review_text_generation(attraction_name, "tripadvisor", tripadvisor_rating)
            all_reviews.append(review)
        
        for _ in range(int(num_reviews * 0.2)):
            review = simulate_review_text_generation(attraction_name, "tabelog", tabelog_rating)
            all_reviews.append(review)
        
        keywords = simulate_tfidf_calculation(all_reviews)
        
        attractions_df.at[idx, "positive_keywords"] = ", ".join(keywords["top_positive"])
        attractions_df.at[idx, "negative_keywords"] = ", ".join(keywords["top_negative"])
        
        if (idx + 1) % 10 == 0:
            print(f"Processed {idx+1}/{len(attractions_df)} attractions")
    
    sample_reviews = {}
    for idx, row in attractions_df.iloc[:5].iterrows():
        attraction_name = row["name_en"]
        reviews = []
        for _ in range(3):
            review = simulate_review_text_generation(attraction_name, "sample", None)
            reviews.append(review["text"])
        sample_reviews[attraction_name] = reviews
    
    with open("raw/sample_reviews.json", "w", encoding="utf-8") as f:
        json.dump(sample_reviews, f, ensure_ascii=False, indent=2)
    
    return attractions_df

def main():
    """Main function to extract keywords from reviews."""
    attractions_df = load_attractions_with_reviews()
    print(f"Loaded {len(attractions_df)} attractions with review data")
    
    updated_df = extract_keywords(attractions_df)
    
    today = datetime.now().strftime("%Y%m%d")
    updated_df.to_csv(f"data/okinawa_tourism_with_keywords_{today}.csv", index=False, encoding="utf-8")
    print(f"Saved to data/okinawa_tourism_with_keywords_{today}.csv")

if __name__ == "__main__":
    main()
