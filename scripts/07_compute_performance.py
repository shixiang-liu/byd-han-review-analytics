#!/usr/bin/env python3
"""
Phase 4: Performance (绩效) Calculation
========================================
Fuses structural scores with BERT sentiment scores:
    P_j = α × normalize(mean_score_j) + (1-α) × normalize(mean_sentiment_j)

Outputs:
    outputs/performance_scores.csv  — per-aspect Performance with α sensitivity
    figures/fig_performance_fusion.png
    figures/fig_alpha_sensitivity.png
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
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

# ── Chinese font ──────────────────────────────────────────────
plt.rcParams['font.sans-serif'] = ['SimHei', 'WenQuanYi Zen Hei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ── Constants ─────────────────────────────────────────────────
ASPECTS = ['space', 'driving', 'range', 'appearance', 'interior', 'value', 'smart']
ASPECTS_CN = ['空间', '驾驶感受', '续航', '外观', '内饰', '性价比', '智能化']
PALETTE = ['#4C78A8', '#F58518', '#E45756', '#72B7B2', '#54A24B', '#EECA3B', '#B279A2']
ALPHA_DEFAULT = 0.5
ALPHA_RANGE = [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, 'outputs', 'tables')
FIG_DIR = os.path.join(BASE_DIR, 'figures')


def min_max_normalize(series):
    """Min-max normalize a Series to [0, 1]."""
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series(0.5, index=series.index)
    return (series - mn) / (mx - mn)


def compute_performance(alpha=ALPHA_DEFAULT):
    """
    Compute per-aspect Performance score.
    
    Returns DataFrame with columns: aspect, aspect_cn, score_mean, sentiment_mean,
                                     score_norm, sentiment_norm, performance
    """
    # Load sentiment scores (has both original scores and sentiment)
    sent_path = os.path.join(OUT_DIR, 'sentiment_scores.csv')
    if not os.path.exists(sent_path):
        print(f"ERROR: {sent_path} not found. Run sentiment_analysis.py first.")
        sys.exit(1)
    
    df = pd.read_csv(sent_path, encoding='utf-8-sig')
    
    results = []
    for asp, asp_cn in zip(ASPECTS, ASPECTS_CN):
        score_col = f'score_{asp}'
        sent_col = f'sent_{asp}'
        
        score_mean = df[score_col].mean()  # mean of 1-5 scores
        sent_mean = df[sent_col].mean()    # mean of 0-1 sentiment
        
        n_score = df[score_col].notna().sum()
        n_sent = df[sent_col].notna().sum()
        
        results.append({
            'aspect': asp,
            'aspect_cn': asp_cn,
            'score_mean': score_mean,
            'sentiment_mean': sent_mean,
            'n_score': n_score,
            'n_sentiment': n_sent,
        })
    
    res = pd.DataFrame(results)
    
    # Normalize both to [0, 1]
    res['score_norm'] = min_max_normalize(res['score_mean'])
    res['sentiment_norm'] = min_max_normalize(res['sentiment_mean'])
    
    # Fuse
    res['performance'] = alpha * res['score_norm'] + (1 - alpha) * res['sentiment_norm']
    
    return res


def alpha_sensitivity_analysis():
    """Compute Performance for each α in ALPHA_RANGE."""
    all_results = []
    for a in ALPHA_RANGE:
        res = compute_performance(alpha=a)
        res['alpha'] = a
        all_results.append(res)
    return pd.concat(all_results, ignore_index=True)


def plot_performance_fusion(res, alpha):
    """Bar chart comparing score_norm, sentiment_norm, and fused performance."""
    fig, ax = plt.subplots(figsize=(12, 7))
    
    x = np.arange(len(ASPECTS_CN))
    width = 0.25
    
    bars1 = ax.bar(x - width, res['score_norm'], width, label='评分绩效 (归一化)',
                   color='#4C78A8', alpha=0.85)
    bars2 = ax.bar(x, res['sentiment_norm'], width, label='情感绩效 (归一化)',
                   color='#F58518', alpha=0.85)
    bars3 = ax.bar(x + width, res['performance'], width, label=f'融合绩效 (α={alpha})',
                   color='#54A24B', alpha=0.85)
    
    ax.set_xlabel('产品属性维度', fontsize=13)
    ax.set_ylabel('绩效得分 (归一化)', fontsize=13)
    ax.set_title('比亚迪汉 各维度绩效评估：评分 vs 情感 vs 融合', fontsize=15, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(ASPECTS_CN, fontsize=12)
    ax.legend(fontsize=11, loc='upper right')
    ax.set_ylim(0, 1.15)
    ax.grid(axis='y', linestyle=':', alpha=0.4)
    
    # Add value labels
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            h = bar.get_height()
            ax.annotate(f'{h:.2f}', xy=(bar.get_x() + bar.get_width() / 2, h),
                       xytext=(0, 3), textcoords='offset points',
                       ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    path = os.path.join(FIG_DIR, 'fig_performance_fusion.png')
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_alpha_sensitivity(sens_df):
    """Line chart showing how each aspect's Performance changes with α."""
    fig, ax = plt.subplots(figsize=(12, 7))
    
    for i, (asp, asp_cn) in enumerate(zip(ASPECTS, ASPECTS_CN)):
        subset = sens_df[sens_df['aspect'] == asp]
        ax.plot(subset['alpha'], subset['performance'], '-o',
                color=PALETTE[i], label=asp_cn, linewidth=2, markersize=6)
    
    ax.set_xlabel('融合权重 α (1=纯评分, 0=纯情感)', fontsize=13)
    ax.set_ylabel('绩效得分', fontsize=13)
    ax.set_title('融合权重 α 对各维度绩效的影响（敏感性分析）', fontsize=15, fontweight='bold')
    ax.legend(fontsize=11, bbox_to_anchor=(1.02, 1), loc='upper left')
    ax.grid(linestyle=':', alpha=0.4)
    ax.set_xticks(ALPHA_RANGE)
    ax.axvline(x=ALPHA_DEFAULT, color='grey', linestyle='--', alpha=0.5, label=f'α={ALPHA_DEFAULT}')
    
    plt.tight_layout()
    path = os.path.join(FIG_DIR, 'fig_alpha_sensitivity.png')
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {path}")


if __name__ == '__main__':
    os.makedirs(FIG_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    
    print("=" * 60)
    print("Phase 4: Performance (绩效) Calculation")
    print("=" * 60)
    
    # Main computation with default alpha
    print(f"\n[1/4] Computing Performance (α={ALPHA_DEFAULT})...")
    res = compute_performance(alpha=ALPHA_DEFAULT)
    
    print("\n  Per-aspect Performance:")
    print("  " + "-" * 75)
    print(f"  {'维度':<8} {'评分均值':>8} {'情感均值':>8} {'评分(归一)':>10} {'情感(归一)':>10} {'融合P':>8}")
    print("  " + "-" * 75)
    for _, r in res.iterrows():
        print(f"  {r['aspect_cn']:<8} {r['score_mean']:>8.3f} {r['sentiment_mean']:>8.3f} "
              f"{r['score_norm']:>10.3f} {r['sentiment_norm']:>10.3f} {r['performance']:>8.3f}")
    
    # Save
    out_path = os.path.join(OUT_DIR, 'performance_scores.csv')
    res.to_csv(out_path, index=False, encoding='utf-8-sig')
    print(f"\n  Saved: {out_path}")
    
    # Figures
    print("\n[2/4] Generating Performance fusion figure...")
    plot_performance_fusion(res, ALPHA_DEFAULT)
    
    # Sensitivity analysis
    print("\n[3/4] Running α sensitivity analysis...")
    sens_df = alpha_sensitivity_analysis()
    sens_path = os.path.join(OUT_DIR, 'alpha_sensitivity.csv')
    sens_df.to_csv(sens_path, index=False, encoding='utf-8-sig')
    print(f"  Saved: {sens_path}")
    
    print("\n[4/4] Generating sensitivity figure...")
    plot_alpha_sensitivity(sens_df)
    
    print("\n" + "=" * 60)
    print("Phase 4 complete.")
    print("=" * 60)
