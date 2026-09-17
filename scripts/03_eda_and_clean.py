from __future__ import annotations

import warnings
from pathlib import Path
from typing import cast

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
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import font_manager


BASE_DIR = Path(__file__).resolve().parents[1]
LEGACY_BASE_DIR = BASE_DIR / "data" / "raw"


def _resolve_existing_path(*candidates: Path) -> Path:
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]


INPUT_PATH = _resolve_existing_path(
    BASE_DIR / "outputs" / "data" / "parsed_reviews.csv",
    BASE_DIR / "outputs" / "parsed_reviews.csv",
    LEGACY_BASE_DIR / "outputs" / "parsed_reviews.csv",
)
OUTPUT_PATH = BASE_DIR / "outputs" / "data" / "cleaned_reviews.csv"
FIGURES_DIR = BASE_DIR / "figures"

SCORE_COLS = [
    "score_space",
    "score_driving",
    "score_range",
    "score_appearance",
    "score_interior",
    "score_value",
    "score_smart",
]

TEXT_COLS = [
    "text_space",
    "text_driving",
    "text_range",
    "text_appearance",
    "text_interior",
    "text_value",
    "text_smart",
    "most_satisfied_text",
    "most_dissatisfied_text",
]

ASPECT_NAME_MAP = {
    "score_space": "空间",
    "score_driving": "驾驶感受",
    "score_range": "续航",
    "score_appearance": "外观",
    "score_interior": "内饰",
    "score_value": "性价比",
    "score_smart": "智能化",
    "text_space": "空间",
    "text_driving": "驾驶感受",
    "text_range": "续航",
    "text_appearance": "外观",
    "text_interior": "内饰",
    "text_value": "性价比",
    "text_smart": "智能化",
}

PALETTE = ["#4C78A8", "#F58518", "#E45756", "#72B7B2", "#54A24B", "#EECA3B", "#B279A2"]


def configure_plot_style() -> None:
    """Global plot styling with robust Chinese font handling.

    Note: seaborn.set_theme() may reset matplotlib rcParams, so we apply font
    configuration AFTER setting the theme.
    """

    # 1) Prefer explicit WQY font file (prevents tofu/blank squares)
    selected_font: str | None = None
    font_path_local = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
    if os.path.exists(font_path_local):
        try:
            fm.fontManager.addfont(font_path_local)
            selected_font = fm.FontProperties(fname=font_path_local).get_name()
        except Exception:
            selected_font = None

    # 2) Fallback to a font available in the environment
    if not selected_font:
        preferred_fonts = [
            "WenQuanYi Zen Hei",
            "WenQuanYi Micro Hei",
            "SimHei",
            "Noto Sans CJK SC",
            "Microsoft YaHei",
            "AR PL KaitiM GB",
        ]
        available_fonts = {f.name for f in font_manager.fontManager.ttflist}
        selected_font = next(
            (name for name in preferred_fonts if name in available_fonts),
            "DejaVu Sans",
        )

    warnings.filterwarnings("ignore", message="Glyph .* missing from font", category=UserWarning)
    sns.set_theme(style="whitegrid")

    # Apply rcParams AFTER seaborn theme to avoid resets
    plt.rcParams["font.family"] = selected_font
    plt.rcParams["font.sans-serif"] = [selected_font, "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["grid.color"] = "#D9D9D9"
    plt.rcParams["grid.linestyle"] = ":"
    plt.rcParams["grid.linewidth"] = 0.8


def read_reviews(path: Path) -> pd.DataFrame:
    for enc in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("unknown", b"", 0, 1, f"无法读取文件编码: {path}")


def clean_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in TEXT_COLS:
        if col not in out.columns:
            continue
        out[col] = out[col].astype("string")
        out[col] = out[col].str.replace(r"\s+", " ", regex=True).str.strip()
        out[col] = out[col].replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
    return out


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["date_parsed"] = pd.to_datetime(out["date"], errors="coerce")
    out["review_year"] = out["date_parsed"].dt.year
    out["review_month"] = out["date_parsed"].dt.month
    return out


def add_total_text(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    all_text_cols = [
        "text_space",
        "text_driving",
        "text_range",
        "text_appearance",
        "text_interior",
        "text_value",
        "text_smart",
        "most_satisfied_text",
        "most_dissatisfied_text",
    ]

    def concat_row(row: pd.Series) -> str:
        values = [str(v).strip() for v in row if pd.notna(v) and str(v).strip()]
        return " ".join(values)

    out["total_text"] = out[all_text_cols].apply(concat_row, axis=1)
    out["total_text"] = out["total_text"].replace({"": pd.NA})
    return out


def drop_all_missing_scores(df: pd.DataFrame) -> pd.DataFrame:
    return df.dropna(subset=SCORE_COLS, how="all").copy()


def save_score_distribution(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(3, 3, figsize=(16, 12))
    axes = axes.flatten()
    score_levels = [1, 2, 3, 4, 5]
    blues = sns.color_palette("Blues", n_colors=5)

    for idx, col in enumerate(SCORE_COLS):
        ax = axes[idx]
        score_series = cast(pd.Series, pd.to_numeric(df[col], errors="coerce"))
        counts = score_series.value_counts(dropna=True).reindex(score_levels, fill_value=0)
        y_labels = [f"{s}分" for s in score_levels]
        bars = ax.barh(y_labels, counts.values, color=blues)
        n = int(score_series.notna().sum())
        ax.set_title(f"{ASPECT_NAME_MAP[col]}评分分布 (N={n})")
        ax.set_xlabel("评论数量")
        ax.set_ylabel("评分")
        ax.grid(axis="x", linestyle=":", alpha=0.7)

        for bar, val in zip(bars, counts.values):
            ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height() / 2, str(int(val)), va="center", fontsize=9)

    for idx in range(len(SCORE_COLS), len(axes)):
        axes[idx].axis("off")

    fig.suptitle("七大维度评分分布", fontsize=16)
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.97))
    fig.savefig(FIGURES_DIR / "fig_score_distribution.png", dpi=200)
    plt.close(fig)


def save_missing_values(df: pd.DataFrame) -> None:
    missing_pct = df.isna().mean().sort_values(ascending=False) * 100
    fig, ax = plt.subplots(figsize=(14, 8))
    cmap = plt.get_cmap("YlOrRd")
    normalized = (missing_pct.values - missing_pct.values.min()) / (
        (missing_pct.values.max() - missing_pct.values.min()) + 1e-9
    )
    colors = [cmap(v) for v in normalized]
    bars = ax.bar(missing_pct.index, missing_pct.values, color=colors)
    ax.set_title("各字段缺失率")
    ax.set_xlabel("字段")
    ax.set_ylabel("缺失率(%)")
    ax.tick_params(axis="x", labelrotation=60)
    for label in ax.get_xticklabels():
        label.set_horizontalalignment("right")
    ax.grid(axis="y", linestyle=":", alpha=0.7)
    for bar, val in zip(bars, missing_pct.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.8, f"{val:.1f}%", ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_missing_values.png", dpi=200)
    plt.close(fig)


def save_score_heatmap(df: pd.DataFrame) -> None:
    score_df = cast(pd.DataFrame, df[SCORE_COLS].apply(pd.to_numeric, errors="coerce"))
    corr = score_df.corr(method="pearson")
    rename_map = {col: ASPECT_NAME_MAP[col] for col in SCORE_COLS}
    corr = corr.rename(index=rename_map, columns=rename_map)
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        linewidths=0.5,
        square=True,
        ax=ax,
    )
    ax.set_title("七大维度评分相关性热力图")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_score_heatmap.png", dpi=200)
    plt.close(fig)


def save_score_boxplot(df: pd.DataFrame) -> None:
    long_df = df[SCORE_COLS].melt(var_name="aspect", value_name="score").dropna()
    long_df["aspect"] = long_df["aspect"].replace(ASPECT_NAME_MAP)
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.boxplot(data=long_df, x="aspect", y="score", hue="aspect", palette=PALETTE, legend=False, ax=ax)
    ax.set_title("七大维度评分箱线图")
    ax.set_xlabel("维度")
    ax.set_ylabel("评分")
    ax.set_ylim(0.5, 5.5)
    ax.grid(axis="y", linestyle=":", alpha=0.7)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_score_boxplot.png", dpi=200)
    plt.close(fig)


def save_model_distribution(df: pd.DataFrame) -> None:
    top_models = df["model"].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(13, 8))
    model_colors = sns.color_palette(PALETTE, n_colors=len(top_models))
    sns.barplot(x=top_models.values, y=top_models.index, hue=top_models.index, palette=model_colors, legend=False, ax=ax)
    ax.set_title("车型/配置出现频次 Top 10")
    ax.set_xlabel("评论数量")
    ax.set_ylabel("车型")
    ax.grid(axis="x", linestyle=":", alpha=0.7)
    for i, val in enumerate(top_models.values):
        ax.text(val + 2, i, str(int(val)), va="center")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_model_distribution.png", dpi=200)
    plt.close(fig)


def save_review_timeline(df: pd.DataFrame) -> None:
    monthly = (
        df["date_parsed"]
        .dropna()
        .dt.to_period("M")
        .value_counts()
        .sort_index()
    )
    timeline = monthly.to_timestamp()
    start_label = f"{timeline.index.min().year}年{timeline.index.min().month}月" if len(timeline) else ""
    end_label = f"{timeline.index.max().year}年{timeline.index.max().month}月" if len(timeline) else ""
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.plot(timeline.index, timeline.values, color=PALETTE[0], marker="o", linewidth=2)
    ax.set_title(f"评论数量时间趋势（月度，{start_label}—{end_label}）")
    ax.set_xlabel("月份")
    ax.set_ylabel("评论数量")
    ax.grid(axis="both", linestyle=":", alpha=0.7)
    fig.autofmt_xdate(rotation=45)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_review_timeline.png", dpi=200)
    plt.close(fig)


def save_text_length_distribution(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(3, 3, figsize=(16, 12))
    axes = axes.flatten()

    for idx, col in enumerate(["text_space", "text_driving", "text_range", "text_appearance", "text_interior", "text_value", "text_smart"]):
        ax = axes[idx]
        lengths = df[col].fillna("").astype(str).str.len()
        lengths = lengths[lengths > 0]
        color = PALETTE[idx % len(PALETTE)]
        ax.hist(lengths, bins=30, color=color, alpha=0.8, edgecolor="white")
        if not lengths.empty:
            mean_val = lengths.mean()
            ax.axvline(mean_val, color="#333333", linestyle="--", linewidth=1.5, label=f"均值={mean_val:.1f}")
            ax.legend(loc="upper right", fontsize=8)
        ax.set_title(f"{ASPECT_NAME_MAP[col]}文本长度分布")
        ax.set_xlabel("文本长度（字符）")
        ax.set_ylabel("频数")
        ax.grid(axis="y", linestyle=":", alpha=0.7)

    for idx in range(7, len(axes)):
        axes[idx].axis("off")

    fig.suptitle("七大维度文本长度分布", fontsize=16)
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.97))
    fig.savefig(FIGURES_DIR / "fig_text_length_distribution.png", dpi=200)
    plt.close(fig)


def save_price_distribution(df: pd.DataFrame) -> None:
    price_series = cast(pd.Series, pd.to_numeric(df["price"], errors="coerce"))
    prices = price_series.dropna()
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.hist(prices, bins=35, color=PALETTE[1], alpha=0.85, edgecolor="white")
    mean_price = prices.mean() if not prices.empty else np.nan
    if not np.isnan(mean_price):
        ax.axvline(mean_price, color="#333333", linestyle="--", linewidth=1.5, label=f"均值={mean_price:.2f}万元")
        ax.legend(loc="upper right")
    ax.set_title("裸车价格分布（万元）")
    ax.set_xlabel("价格（万元）")
    ax.set_ylabel("频数")
    ax.grid(axis="y", linestyle=":", alpha=0.7)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_price_distribution.png", dpi=200)
    plt.close(fig)


def generate_all_figures(df: pd.DataFrame) -> None:
    save_score_distribution(df)
    save_missing_values(df)
    save_score_heatmap(df)
    save_score_boxplot(df)
    save_model_distribution(df)
    save_review_timeline(df)
    save_text_length_distribution(df)
    save_price_distribution(df)


def main() -> None:
    configure_plot_style()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    raw_df = read_reviews(INPUT_PATH)
    cleaned_df = clean_text_columns(raw_df)
    cleaned_df = add_time_features(cleaned_df)
    cleaned_df = drop_all_missing_scores(cleaned_df)
    cleaned_df = add_total_text(cleaned_df)

    generate_all_figures(cleaned_df)

    export_df = cleaned_df.drop(columns=["date_parsed"])
    export_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print("EDA与清洗完成")
    print(f"原始数据行数: {len(raw_df)}")
    print(f"清洗后行数: {len(cleaned_df)}")
    print(f"删除全缺失评分行数: {len(raw_df) - len(cleaned_df)}")
    print(f"输出文件: {OUTPUT_PATH}")
    print(f"图表目录: {FIGURES_DIR}")


if __name__ == "__main__":
    main()
