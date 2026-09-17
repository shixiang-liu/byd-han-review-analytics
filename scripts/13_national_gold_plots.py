import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = PROJECT_ROOT / "outputs" / "tables"
FIGURES_DIR = PROJECT_ROOT / "figures"
FIGURES_DIR.mkdir(exist_ok=True)

# Colors
DEEP_INDIGO = "#0D223F"
GOLD = "#C8A03D"
SLATE = "#34495E"
SOFT_GREY = "#95A5A6"

def set_style():
    font_path = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
    from matplotlib import font_manager
    font_manager.fontManager.addfont(font_path)
    prop = font_manager.FontProperties(fname=font_path)
    plt.rcParams["font.family"] = prop.get_name()
    sns.set_theme(style="whitegrid", font=prop.get_name())
    plt.rcParams["axes.prop_cycle"] = plt.cycler(color=[DEEP_INDIGO, GOLD, SLATE, "#E74C3C", "#2ECC71"])
    plt.rcParams["axes.unicode_minus"] = False

def plot_powertrain_radar():
    df = pd.read_csv(OUTPUTS_DIR / "aug_powertrain_comp.csv")
    aspects = ['score_space', 'score_driving', 'score_range', 'score_appearance', 'score_interior', 'score_value']
    labels = ['空间', '驾驶', '续航', '外观', '内饰', '价值']
    
    # Simple Bar Comparison for Radar-like data
    fig, ax = plt.subplots(figsize=(10, 6))
    df_melt = df.melt(id_vars='powertrain', value_vars=aspects)
    sns.barplot(data=df_melt, x='variable', y='value', hue='powertrain', palette=[DEEP_INDIGO, GOLD, SLATE])
    ax.set_ylim(4.0, 5.0)
    ax.set_title("各动力版本体验多维对比 (4.0-5.0分段)", fontsize=14, fontweight='bold', color=DEEP_INDIGO)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "national_powertrain_bar.png", dpi=300)
    plt.close()

def plot_city_tier():
    df = pd.read_csv(OUTPUTS_DIR / "aug_city_tier_comp.csv")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(data=df, x='score_range', y='score_smart', size='sample_size', hue='city_tier', sizes=(100, 1000), palette='viridis')
    ax.set_title("城市能级视角下的续航与智能满意度落位", fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "national_city_tier_bubble.png", dpi=300)
    plt.close()

if __name__ == "__main__":
    set_style()
    plot_powertrain_radar()
    plot_city_tier()
    print("National gold plots generated.")
