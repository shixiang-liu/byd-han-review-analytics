# pyright: reportGeneralTypeIssues=false, reportMissingTypeStubs=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportAny=false, reportAttributeAccessIssue=false, reportMissingTypeArgument=false, reportUnreachable=false, reportImplicitStringConcatenation=false, reportOperatorIssue=false, reportReturnType=false, reportUnusedCallResult=false, reportUnknownParameterType=false
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
import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import KFold


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


def crossfit_partialling_out(
    df: pd.DataFrame,
    treatment_col: str,
    outcome_col: str,
    control_cols: list[str],
    n_splits: int = 5,
    random_state: int = 42,
) -> tuple[float, float, float, float, float, int]:
    use_cols = [treatment_col, outcome_col] + control_cols
    sub = df[use_cols].dropna().copy()
    n = len(sub)

    if n < n_splits + 5:
        return np.nan, np.nan, np.nan, np.nan, np.nan, n

    x = sub[control_cols].values
    t = sub[treatment_col].values
    y = sub[outcome_col].values

    eps = np.zeros(n)
    eta = np.zeros(n)

    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    for train_idx, test_idx in kf.split(x):
        x_train, x_test = x[train_idx], x[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        t_train, t_test = t[train_idx], t[test_idx]

        model_y = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=3,
            random_state=random_state,
        )
        model_t = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=3,
            random_state=random_state,
        )

        model_y.fit(x_train, y_train)
        model_t.fit(x_train, t_train)

        y_hat = model_y.predict(x_test)
        t_hat = model_t.predict(x_test)

        eps[test_idx] = y_test - y_hat
        eta[test_idx] = t_test - t_hat

    denom = np.sum(eta**2)
    if np.isclose(denom, 0.0):
        return np.nan, np.nan, np.nan, np.nan, np.nan, n

    theta = np.sum(eps * eta) / denom
    se = np.sqrt(np.sum((eps - theta * eta) ** 2) / (n * denom))
    ci_lower = theta - 1.96 * se
    ci_upper = theta + 1.96 * se

    z = theta / se if not np.isclose(se, 0.0) else np.nan
    p_value = 2 * norm.sf(abs(z)) if np.isfinite(z) else np.nan

    return theta, se, ci_lower, ci_upper, p_value, n


def main() -> None:
    plt.rcParams["font.sans-serif"] = ["SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    root = Path(__file__).resolve().parents[1]
    data_path = root / "outputs" / "cleaned_reviews.csv"
    out_dir = root / "outputs"
    fig_dir = root / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(data_path, encoding="utf-8-sig")
    score_cols = list(ASPECT_COLS.values())
    y_col = "y_overall"
    df[y_col] = df[score_cols].mean(axis=1, skipna=True)

    has_price = "price" in df.columns and pd.api.types.is_numeric_dtype(df["price"])
    print(f"Price control included: {has_price}")

    rows = []
    for aspect_key, treatment_col in ASPECT_COLS.items():
        control_cols = [c for c in score_cols if c != treatment_col]
        if has_price:
            control_cols = control_cols + ["price"]

        theta, se, ci_lower, ci_upper, p_value, n_used = crossfit_partialling_out(
            df=df,
            treatment_col=treatment_col,
            outcome_col=y_col,
            control_cols=control_cols,
            n_splits=5,
            random_state=42,
        )

        rows.append(
            {
                "aspect": aspect_key,
                "aspect_cn": ASPECT_CN[aspect_key],
                "theta": theta,
                "se": se,
                "ci_lower": ci_lower,
                "ci_upper": ci_upper,
                "p_value": p_value,
                "n_used": n_used,
            }
        )

    dml_res = pd.DataFrame(rows)
    dml_res = dml_res.sort_values("theta", ascending=False).reset_index(drop=True)
    dml_res.to_csv(out_dir / "dml_results.csv", index=False, encoding="utf-8-sig")

    print("\n=== DML results ===")
    print(
        dml_res[
            ["aspect_cn", "theta", "se", "ci_lower", "ci_upper", "p_value", "n_used"]
        ].to_string(index=False)
    )

    plot_df = dml_res.sort_values("theta", ascending=True).copy()
    is_sig = plot_df["p_value"].lt(0.05)
    colors = np.where(is_sig, PALETTE[2], "#BDBDBD")

    y_pos = np.arange(len(plot_df))
    xerr = np.vstack(
        [
            plot_df["theta"].values - plot_df["ci_lower"].values,
            plot_df["ci_upper"].values - plot_df["theta"].values,
        ]
    )

    fig, ax = plt.subplots(figsize=(9, 5.5))
    for i in range(len(plot_df)):
        ax.errorbar(
            x=plot_df.iloc[i]["theta"],
            y=y_pos[i],
            xerr=np.array([[xerr[0, i]], [xerr[1, i]]]),
            fmt="o",
            color=colors[i],
            ecolor=colors[i],
            capsize=4,
            markersize=6,
        )
    ax.axvline(0, color="black", linestyle="--", linewidth=1)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(plot_df["aspect_cn"].values)
    ax.set_xlabel("DML估计系数 θ")
    ax.set_title("DML稳健性检验：各维度影响及95%置信区间")

    from matplotlib.lines import Line2D

    legend_handles = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=PALETTE[2], label="显著 (p<0.05)", markersize=8),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#BDBDBD", label="不显著", markersize=8),
    ]
    ax.legend(handles=legend_handles, loc="best")

    plt.tight_layout()
    plt.savefig(fig_dir / "fig_dml_effects.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    shap_path = out_dir / "importance_scores.csv"
    if shap_path.exists():
        shap_res = pd.read_csv(shap_path, encoding="utf-8-sig")
        shap_rank = shap_res.sort_values("combined_importance", ascending=False).reset_index(drop=True)
        dml_rank = dml_res.sort_values("theta", ascending=False).reset_index(drop=True)

        shap_rank_map = {row["aspect"]: idx + 1 for idx, row in shap_rank.iterrows()}
        dml_rank_map = {row["aspect"]: idx + 1 for idx, row in dml_rank.iterrows()}

        compare_rows = []
        for key in ASPECT_COLS.keys():
            compare_rows.append(
                {
                    "aspect_cn": ASPECT_CN[key],
                    "SHAP排名": shap_rank_map.get(key, np.nan),
                    "DML排名": dml_rank_map.get(key, np.nan),
                }
            )

        compare_df = pd.DataFrame(compare_rows).sort_values("SHAP排名")
        print("\n=== SHAP ranking vs DML ranking ===")
        print(compare_df.to_string(index=False))
    else:
        print("\nimportance_scores.csv not found, skipped SHAP vs DML ranking comparison.")

    print(f"\nSaved: {out_dir / 'dml_results.csv'}")
    print(f"Saved figure: {fig_dir / 'fig_dml_effects.png'}")


if __name__ == "__main__":
    main()
