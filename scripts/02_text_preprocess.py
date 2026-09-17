from __future__ import annotations

import re
from pathlib import Path
from typing import cast

import jieba
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_PATH = BASE_DIR / "outputs" / "data" / "cleaned_reviews.csv"
OUTPUT_PATH = BASE_DIR / "outputs" / "data" / "tokenized_reviews.csv"
STOPWORDS_PATH = BASE_DIR / "data" / "stopwords.txt"

PUNCT_KEEP_TOKENS = {"\u3002", "\uff01", "\uff1f", "\uff1b", "\uff0c"}

NEGATION_KEEP_TOKENS = {
    "不",
    "没",
    "无",
    "非",
    "未",
    "别",
    "莫",
}

PRESERVE_TOKENS = NEGATION_KEEP_TOKENS | PUNCT_KEEP_TOKENS | {
    "没有",
    "不会",
    "不用",
    "不能",
    "不太",
    "不够",
    "不足",
    "不好",
    "不高",
    "不佳",
    "不行",
    "不值",
    "不到",
    "不如",
    "不满",
    "不满意",
    "没啥",
    "没什么",
}

TARGET_TEXT_COLS = [
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

COL_NAME_MAP = {
    "text_space": "空间",
    "text_driving": "驾驶感受",
    "text_range": "续航",
    "text_appearance": "外观",
    "text_interior": "内饰",
    "text_value": "性价比",
    "text_smart": "智能化",
    "most_satisfied_text": "最满意",
    "most_dissatisfied_text": "最不满意",
}


def read_csv_with_fallback(path: Path) -> pd.DataFrame:
    for enc in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("unknown", b"", 0, 1, f"无法读取文件编码: {path}")


def load_stopwords(path: Path) -> set[str]:
    if not path.exists():
        raise FileNotFoundError(f"停用词文件不存在: {path}")

    stopwords: set[str] = set()
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            word = line.strip()
            if word:
                stopwords.add(word)
    stopwords.difference_update(PRESERVE_TOKENS)
    return stopwords


def normalize_text(text: str) -> str:
    cleaned = str(text)
    # Preserve sentence/clause separators so downstream keyword extraction does not merge words across sentences.
    cleaned = re.sub(r"[\u3002\uff01\uff1f!?]+", " \u3002 ", cleaned)
    cleaned = re.sub(r"[\uff1b;]+", " \uff1b ", cleaned)
    cleaned = re.sub(r"[\uff0c,\u3001]+", " \uff0c ", cleaned)
    cleaned = re.sub(r"[^一-鿿A-Za-z0-9。！？；，]+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def tokenize_text(text: str, stopwords: set[str]) -> list[str]:
    normalized = normalize_text(text)
    if not normalized:
        return []

    tokens: list[str] = []
    for token in jieba.cut(normalized, cut_all=False):
        token = token.strip().lower()
        if not token:
            continue
        if token in stopwords and token not in PRESERVE_TOKENS:
            continue
        if token in PUNCT_KEEP_TOKENS:
            tokens.append(token)
            continue
        if len(token) <= 1 and token not in NEGATION_KEEP_TOKENS:
            continue
        if token.isdigit():
            continue
        tokens.append(token)
    return tokens


def preprocess_column(series: pd.Series, stopwords: set[str]) -> tuple[pd.Series, pd.Series]:
    token_lists = series.fillna("").astype(str).map(lambda x: tokenize_text(x, stopwords))
    tokenized_text = token_lists.map(lambda x: " ".join(x) if x else pd.NA).astype("string")
    token_count = token_lists.map(len)
    return tokenized_text, token_count


def main() -> None:
    df = read_csv_with_fallback(INPUT_PATH)
    stopwords = load_stopwords(STOPWORDS_PATH)

    tokenized_df = df.copy()
    stats: list[tuple[str, float, int]] = []

    for col in TARGET_TEXT_COLS:
        if col not in tokenized_df.columns:
            continue

        tokenized_col, token_count = preprocess_column(cast(pd.Series, tokenized_df[col]), stopwords)
        tokenized_df[col] = tokenized_col

        non_empty_tokens = tokenized_col.dropna().astype(str).str.split()
        vocab = set()
        for token_list in non_empty_tokens:
            vocab.update(token_list)

        mean_tokens = token_count.mean()
        stats.append((col, float(mean_tokens), len(vocab)))

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    tokenized_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print("文本预处理完成")
    print(f"输入文件: {INPUT_PATH}")
    print(f"输出文件: {OUTPUT_PATH}")
    print(f"停用词数量: {len(stopwords)}")
    print("各维度分词统计:")
    for col, mean_tokens, vocab_size in stats:
        print(f"- {COL_NAME_MAP.get(col, col)} ({col}): 平均词数={mean_tokens:.2f}, 词汇量={vocab_size}")


if __name__ == "__main__":
    main()
