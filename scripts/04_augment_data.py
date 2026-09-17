import pandas as pd
import numpy as np
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LEGACY_ROOT = PROJECT_ROOT / "data" / "raw"
OUTPUTS_DIR = PROJECT_ROOT / "outputs" / "tables"


def _resolve_existing_path(*candidates: Path) -> Path:
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]


CLEANED_CSV = _resolve_existing_path(
    PROJECT_ROOT / "outputs" / "data" / "cleaned_reviews.csv",
    PROJECT_ROOT / "outputs" / "cleaned_reviews.csv",
    LEGACY_ROOT / "outputs" / "cleaned_reviews.csv",
)

def classify_powertrain(model: str) -> str:
    m = str(model).upper()
    if 'DM-P' in m or 'DMP' in m or '四驱高性能' in m:
        return 'DM-p'
    if 'DM-I' in m or 'DMI' in m:
        return 'DM-i'
    if 'EV' in m:
        return 'EV'
    return 'Other'

def get_city_tier(city: str) -> str:
    tier1 = ['上海', '北京', '广州', '深圳']
    new_tier1 = ['成都', '重庆', '杭州', '武汉', '西安', '天津', '苏州', '南京', '郑州', '长沙', '东莞', '沈阳', '青岛', '合肥', '佛山']
    c = str(city)
    if any(x in c for x in tier1): return '一线城市'
    if any(x in c for x in new_tier1): return '新一线城市'
    return '二三线及其他'

def augment():
    df = pd.read_csv(CLEANED_CSV)
    df['powertrain'] = df['model'].apply(classify_powertrain)
    df['city_tier'] = df['purchase_city'].apply(get_city_tier)
    
    # 1. Monthly Sentiment Trend
    trend = df.groupby(['review_year', 'review_month']).agg({
        'score_space': 'mean',
        'score_driving': 'mean',
        'score_range': 'mean',
        'score_appearance': 'mean',
        'score_interior': 'mean',
        'score_value': 'mean',
        'score_smart': 'mean'
    }).reset_index()
    trend.to_csv(OUTPUTS_DIR / "aug_sentiment_trend.csv", index=False)
    
    # 2. Powertrain Comparison
    p_comp = df.groupby('powertrain').agg({
        'score_space': 'mean',
        'score_driving': 'mean',
        'score_range': 'mean',
        'score_appearance': 'mean',
        'score_interior': 'mean',
        'score_value': 'mean',
        'score_smart': 'mean',
        'username': 'count'
    }).rename(columns={'username': 'sample_size'}).reset_index()
    p_comp.to_csv(OUTPUTS_DIR / "aug_powertrain_comp.csv", index=False)
    
    # 3. City Tier Analysis
    c_comp = df.groupby('city_tier').agg({
        'score_range': 'mean',
        'score_value': 'mean',
        'score_smart': 'mean',
        'username': 'count'
    }).rename(columns={'username': 'sample_size'}).reset_index()
    c_comp.to_csv(OUTPUTS_DIR / "aug_city_tier_comp.csv", index=False)
    
    # 4. Price Correlation
    df['price_range'] = pd.cut(df['price'], bins=[0, 20, 25, 30, 100], labels=['20万以下', '20-25万', '25-30万', '30万以上'])
    price_comp = df.groupby('price_range', observed=False).agg({
        'score_value': 'mean',
        'score_interior': 'mean',
        'username': 'count'
    }).reset_index()
    price_comp.to_csv(OUTPUTS_DIR / "aug_price_comp.csv", index=False)
    
    print("Data augmentation complete.")

if __name__ == "__main__":
    augment()
