# pyright: basic, reportCallIssue=false, reportArgumentType=false, reportGeneralTypeIssues=false, reportAttributeAccessIssue=false, reportUnusedVariable=false

import sys
import argparse
import math
import re
import time

import numpy as np
import pandas as pd
from transformers import pipeline
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]  # repository root; raw corpus is not committed


MODEL_CANDIDATES = [
    "uer/roberta-base-finetuned-jd-binary-chinese",
    "techthiyanes/chinese-sentiment-analysis-large",
    "lxyuan/distilbert-base-multilingual-cased-sentiments-student",
]

INPUT_COLUMNS = [
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

OUTPUT_COLUMN_MAP = {
    "text_space": "sent_space",
    "text_driving": "sent_driving",
    "text_range": "sent_range",
    "text_appearance": "sent_appearance",
    "text_interior": "sent_interior",
    "text_value": "sent_value",
    "text_smart": "sent_smart",
    "most_satisfied_text": "sent_satisfied",
    "most_dissatisfied_text": "sent_dissatisfied",
}


def normalize_label(label: str) -> str:
    s = re.sub(r"[^a-z0-9]", "", str(label).strip().lower())
    return s


def infer_label_roles(classifier) -> tuple[dict[str, str], int]:
    id2label = getattr(classifier.model.config, "id2label", {})
    roles: dict[str, str] = {}

    for idx, label in id2label.items():
        nl = normalize_label(label)
        if any(k in nl for k in ["pos", "positive", "praise", "good"]):
            roles[nl] = "pos"
        elif any(k in nl for k in ["neg", "negative", "bad", "complaint"]):
            roles[nl] = "neg"
        elif any(k in nl for k in ["neu", "neutral", "middle"]):
            roles[nl] = "neu"

    num_labels = len(id2label) if id2label else 0
    generic = []
    for label in id2label.values():
        nl = normalize_label(label)
        m = re.fullmatch(r"label(\d+)", nl)
        if m:
            generic.append((int(m.group(1)), nl))

    if generic and ("pos" not in roles.values() or "neg" not in roles.values()):
        generic_sorted = sorted(generic, key=lambda x: x[0])
        if len(generic_sorted) == 2:
            roles[generic_sorted[0][1]] = roles.get(generic_sorted[0][1], "neg")
            roles[generic_sorted[1][1]] = roles.get(generic_sorted[1][1], "pos")
        elif len(generic_sorted) >= 3:
            roles[generic_sorted[0][1]] = roles.get(generic_sorted[0][1], "neg")
            roles[generic_sorted[-1][1]] = roles.get(generic_sorted[-1][1], "pos")
            mid = generic_sorted[len(generic_sorted) // 2][1]
            roles[mid] = roles.get(mid, "neu")

    return roles, num_labels


def load_sentiment_pipeline() -> tuple:
    last_exc = None
    for model_name in MODEL_CANDIDATES:
        try:
            print(f"Trying model: {model_name}", flush=True)
            try:
                clf = pipeline(
                    "sentiment-analysis",
                    model=model_name,
                    device="cpu",
                    truncation=True,
                    max_length=512,
                )
            except TypeError:
                clf = pipeline(
                    "sentiment-analysis",
                    model=model_name,
                    device=-1,
                    truncation=True,
                    max_length=512,
                )

            _ = clf(["这个车很好"], truncation=True, max_length=512)
            roles, num_labels = infer_label_roles(clf)
            print(
                f"Loaded model: {model_name} | num_labels={num_labels} | inferred_roles={roles}",
                flush=True,
            )
            return clf, model_name, roles, num_labels
        except Exception as exc:
            last_exc = exc
            print(f"Failed model {model_name}: {exc}", flush=True)

    raise RuntimeError(f"All candidate models failed to load. Last error: {last_exc}")


def to_sentiment_score(
    pred: list[dict[str, float]], roles: dict[str, str], num_labels: int
) -> float:
    probs: dict[str, float] = {}
    for item in pred:
        probs[normalize_label(item["label"])] = float(item["score"])

    p_pos = 0.0
    p_neg = 0.0
    p_neu = 0.0

    for label, prob in probs.items():
        role = roles.get(label)
        if role == "pos":
            p_pos += prob
        elif role == "neg":
            p_neg += prob
        elif role == "neu":
            p_neu += prob

    if p_pos == 0.0 and p_neg > 0.0 and num_labels == 2:
        p_pos = max(0.0, 1.0 - p_neg)
    if p_neg == 0.0 and p_pos > 0.0 and num_labels == 2:
        p_neg = max(0.0, 1.0 - p_pos)

    if p_neu > 0.0:
        score = 1.0 * p_pos + 0.5 * p_neu + 0.0 * p_neg
    elif num_labels == 3 and len(probs) >= 3:
        vals = sorted(probs.items(), key=lambda x: x[1], reverse=True)
        weighted = 0.0
        for lbl, prob in vals:
            role = roles.get(lbl)
            if role == "pos":
                weighted += prob
            elif role == "neu":
                weighted += 0.5 * prob
        score = weighted
    else:
        score = p_pos

    return float(np.clip(score, 0.0, 1.0))


def smoke_test(classifier, df: pd.DataFrame, roles: dict[str, str], num_labels: int) -> None:
    sample_texts = []
    for col in INPUT_COLUMNS:
        non_empty = df[col].dropna().astype(str)
        non_empty = non_empty[non_empty.str.strip() != ""]
        if not non_empty.empty:
            sample_texts.append(non_empty.iloc[0])
        if len(sample_texts) >= 5:
            break

    if len(sample_texts) < 5:
        sample_texts.extend([
            "这辆车外观很漂亮，空间很大，开起来很舒服。",
            "续航太差了，冬天掉电严重，非常失望。",
            "一般般，没有特别好也没有特别差。",
        ])
        sample_texts = sample_texts[:5]

    print("\n[Smoke Test] Running sentiment on 5 sample texts...", flush=True)
    preds = classifier(sample_texts, truncation=True, max_length=512, batch_size=8)
    for i, (txt, pred) in enumerate(zip(sample_texts, preds), start=1):
        if isinstance(pred, dict):
            pred = [pred]
        score = to_sentiment_score(pred, roles=roles, num_labels=num_labels)
        preview = txt.replace("\n", " ")[:80]
        print(f"  {i}. text='{preview}'")
        print(f"     raw={pred}")
        print(f"     score={score:.4f}", flush=True)


def run(args) -> None:
    t0 = time.time()

    print(f"Reading input: {args.input}", flush=True)
    df = pd.read_csv(args.input, encoding="utf-8-sig")
    print(f"Input shape: {df.shape}", flush=True)

    missing = [c for c in INPUT_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required input columns: {missing}")

    classifier, model_name, roles, num_labels = load_sentiment_pipeline()

    smoke_test(classifier, df, roles=roles, num_labels=num_labels)

    for out_col in OUTPUT_COLUMN_MAP.values():
        df[out_col] = np.nan

    n_rows = len(df)

    # ── Optimized: process one column at a time with large internal batch ────
    # Instead of iterating row-batches × columns, iterate columns × row-batches.
    # This reduces pipeline overhead and allows larger internal batching.

    print(
        f"\nStarting full inference with model '{model_name}' | rows={n_rows} | "
        f"columns={len(INPUT_COLUMNS)}",
        flush=True,
    )

    overall_start = time.time()
    PIPE_BATCH_SIZE = 64  # internal pipeline batch size for CPU

    for col_idx, (in_col, out_col) in enumerate(OUTPUT_COLUMN_MAP.items(), start=1):
        col_start_t = time.time()

        # Gather all valid texts for this column
        all_texts = df[in_col].tolist()
        valid_indices: list[int] = []
        valid_texts: list[str] = []

        for i, value in enumerate(all_texts):
            if pd.isna(value):
                continue
            text = str(value).strip()
            if not text:
                continue
            valid_indices.append(i)
            valid_texts.append(text)

        n_valid = len(valid_texts)
        print(
            f"\n[Column {col_idx}/{len(INPUT_COLUMNS)}] {in_col} -> {out_col} | "
            f"valid texts: {n_valid}/{n_rows}",
            flush=True,
        )

        if not valid_texts:
            print(f"  No valid texts, skipping.", flush=True)
            continue

        # Process in chunks for progress reporting (every 1000 texts)
        CHUNK = 1000
        scores = [math.nan] * n_rows
        processed = 0

        for chunk_start in range(0, n_valid, CHUNK):
            chunk_end = min(chunk_start + CHUNK, n_valid)
            chunk_texts = valid_texts[chunk_start:chunk_end]
            chunk_indices = valid_indices[chunk_start:chunk_end]

            preds = classifier(
                chunk_texts,
                truncation=True,
                max_length=512,
                batch_size=PIPE_BATCH_SIZE,
            )

            for idx, pred in zip(chunk_indices, preds):
                if isinstance(pred, dict):
                    pred = [pred]
                scores[idx] = to_sentiment_score(pred, roles=roles, num_labels=num_labels)

            processed += len(chunk_texts)
            elapsed_col = time.time() - col_start_t
            speed = processed / elapsed_col if elapsed_col > 0 else 0
            remaining = n_valid - processed
            eta = remaining / speed if speed > 0 else 0
            print(
                f"  {processed}/{n_valid} ({100*processed/n_valid:.0f}%) | "
                f"speed={speed:.1f} texts/s | eta={eta:.0f}s",
                flush=True,
            )

        df[out_col] = scores
        col_time = time.time() - col_start_t
        total_elapsed = time.time() - overall_start
        print(
            f"  Column done in {col_time:.1f}s | total elapsed: {total_elapsed/60:.1f} min",
            flush=True,
        )

        # Checkpoint after each column
        df.to_csv(args.checkpoint, index=False, encoding="utf-8-sig")
        print(f"  Checkpoint saved after column {in_col}", flush=True)

    df.to_csv(args.output, index=False, encoding="utf-8-sig")
    total_time = time.time() - t0

    print(f"\nOutput saved: {args.output}", flush=True)
    print(f"Total runtime: {total_time/60:.2f} min", flush=True)

    expected_new = list(OUTPUT_COLUMN_MAP.values())
    missing_output_cols = [c for c in expected_new if c not in df.columns]
    print("\n[Validation]", flush=True)
    print(f"Rows: {len(df)}", flush=True)
    print(f"Columns: {len(df.columns)}", flush=True)
    print(f"Missing sentiment columns: {missing_output_cols}", flush=True)

    print("\n[Summary Statistics]", flush=True)
    for c in expected_new:
        s = df[c]
        non_null = s.notna().sum()
        if non_null > 0:
            print(
                f"{c}: count={int(non_null)}, mean={s.mean():.4f}, "
                f"std={s.std():.4f}, min={s.min():.4f}, max={s.max():.4f}",
                flush=True,
            )
        else:
            print(f"{c}: count=0 (all NaN)", flush=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="BERT-based sentiment analysis for BYD Han review aspect texts"
    )
    parser.add_argument(
        "--input",
        default=str(PROJECT_ROOT) + "/outputs/cleaned_reviews.csv",
        help="Input cleaned reviews CSV",
    )
    parser.add_argument(
        "--output",
        default=str(PROJECT_ROOT) + "/outputs/sentiment_scores.csv",
        help="Output CSV with sentiment scores",
    )
    parser.add_argument(
        "--checkpoint",
        default=str(PROJECT_ROOT) + "/outputs/sentiment_checkpoint.csv",
        help="Checkpoint CSV path",
    )
    parser.add_argument("--batch-size", type=int, default=64, help="Pipeline batch size")
    parser.add_argument(
        "--progress-every", type=int, default=1000, help="Print progress every N rows"
    )
    parser.add_argument(
        "--checkpoint-every",
        type=int,
        default=2000,
        help="Save checkpoint every N rows",
    )
    return parser


if __name__ == "__main__":
    parser = build_parser()
    run(parser.parse_args())
