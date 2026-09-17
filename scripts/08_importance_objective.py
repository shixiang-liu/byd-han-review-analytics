# pyright: basic, reportMissingImports=false
import pandas as pd
import numpy as np
import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
font_path = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
if os.path.exists(font_path):
    try:
        fm.fontManager.addfont(font_path)
        plt.rcParams["font.family"] = fm.FontProperties(fname=font_path).get_name()
    except Exception as e:
        print("Font load error:", e)
plt.rcParams["axes.unicode_minus"] = False

plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'WenQuanYi Micro Hei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

ASPECTS = ['space', 'driving', 'range', 'appearance', 'interior', 'value', 'smart']
ASPECTS_CN = ['空间', '驾驶感受', '续航', '外观', '内饰', '性价比', '智能化']

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LEGACY_ROOT = PROJECT_ROOT / "data" / "raw"


def _resolve_existing_path(*candidates: Path) -> Path:
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]

def cv_method(data):
    """变异系数法 (Coefficient of Variation)"""
    mean = data.mean()
    std = data.std()
    cv = std / mean
    weights = cv / cv.sum()
    return weights

def entropy_method(data):
    """熵权法 (Entropy Weight Method)"""
    # 极差标准化 (0.001 to avoid log(0))
    min_val = data.min()
    max_val = data.max()
    norm_data = (data - min_val) / (max_val - min_val)
    norm_data = norm_data.replace(0, 0.001)
    
    # 归一化
    p = norm_data / norm_data.sum(axis=0)
    
    # 计算熵
    n = len(data)
    e = - (p * np.log(p)).sum(axis=0) / np.log(n)
    
    # 计算权重
    d = 1 - e
    weights = d / d.sum()
    return weights

def critic_method(data):
    """CRITIC法"""
    # 极差标准化
    min_val = data.min()
    max_val = data.max()
    norm_data = (data - min_val) / (max_val - min_val)
    
    # 标准差 (对比性)
    std = norm_data.std()
    
    # 相关系数矩阵
    corr_matrix = norm_data.corr()
    
    # 冲突性
    conflict = len(data.columns) - corr_matrix.sum(axis=0)
    
    # 信息量
    c = std * conflict
    
    # 权重
    weights = c / c.sum()
    return weights

def run():
    print("Loading data for objective weight calculation...")
    data_path = _resolve_existing_path(
        PROJECT_ROOT / 'outputs' / 'data' / 'cleaned_reviews.csv',
        PROJECT_ROOT / 'outputs' / 'cleaned_reviews.csv',
        LEGACY_ROOT / 'outputs' / 'cleaned_reviews.csv',
    )
    df = pd.read_csv(data_path)
    
    cols = [f'score_{a}' for a in ASPECTS]
    data = df[cols].dropna()
    print(f"Valid rows for objective weights: {len(data)}/{len(df)}")
    
    # Calculate weights
    w_cv = cv_method(data).values
    w_entropy = entropy_method(data).values
    w_critic = critic_method(data).values
    
    # 综合权重 (均值融合)
    w_combined = (w_cv + w_entropy + w_critic) / 3
    
    res = pd.DataFrame({
        'aspect': ASPECTS,
        'aspect_cn': ASPECTS_CN,
        'w_cv': w_cv,
        'w_entropy': w_entropy,
        'w_critic': w_critic,
        'w_objective_combined': w_combined
    })
    
    res = res.sort_values('w_objective_combined', ascending=False)
    
    print("\nObjective Importance (Three-Method Fusion):")
    print(res[['aspect_cn', 'w_cv', 'w_entropy', 'w_critic', 'w_objective_combined']].to_string(index=False))
    
    out_path = PROJECT_ROOT / 'outputs' / 'tables' / 'importance_objective.csv'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(out_path, index=False, encoding='utf-8-sig')
    print(f"\nSaved objective weights to {out_path}")
    
    # Generate chart
    fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
    x = np.arange(len(res))
    width = 0.2
    
    ax.bar(x - width*1.5, res['w_cv'], width, label='变异系数法', color='#72B7B2')
    ax.bar(x - width*0.5, res['w_entropy'], width, label='熵权法', color='#F58518')
    ax.bar(x + width*0.5, res['w_critic'], width, label='CRITIC法', color='#4C78A8')
    ax.bar(x + width*1.5, res['w_objective_combined'], width, label='三法融合(综合)', color='#E45756')
    
    ax.set_xticks(x)
    ax.set_xticklabels(res['aspect_cn'], fontsize=12)
    ax.set_ylabel('客观权重 (Objective Weight)', fontsize=12)
    ax.set_title('三法融合：各维度客观重要度评估', fontsize=16, pad=15)
    ax.legend(fontsize=10)
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    fig_path = PROJECT_ROOT / 'figures' / 'fig_objective_weights.png'
    fig_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(fig_path)
    print(f"Saved figure to {fig_path}")

if __name__ == '__main__':
    run()
