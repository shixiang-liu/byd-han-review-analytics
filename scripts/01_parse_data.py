import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LEGACY_ROOT = PROJECT_ROOT / "data" / "raw"


def _resolve_existing_path(*candidates: Path) -> Path:
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]


INPUT_PATH = _resolve_existing_path(
    PROJECT_ROOT / "data" / "data_BYDhan_2.7_qichezhijia.csv",
    LEGACY_ROOT / "data_BYDhan_2.7_qichezhijia.csv",
)
OUTPUT_PATH = PROJECT_ROOT / "outputs" / "data" / "parsed_reviews.csv"

START_LINE_PATTERN = re.compile(r"^[^,]+,.+,.+,\d{4}-\d{2}-\d{2}[^,]*,")
NUMERIC_PATTERN = re.compile(r"-?\d+(?:\.\d+)?")
SCORE_PATTERN = re.compile(r"^\D*([1-5])\D*$")

ASPECT_ALIASES = {
    "空间": ["空间"],
    "驾驶感受": ["驾驶感受", "操控"],
    "续航": ["续航", "冬季续航", "夏季续航", "春秋续航"],
    "外观": ["外观"],
    "内饰": ["内饰", "舒适性"],
    "性价比": ["性价比", "价格政策", "选择这款车的理由"],
    "智能化": ["智能化"],
}

ASPECTS = [
    ("MY", "空间", "score_space", "text_space"),
    ("HX", "驾驶感受", "score_driving", "text_driving"),
    ("KY", "续航", "score_range", "text_range"),
    ("SY", "外观", "score_appearance", "text_appearance"),
    ("VK", "内饰", "score_interior", "text_interior"),
    ("YY", "性价比", "score_value", "text_value"),
    ("KX", "智能化", "score_smart", "text_smart"),
]

ALL_POSSIBLE_LABELS = set(["最满意", "最不满意", "新车好评", "新车槽点", "裸车购买价", "购买时间", "购买地点", "参考价格", "探店时间", "探店地点"] + [alias for aliases in ASPECT_ALIASES.values() for alias in aliases])

@dataclass
class ParsedLine:
    line_no: int
    raw: str
    tag: str
    value: str

def split_tag(raw_line: str, line_no: int) -> ParsedLine:
    text = raw_line.rstrip("\n").rstrip("\r")
    if "|" in text:
        left, right = text.split("|", 1)
        tag = left[1:] if left.startswith("#") else left
        value = right.strip().strip('"')
        return ParsedLine(line_no=line_no, raw=text, tag=tag, value=value)
    return ParsedLine(line_no=line_no, raw=text, tag="", value=text.strip().strip('"'))

def is_review_start(line: ParsedLine) -> bool:
    return bool(START_LINE_PATTERN.match(line.value))

def parse_start_line(line: ParsedLine, issues: List[str]) -> Dict[str, Optional[str]]:
    raw = line.value.strip().strip('"')
    date_match = re.search(r",(\d{4}-\d{2}-\d{2}[^,]*),", raw)
    if not date_match:
        issues.append(f"[line {line.line_no}] malformed start line (missing date): {line.raw}")
        return {"username": None, "model": None, "date": None, "mileage": None}

    prefix = raw[: date_match.start()]
    date = date_match.group(1).replace(" 首次发表", "").strip()
    mileage = raw[date_match.end() :].strip().strip('"')

    first_comma = prefix.find(",")
    last_comma = prefix.rfind(",")
    if first_comma == -1 or last_comma == -1 or first_comma == last_comma:
        issues.append(f"[line {line.line_no}] malformed start line (insufficient commas): {line.raw}")
        return {"username": None, "model": None, "date": date, "mileage": mileage}

    username = prefix[:first_comma].strip()
    model = prefix[last_comma + 1 :].strip()

    return {
        "username": username,
        "model": model,
        "date": date,
        "mileage": mileage,
    }

def line_has_label(line: ParsedLine, expected_texts: List[str], expected_tag: Optional[str] = None) -> bool:
    if line.value in expected_texts:
        return True
    if expected_tag and line.tag == expected_tag:
        return True
    return False

def find_label_index(
    review_lines: List[ParsedLine],
    start_idx: int,
    label_texts: List[str],
    label_tag: Optional[str],
) -> Optional[int]:
    for idx in range(start_idx, len(review_lines)):
        if line_has_label(review_lines[idx], label_texts, label_tag):
            return idx
    return None

def find_value_before_label(
    review_lines: List[ParsedLine],
    start_idx: int,
    label_texts: List[str],
    label_tag: Optional[str],
    issues: List[str],
    review_start_line: int,
) -> Tuple[Optional[str], int]:
    label_idx = find_label_index(review_lines, start_idx, label_texts, label_tag)
    if label_idx is None:
        issues.append(f"[line {review_start_line}] missing label: {label_texts[0]}")
        return None, start_idx

    value = None
    for idx in range(label_idx - 1, start_idx - 1, -1):
        candidate = review_lines[idx].value.strip().strip('"')
        if candidate:
            value = candidate
            break

    if value is None:
        issues.append(f"[line {review_start_line}] missing value before label: {label_texts[0]}")

    return value, label_idx + 1

def find_text_after_label(
    review_lines: List[ParsedLine],
    start_idx: int,
    label_texts: List[str],
    label_tag: Optional[str],
    issues: List[str],
    review_start_line: int,
) -> Tuple[str, int]:
    label_idx = find_label_index(review_lines, start_idx, label_texts, label_tag)
    if label_idx is None:
        issues.append(f"[line {review_start_line}] missing section label: {label_texts[0]}")
        return "", start_idx

    if label_idx + 1 >= len(review_lines):
        issues.append(f"[line {review_start_line}] missing text after label: {label_texts[0]}")
        return "", label_idx + 1
        
    # We should gather all text until the next known label or end of review
    text_parts = []
    next_idx = len(review_lines)
    for j in range(label_idx + 1, len(review_lines)):
        if review_lines[j].value in ALL_POSSIBLE_LABELS:
            next_idx = j
            break
        val = review_lines[j].value.strip().strip('"')
        if val:
            text_parts.append(val)
            
    return "\n".join(text_parts), next_idx

def parse_numeric(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    match = NUMERIC_PATTERN.search(value)
    if not match:
        return None
    return float(match.group(0))

def parse_aspects(
    review_lines: List[ParsedLine],
    start_idx: int,
    issues: List[str],
    review_start_line: int,
) -> Dict[str, Optional[object]]:
    parsed: Dict[str, Optional[object]] = {}
    for _, _, score_col, text_col in ASPECTS:
        parsed[score_col] = None
        parsed[text_col] = ""

    cursor = start_idx
    for i, (tag, base_label, score_col, text_col) in enumerate(ASPECTS):
        aliases = ASPECT_ALIASES[base_label]
        label_idx = find_label_index(review_lines, cursor, aliases, tag)
        if label_idx is None:
            issues.append(f"[line {review_start_line}] missing aspect: {base_label}")
            continue

        # Look for next valid label
        next_idx = len(review_lines)
        for j in range(label_idx + 1, len(review_lines)):
            if review_lines[j].value in ALL_POSSIBLE_LABELS:
                next_idx = j
                break

        score = None
        score_line_idx = None
        for idx in range(label_idx + 1, next_idx):
            match = SCORE_PATTERN.match(review_lines[idx].value.strip())
            if match:
                score = int(match.group(1))
                score_line_idx = idx
                break

        if score is None:
            issues.append(f"[line {review_start_line}] missing score for aspect: {base_label}")
            text_start = label_idx + 1
        else:
            text_start = (score_line_idx + 1) if score_line_idx is not None else (label_idx + 1)

        text_parts = []
        for idx in range(text_start, next_idx):
            value = review_lines[idx].value.strip().strip('"')
            if value:
                text_parts.append(value)

        parsed[score_col] = score
        parsed[text_col] = "\n".join(text_parts)
        cursor = next_idx  # Resume search from here

    return parsed

def parse_reviews(input_path: Path) -> Tuple[pd.DataFrame, List[str]]:
    lines: List[ParsedLine] = []
    with input_path.open("r", encoding="utf-8", newline="") as f:
        for line_no, raw in enumerate(f, start=1):
            lines.append(split_tag(raw, line_no))

    if not lines:
        return pd.DataFrame(), ["Input file is empty"]

    start_indices = [idx for idx, line in enumerate(lines) if idx > 0 and is_review_start(line)]
    issues: List[str] = []
    records: List[Dict[str, Optional[object]]] = []

    for i, start_idx in enumerate(start_indices):
        end_idx = start_indices[i + 1] if i + 1 < len(start_indices) else len(lines)
        review_lines = lines[start_idx:end_idx]
        review_start_line = review_lines[0].line_no

        base = parse_start_line(review_lines[0], issues)
        cursor = 1

        mileage_label_idx = find_label_index(review_lines, cursor, ["行驶里程"], "SM")
        if mileage_label_idx is None:
            issues.append(f"[line {review_start_line}] missing label: 行驶里程")
        else:
            cursor = mileage_label_idx + 1

        fuel_raw, cursor = find_value_before_label(
            review_lines, cursor, ["百公里油耗"], "YH", issues, review_start_line
        )
        winter_elec_raw, cursor = find_value_before_label(
            review_lines, cursor, ["冬季电耗", "百公里电耗"], "MK", issues, review_start_line
        )
        winter_range_raw, cursor = find_value_before_label(
            review_lines, cursor, ["冬季续航", "夏季续航", "春秋续航"], "PY", issues, review_start_line
        )
        price_raw, cursor = find_value_before_label(
            review_lines, cursor, ["裸车购买价", "参考价格"], "XJ", issues, review_start_line
        )
        purchase_time_raw, cursor = find_value_before_label(
            review_lines, cursor, ["购买时间", "探店时间"], "RP", issues, review_start_line
        )
        purchase_city_raw, cursor = find_value_before_label(
            review_lines, cursor, ["购买地点", "探店地点"], "BH", issues, review_start_line
        )

        most_satisfied_text, cursor = find_text_after_label(
            review_lines, cursor, ["最满意", "新车好评"], "YJ", issues, review_start_line
        )
        most_dissatisfied_text, cursor = find_text_after_label(
            review_lines, cursor, ["最不满意", "新车槽点"], "HR", issues, review_start_line
        )

        aspects = parse_aspects(review_lines, cursor, issues, review_start_line)

        record: Dict[str, Optional[object]] = {
            "username": base["username"],
            "model": base["model"],
            "date": base["date"],
            "mileage": base["mileage"],
            "fuel_consumption": parse_numeric(fuel_raw),
            "winter_elec_consumption": parse_numeric(winter_elec_raw),
            "winter_range": parse_numeric(winter_range_raw),
            "price": parse_numeric(price_raw),
            "purchase_time": purchase_time_raw,
            "purchase_city": purchase_city_raw,
            "most_satisfied_text": most_satisfied_text,
            "most_dissatisfied_text": most_dissatisfied_text,
        }
        record.update(aspects)
        records.append(record)

    columns = [
        "username",
        "model",
        "date",
        "mileage",
        "fuel_consumption",
        "winter_elec_consumption",
        "winter_range",
        "price",
        "purchase_time",
        "purchase_city",
        "most_satisfied_text",
        "most_dissatisfied_text",
        "score_space",
        "score_driving",
        "score_range",
        "score_appearance",
        "score_interior",
        "score_value",
        "score_smart",
        "text_space",
        "text_driving",
        "text_range",
        "text_appearance",
        "text_interior",
        "text_value",
        "text_smart",
    ]

    df = pd.DataFrame(records, columns=columns)
    score_cols = [
        "score_space",
        "score_driving",
        "score_range",
        "score_appearance",
        "score_interior",
        "score_value",
        "score_smart",
    ]
    for col in score_cols:
        score_series = pd.to_numeric(df[col], errors="coerce")
        df[col] = pd.Series(score_series, index=df.index, dtype="Int64")

    for col in ["fuel_consumption", "winter_elec_consumption", "winter_range", "price"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df, issues

def print_summary(df: pd.DataFrame) -> None:
    score_cols = [
        "score_space",
        "score_driving",
        "score_range",
        "score_appearance",
        "score_interior",
        "score_value",
        "score_smart",
    ]
    print("=== Parsing Summary ===")
    print(f"Total reviews parsed: {len(df):,}")
    print("\nMissing values per column:")
    print(df.isna().sum().to_string())

def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df, issues = parse_reviews(INPUT_PATH)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print_summary(df)
    print(f"\nOutput saved: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
