# pyright: reportGeneralTypeIssues=false, reportMissingTypeStubs=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportAny=false, reportAttributeAccessIssue=false, reportMissingTypeArgument=false, reportUnreachable=false, reportImplicitStringConcatenation=false, reportOperatorIssue=false, reportReturnType=false, reportUnusedCallResult=false, reportUnknownParameterType=false
from pathlib import Path

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

# Chinese font setup
plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
import numpy as np
import pandas as pd
import shap
from scipy.stats import pearsonr
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from xgboost import XGBRegressor


ASPECT_COLS = {
    "space": "score_space",
    "driving": "score_driving",
    "range": "score_range",
    "appearance": "score_appearance",
    "interior": "score_interior",
    "value": "score_value",
    "smart": "score_smart",
}

ASPECT_CN = {
    "space": "空间",
    "driving": "驾驶感受",
    "range": "续航",
    "appearance": "外观",
    "interior": "内饰",
    "value": "性价比",
    "smart": "智能化",
}

PALETTE = [
    "#4C78A8",
    "#F58518",
    "#E45756",
    "#72B7B2",
    "#54A24B",
    "#EECA3B",
    "#B279A2",
]


def normalize_01(arr: np.ndarray) -> np.ndarray:
    arr = np.asarray(arr, dtype=float)
    max_val = np.nanmax(arr)
    min_val = np.nanmin(arr)
    if np.isclose(max_val, min_val):
        return np.zeros_like(arr)
    return (arr - min_val) / (max_val - min_val)


def partial_corr_manual(df: pd.DataFrame) -> dict:
    """
    Compute partial correlation for each aspect using leave-one-out y.
    For aspect j: y_j = mean of all OTHER scores (excluding score_j).
    Then partial_corr(score_j, y_j | controls) where controls are metadata.
    This avoids the circularity of y_overall = mean(all scores).
    """
    partial_corr = {}
    all_score_cols = list(ASPECT_COLS.values())

    for key, score_col in ASPECT_COLS.items():
        other_cols = [c for c in all_score_cols if c != score_col]
        sub = df[[score_col] + other_cols].dropna().copy()

        if len(sub) < 10:
            partial_corr[key] = np.nan
            continue

        # Leave-one-out y: mean of all OTHER aspect scores
        y_loo = sub[other_cols].mean(axis=1).values
        t = sub[score_col].values

        # Controls: the other individual scores (not their mean)
        x_controls = sub[other_cols].values

        model_t = LinearRegression().fit(x_controls, t)
        model_y = LinearRegression().fit(x_controls, y_loo)

        resid_t = t - model_t.predict(x_controls)
        resid_y = y_loo - model_y.predict(x_controls)

        if np.isclose(np.std(resid_t), 0.0) or np.isclose(np.std(resid_y), 0.0):
            partial_corr[key] = np.nan
            continue

        corr, _ = pearsonr(resid_t, resid_y)
        partial_corr[key] = corr

    return partial_corr


def main() -> None:
    plt.rcParams["font.sans-serif"] = ["SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    root = Path(__file__).resolve().parents[1]
    data_path = root / "outputs" / "data" / "cleaned_reviews.csv"
    out_dir = root / "outputs" / "tables"
    fig_dir = root / "outputs" / "tables"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(data_path, encoding="utf-8-sig")

    score_cols = list(ASPECT_COLS.values())
    y_col = "y_overall"
    df[y_col] = df[score_cols].mean(axis=1, skipna=True)
    df = df.dropna(subset=[y_col]).copy()

    X_raw = df[score_cols].copy()
    y = df[y_col].values

    imputer = SimpleImputer(strategy="median")
    X_imputed = imputer.fit_transform(X_raw)

    model = XGBRegressor(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.1,
        random_state=42,
    )
    model.fit(X_imputed, y)

    pred = model.predict(X_imputed)
    r2 = r2_score(y, pred)
    rmse = np.sqrt(mean_squared_error(y, pred))

    print("=== XGBoost model performance ===")
    print(f"R2: {r2:.4f}")
    print(f"RMSE: {rmse:.4f}")

    x_model_df = pd.DataFrame(X_imputed, columns=score_cols)
    cn_feature_names = [ASPECT_CN[k] for k in ASPECT_COLS.keys()]

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(x_model_df)
    shap_abs_mean = np.abs(shap_values).mean(axis=0)
    shap_norm = normalize_01(shap_abs_mean)

    plt.figure(figsize=(9, 6))
    shap.summary_plot(
        shap_values,
        x_model_df,
        feature_names=cn_feature_names,
        show=False,
    )
    plt.tight_layout()
    plt.savefig(fig_dir / "fig_shap_beeswarm.png", dpi=200, bbox_inches="tight")
    plt.close()

    order_idx = np.argsort(shap_abs_mean)[::-1]
    order_keys = np.array(list(ASPECT_COLS.keys()))[order_idx]
    order_cn = [ASPECT_CN[k] for k in order_keys]
    order_vals = shap_abs_mean[order_idx]

    plt.figure(figsize=(8, 5))
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(order_cn))]
    plt.barh(order_cn[::-1], order_vals[::-1], color=colors[::-1])
    plt.xlabel("Mean |SHAP value|")
    plt.ylabel("维度")
    plt.title("SHAP重要性（平均绝对值）")
    plt.tight_layout()
    plt.savefig(fig_dir / "fig_shap_bar.png", dpi=200, bbox_inches="tight")
    plt.close()

    top3_keys = order_keys[:3]
    top3_score_cols = [ASPECT_COLS[k] for k in top3_keys]
    top3_cn = [ASPECT_CN[k] for k in top3_keys]

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    for idx, (col_name, cn_name) in enumerate(zip(top3_score_cols, top3_cn)):
        shap.dependence_plot(
            ind=col_name,
            shap_values=shap_values,
            features=x_model_df,
            feature_names=score_cols,
            interaction_index=None,
            ax=axes[idx],
            show=False,
        )
        axes[idx].set_title(cn_name)
        axes[idx].set_xlabel(f"{cn_name}评分")
        axes[idx].set_ylabel("SHAP值")
    plt.tight_layout()
    plt.savefig(fig_dir / "fig_shap_dependence_top3.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # NOTE: Partial correlation is degenerate when y_overall = mean(all scores)
    # because each score is mechanically part of y. We use SHAP as sole importance.
    # DML robustness check (importance_dml.py) provides independent validation.

    combined = shap_norm  # SHAP-only importance

    results = pd.DataFrame(
        {
            "aspect": list(ASPECT_COLS.keys()),
            "aspect_cn": [ASPECT_CN[k] for k in ASPECT_COLS.keys()],
            "shap_importance": shap_norm,
            "combined_importance": combined,
        }
    )
    results = results.sort_values("combined_importance", ascending=False).reset_index(drop=True)
    results.to_csv(out_dir / "importance_scores.csv", index=False, encoding="utf-8-sig")

    # SHAP importance bar chart (single, clean)
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(results))]
    bars = ax.barh(
        results["aspect_cn"].values[::-1],
        results["shap_importance"].values[::-1],
        color=colors[::-1],
        edgecolor='white',
        linewidth=1.5,
        height=0.6,
    )
    for bar, val in zip(bars, results["shap_importance"].values[::-1]):
        ax.text(val + 0.01, bar.get_y() + bar.get_height() / 2,
                f'{val:.3f}', va='center', fontsize=11)
    ax.set_xlabel("SHAP 重要性 (归一化)", fontsize=13)
    ax.set_title("比亚迪汉 各维度对总体满意度的重要性 (SHAP)", fontsize=15, fontweight='bold')
    ax.grid(axis='x', linestyle=':', alpha=0.4)
    plt.tight_layout()
    plt.savefig(fig_dir / "fig_importance_comparison.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    print("\n=== Combined importance ranking ===")
    for i, row in results.iterrows():
        print(
            f"{i + 1}. {row['aspect_cn']} ({row['aspect']}): "
            f"importance={row['combined_importance']:.4f}, "
            f"shap={row['shap_importance']:.4f}"
        )

    print(f"\nSaved: {out_dir / 'importance_scores.csv'}")
    print(f"Saved figures to: {fig_dir}")


if __name__ == "__main__":
    main()
