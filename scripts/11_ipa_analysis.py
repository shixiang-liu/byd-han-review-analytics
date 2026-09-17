#!/usr/bin/env python3
"""
Phase 8: IPA Quadrant Analysis
================================
Combines Performance (P) and Importance (I) into IPA quadrant chart.
Generates decision recommendations per quadrant.

Outputs:
    outputs/ipa_results.csv
    figures/fig_ipa_quadrant.png
    figures/fig_ipa_radar.png
    figures/fig_ipa_priority_bar.png
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
from matplotlib.patches import FancyBboxPatch
import matplotlib.patches as mpatches

# ── Chinese font ──────────────────────────────────────────────
plt.rcParams['font.sans-serif'] = ['SimHei', 'WenQuanYi Zen Hei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ── Constants ─────────────────────────────────────────────────
ASPECTS = ['space', 'driving', 'range', 'appearance', 'interior', 'value', 'smart']
ASPECTS_CN = ['空间', '驾驶感受', '续航', '外观', '内饰', '性价比', '智能化']
PALETTE = ['#4C78A8', '#F58518', '#E45756', '#72B7B2', '#54A24B', '#EECA3B', '#B279A2']

# IPA Quadrant definitions
QUADRANT_NAMES = {
    'Q1': '优势保持区',       # High I, High P — Keep up the good work
    'Q2': '重点改进区',       # High I, Low P — Concentrate here  
    'Q3': '次要改进区',       # Low I, Low P — Low priority
    'Q4': '过度投入区',       # Low I, High P — Possible overkill
}

QUADRANT_COLORS = {
    'Q1': '#54A24B',  # Green — good
    'Q2': '#E45756',  # Red — urgent
    'Q3': '#EECA3B',  # Yellow — low priority
    'Q4': '#4C78A8',  # Blue — over-invested
}

QUADRANT_ACTIONS = {
    'Q1': '继续保持现有水平，作为品牌竞争优势进行宣传',
    'Q2': '【紧急】需要重点投入资源改进，这些维度对用户满意度影响大但表现差',
    'Q3': '可适当关注，但不需要优先投入资源',
    'Q4': '可考虑适当调整资源配置，将过度投入的资源转移到重点改进区',
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, 'outputs', 'tables')
FIG_DIR = os.path.join(BASE_DIR, 'figures')


def load_ipa_data():
    """Load Performance and Importance scores, merge into IPA DataFrame."""
    perf_path = os.path.join(OUT_DIR, 'performance_scores.csv')
    imp_path = os.path.join(OUT_DIR, 'importance_scores.csv')
    
    for p, name in [(perf_path, 'Performance'), (imp_path, 'Importance')]:
        if not os.path.exists(p):
            print(f"ERROR: {p} not found. Run {name} calculation first.")
            sys.exit(1)
    
    perf = pd.read_csv(perf_path, encoding='utf-8-sig')
    imp = pd.read_csv(imp_path, encoding='utf-8-sig')
    
    # Merge on aspect
    ipa = perf[['aspect', 'aspect_cn', 'performance']].merge(
        imp[['aspect', 'combined_importance']], on='aspect'
    )
    ipa.rename(columns={'performance': 'P', 'combined_importance': 'I'}, inplace=True)
    
    return ipa


def assign_quadrants(ipa):
    """Assign each aspect to an IPA quadrant based on mean crosshairs."""
    p_mean = ipa['P'].mean()
    i_mean = ipa['I'].mean()
    
    def classify(row):
        if row['I'] >= i_mean and row['P'] >= p_mean:
            return 'Q1'
        elif row['I'] >= i_mean and row['P'] < p_mean:
            return 'Q2'
        elif row['I'] < i_mean and row['P'] < p_mean:
            return 'Q3'
        else:
            return 'Q4'
    
    ipa['quadrant'] = ipa.apply(classify, axis=1)
    ipa['quadrant_name'] = ipa['quadrant'].map(QUADRANT_NAMES)
    ipa['action'] = ipa['quadrant'].map(QUADRANT_ACTIONS)
    
    # Priority score: higher importance + lower performance = higher priority
    ipa['priority_score'] = ipa['I'] * (1 - ipa['P'])
    ipa['priority_rank'] = ipa['priority_score'].rank(ascending=False).astype(int)
    
    return ipa, p_mean, i_mean


def plot_ipa_quadrant(ipa, p_mean, i_mean):
    """Publication-quality IPA quadrant scatter plot."""
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Background quadrant colors (very light)
    x_min, x_max = ipa['I'].min() - 0.08, ipa['I'].max() + 0.08
    y_min, y_max = ipa['P'].min() - 0.08, ipa['P'].max() + 0.08
    
    # Draw quadrant backgrounds
    ax.axhspan(p_mean, y_max + 0.1, xmin=0, xmax=1, alpha=0.06, color='#54A24B', zorder=0)
    ax.axhspan(y_min - 0.1, p_mean, xmin=0, xmax=1, alpha=0.06, color='#EECA3B', zorder=0)
    
    # Crosshairs
    ax.axhline(y=p_mean, color='#666666', linestyle='--', linewidth=1.5, alpha=0.7, zorder=1)
    ax.axvline(x=i_mean, color='#666666', linestyle='--', linewidth=1.5, alpha=0.7, zorder=1)
    
    # Plot points
    for idx, row in ipa.iterrows():
        color = QUADRANT_COLORS[row['quadrant']]
        ax.scatter(row['I'], row['P'], c=color, s=250, zorder=5,
                  edgecolors='white', linewidth=2, alpha=0.9)
        
        # Label with Chinese name + slight offset
        offset_x = 0.015
        offset_y = 0.015
        ax.annotate(row['aspect_cn'], (row['I'], row['P']),
                   xytext=(row['I'] + offset_x, row['P'] + offset_y),
                   fontsize=13, fontweight='bold', color=color,
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                            edgecolor=color, alpha=0.85),
                   zorder=6)
    
    # Quadrant labels
    label_kw = dict(fontsize=12, alpha=0.6, ha='center', va='center', style='italic')
    ax.text(i_mean + (x_max - i_mean) / 2, p_mean + (y_max - p_mean) / 2,
            'Ⅰ 优势保持区\n(继续保持)', color='#54A24B', **label_kw)
    ax.text(i_mean + (x_max - i_mean) / 2, p_mean - (p_mean - y_min) / 2,
            'Ⅱ 重点改进区\n(集中资源)', color='#E45756', **label_kw)
    ax.text(i_mean - (i_mean - x_min) / 2, p_mean - (p_mean - y_min) / 2,
            'Ⅲ 次要改进区\n(低优先级)', color='#999999', **label_kw)
    ax.text(i_mean - (i_mean - x_min) / 2, p_mean + (y_max - p_mean) / 2,
            'Ⅳ 过度投入区\n(可调整)', color='#4C78A8', **label_kw)
    
    ax.set_xlabel('重要性 (Importance)', fontsize=14, fontweight='bold')
    ax.set_ylabel('绩效 (Performance)', fontsize=14, fontweight='bold')
    ax.set_title('比亚迪汉 IPA 分析：重要性-绩效矩阵', fontsize=16, fontweight='bold', pad=15)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.grid(linestyle=':', alpha=0.3)
    
    # Legend for quadrants
    legend_patches = [mpatches.Patch(color=QUADRANT_COLORS[q], label=f'{q}: {QUADRANT_NAMES[q]}')
                      for q in ['Q1', 'Q2', 'Q3', 'Q4']]
    ax.legend(handles=legend_patches, loc='lower right', fontsize=10, framealpha=0.9)
    
    plt.tight_layout()
    path = os.path.join(FIG_DIR, 'fig_ipa_quadrant.png')
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_ipa_radar(ipa):
    """Radar chart showing P and I together."""
    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True))
    
    n = len(ASPECTS_CN)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]
    
    p_vals = ipa['P'].tolist() + [ipa['P'].iloc[0]]
    i_vals = ipa['I'].tolist() + [ipa['I'].iloc[0]]
    
    ax.plot(angles, p_vals, 'o-', color='#4C78A8', linewidth=2.5, label='绩效 (Performance)', markersize=8)
    ax.fill(angles, p_vals, alpha=0.15, color='#4C78A8')
    ax.plot(angles, i_vals, 's-', color='#E45756', linewidth=2.5, label='重要性 (Importance)', markersize=8)
    ax.fill(angles, i_vals, alpha=0.15, color='#E45756')
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(ASPECTS_CN, fontsize=12)
    ax.set_ylim(0, 1.05)
    ax.set_title('比亚迪汉 绩效-重要性 雷达图', fontsize=15, fontweight='bold', pad=25)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=11)
    
    plt.tight_layout()
    path = os.path.join(FIG_DIR, 'fig_ipa_radar.png')
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_priority_bar(ipa):
    """Horizontal bar chart: improvement priority ranking."""
    sorted_ipa = ipa.sort_values('priority_score', ascending=True)
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    colors = [QUADRANT_COLORS[q] for q in sorted_ipa['quadrant']]
    bars = ax.barh(sorted_ipa['aspect_cn'], sorted_ipa['priority_score'],
                   color=colors, edgecolor='white', linewidth=1.5, height=0.6)
    
    for bar, (_, row) in zip(bars, sorted_ipa.iterrows()):
        w = bar.get_width()
        ax.text(w + 0.005, bar.get_y() + bar.get_height() / 2,
                f'{w:.3f} ({row["quadrant_name"]})',
                va='center', fontsize=11, color='#333333')
    
    ax.set_xlabel('改进优先级得分 (Importance × (1 - Performance))', fontsize=13)
    ax.set_title('比亚迪汉 产品改进优先级排序', fontsize=15, fontweight='bold')
    ax.grid(axis='x', linestyle=':', alpha=0.4)
    ax.invert_yaxis()  # Highest priority on top — wait, sorted ascending so reverse
    
    # Actually, we want highest on top
    sorted_ipa2 = ipa.sort_values('priority_score', ascending=False)
    ax.clear()
    colors2 = [QUADRANT_COLORS[q] for q in sorted_ipa2['quadrant']]
    bars2 = ax.barh(range(len(sorted_ipa2)), sorted_ipa2['priority_score'].values,
                    color=colors2, edgecolor='white', linewidth=1.5, height=0.6)
    ax.set_yticks(range(len(sorted_ipa2)))
    ax.set_yticklabels(sorted_ipa2['aspect_cn'].values, fontsize=12)
    
    for bar, (_, row) in zip(bars2, sorted_ipa2.iterrows()):
        w = bar.get_width()
        ax.text(w + 0.005, bar.get_y() + bar.get_height() / 2,
                f'{w:.3f} ({row["quadrant_name"]})',
                va='center', fontsize=11, color='#333333')
    
    ax.set_xlabel('改进优先级得分 (Importance × (1 - Performance))', fontsize=13)
    ax.set_title('比亚迪汉 产品改进优先级排序', fontsize=15, fontweight='bold')
    ax.grid(axis='x', linestyle=':', alpha=0.4)
    
    plt.tight_layout()
    path = os.path.join(FIG_DIR, 'fig_ipa_priority_bar.png')
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {path}")


if __name__ == '__main__':
    os.makedirs(FIG_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    
    print("=" * 60)
    print("Phase 8: IPA Quadrant Analysis")
    print("=" * 60)
    
    # Load data
    print("\n[1/5] Loading Performance and Importance data...")
    ipa = load_ipa_data()
    
    # Assign quadrants
    print("[2/5] Assigning IPA quadrants...")
    ipa, p_mean, i_mean = assign_quadrants(ipa)
    
    # Print results
    print(f"\n  Crosshairs: P_mean={p_mean:.3f}, I_mean={i_mean:.3f}")
    print("\n  IPA Results:")
    print("  " + "-" * 80)
    print(f"  {'维度':<8} {'绩效P':>8} {'重要性I':>8} {'象限':>10} {'优先级':>8} {'排名':>4}")
    print("  " + "-" * 80)
    for _, r in ipa.iterrows():
        print(f"  {r['aspect_cn']:<8} {r['P']:>8.3f} {r['I']:>8.3f} "
              f"{r['quadrant_name']:>10} {r['priority_score']:>8.3f} {r['priority_rank']:>4}")
    
    # Decision recommendations
    print("\n  决策建议:")
    print("  " + "-" * 80)
    for _, r in ipa.sort_values('priority_rank').iterrows():
        print(f"  [{r['priority_rank']}] {r['aspect_cn']} ({r['quadrant_name']}): {r['action']}")
    
    # Save
    out_path = os.path.join(OUT_DIR, 'ipa_results.csv')
    ipa.to_csv(out_path, index=False, encoding='utf-8-sig')
    print(f"\n  Saved: {out_path}")
    
    # Figures
    print("\n[3/5] Generating IPA quadrant plot...")
    plot_ipa_quadrant(ipa, p_mean, i_mean)
    
    print("[4/5] Generating IPA radar chart...")
    plot_ipa_radar(ipa)
    
    print("[5/5] Generating priority ranking chart...")
    plot_priority_bar(ipa)
    
    print("\n" + "=" * 60)
    print("Phase 8 complete.")
    print("=" * 60)
