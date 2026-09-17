import pandas as pd
import numpy as np
import re
from pathlib import Path
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LEGACY_ROOT = PROJECT_ROOT / "data" / "raw"
OUTPUTS_DIR = PROJECT_ROOT / "outputs" / "tables"


def _resolve_existing_path(*candidates: Path) -> Path:
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]


INPUT_CSV = _resolve_existing_path(
    PROJECT_ROOT / "outputs" / "data" / "cleaned_reviews.csv",
    PROJECT_ROOT / "outputs" / "cleaned_reviews.csv",
    LEGACY_ROOT / "outputs" / "cleaned_reviews.csv",
)

ASPECTS = ["space", "driving", "range", "appearance", "interior", "value", "smart"]

# Pattern for Innovation Z
EXPECT_PAT = re.compile(r"(希望|期待|最好|至少|要是|能不能|如果能|要是能|建议)")
NEG_PAT = re.compile(r"(太差|不行|不足|拉胯|糟糕|失望|不满意|吐槽|缺陷|毛病)")

def compute_metrics():
    df = pd.read_csv(INPUT_CSV)
    
    # --- 1. Basic Stats & DML Importance (Placeholder or Load) ---
    # We already have dml_results.csv from previous runs or we can compute proxy if missing
    dml_path = OUTPUTS_DIR / "dml_results.csv"
    if dml_path.exists():
        dml_df = pd.read_csv(dml_path)
        # In dml_results.csv, aspects are already stripped of 'score_' prefix
        importance_map = {str(row['aspect']): row['theta'] for _, row in dml_df.iterrows()}
    else:
        # Fallback to simple correlation if DML missing
        importance_map = {a: df['score_'+a].corr(df[['score_'+x for x in ASPECTS]].mean(axis=1)) for a in ASPECTS}

    # --- 2. PRCA (Asymmetric Effects) ---
    prca_results = []
    y_overall = df[['score_'+a for a in ASPECTS]].mean(axis=1) # Synthetic overall satisfaction
    df['y_overall'] = y_overall
    
    for a in ASPECTS:
        score_col = 'score_' + a
        data = df[[score_col, 'y_overall']].dropna()
        if len(data) < 100: continue
        
        y = data['y_overall'].values
        val = data[score_col].values
        med = val.mean() # Changed from np.median(val) to handle severe right-skewness
        
        penalty = np.maximum(med - val, 0)
        reward = np.maximum(val - med, 0)
        
        # Simple Ridge to get asymmetric coefficients
        model = Ridge(alpha=1.0)
        X = np.column_stack([penalty, reward])
        model.fit(X, y)
        
        p_coef = abs(model.coef_[0]) # We expect penalty variable to have negative effect usually, 
                                     # but max(med-val,0) means as shortfall increases, Y decreases.
                                     # So coef will be negative. We take abs as "Penalty Weight".
        r_coef = max(model.coef_[1], 0) # Reward Weight (truncated to strictly non-negative)
        
        # Classification (Simplified)
        if p_coef > 1.5 * r_coef:
            cls = "Hygiene (基础型)"
        elif r_coef > 1.5 * p_coef:
            cls = "Delighter (魅力型)"
        else:
            cls = "Performance (期望型)"
        
        perf = val.mean()
        doi = r_coef * (5.0 - perf) / 5.0 # Opportunity to delight
        
        prca_results.append({
            "aspect": a,
            "penalty_weight": p_coef,
            "reward_weight": r_coef,
            "classification": cls,
            "performance": perf,
            "doi": doi
        })

    pd.DataFrame(prca_results).to_csv(OUTPUTS_DIR / "deep_prca_results.csv", index=False)

    # --- 3. IPIA (Innovation Z) ---
    ipia_results = []
    for a in ASPECTS:
        text_col = 'text_' + a
        score_col = 'score_' + a
        
        # Filter rows where aspect is mentioned
        subset = df[df[text_col].notna()]
        if len(subset) == 0:
            exp_rate = 0
            neg_rate = 0
        else:
            texts = subset[text_col].astype(str)
            exp_rate = texts.apply(lambda x: 1 if EXPECT_PAT.search(x) else 0).mean()
            neg_rate = texts.apply(lambda x: 1 if NEG_PAT.search(x) else 0).mean()
        
        perf = df[score_col].mean()
        # Scale performance to [0,1] for Z calculation
        P = (perf - 1) / 4.0
        gap = max(exp_rate - P, 0)
        z = 0.6 * gap + 0.4 * neg_rate
        
        ipia_results.append({
            "aspect": a,
            "importance": importance_map.get(a, 0),
            "performance": perf,
            "innovation_z": z,
            "expect_rate": exp_rate,
            "neg_rate": neg_rate
        })
    
    pd.DataFrame(ipia_results).to_csv(OUTPUTS_DIR / "deep_ipia_results.csv", index=False)
    print("Deep metrics computation complete.")

if __name__ == "__main__":
    compute_metrics()
