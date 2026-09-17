#!/usr/bin/env python3
# pyright: basic

from __future__ import annotations

from pathlib import Path
from typing import Any, cast
import re

import os
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
try:
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    from matplotlib import font_manager
    from matplotlib.colors import LinearSegmentedColormap
    from PIL import Image, ImageDraw, ImageFont
    from wordcloud import WordCloud

    HAS_PLOT_LIBS = True
except ModuleNotFoundError:
    plt = None  # type: ignore[assignment]
    fm = None  # type: ignore[assignment]
    font_manager = None  # type: ignore[assignment]
    LinearSegmentedColormap = None  # type: ignore[assignment]
    Image = None  # type: ignore[assignment]
    ImageDraw = None  # type: ignore[assignment]
    ImageFont = None  # type: ignore[assignment]
    WordCloud = None  # type: ignore[assignment]
    HAS_PLOT_LIBS = False

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LEGACY_ROOT = PROJECT_ROOT / "data" / "raw"


def resolve_path(*parts: str, legacy: bool = False) -> Path:
    root = LEGACY_ROOT if legacy else PROJECT_ROOT
    return root.joinpath(*parts)


INPUT_CSV = resolve_path("outputs", "data", "tokenized_reviews.csv")
SENTIMENT_CSV = resolve_path("outputs", "data", "sentiment_scores.csv")
OUTPUT_CSV = resolve_path("outputs", "tables", "keywords_top.csv")
OUTPUT_XLSX = resolve_path("outputs", "tables", "keywords_top.xlsx")
FIG_DIR = resolve_path("figures")

ASPECT_SPECS = [
    ("text_space", "space", "空间"),
    ("text_driving", "driving", "驾驶感受"),
    ("text_range", "range", "续航"),
    ("text_appearance", "appearance", "外观"),
    ("text_interior", "interior", "内饰"),
    ("text_value", "value", "性价比"),
    ("text_smart", "smart", "智能化"),
]

EXTRA_SPECS = [
    ("most_satisfied_text", "satisfied", "最满意"),
    ("most_dissatisfied_text", "dissatisfied", "最不满意"),
]

PALETTE = ["#4C78A8", "#F58518", "#E45756", "#72B7B2", "#54A24B", "#EECA3B", "#B279A2"]
WC_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
    "C:/Windows/Fonts/simhei.ttf",
    "C:/Windows/Fonts/simsun.ttc",
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/msyhbd.ttc",
    "C:/Windows/Fonts/simkai.ttf",
]

if HAS_PLOT_LIBS:
    for font_path in [
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/msyhbd.ttc",
        "C:/Windows/Fonts/simkai.ttf",
    ]:
        if os.path.exists(font_path):
            try:
                fm.fontManager.addfont(font_path)
                plt.rcParams["font.family"] = fm.FontProperties(fname=font_path).get_name()
                break
            except Exception as e:
                print("Font load error:", e)
    plt.rcParams["font.sans-serif"] = ["SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

TEXT_TO_SENTIMENT_COL = {
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

TEXT_TO_SCORE_COL = {
    "text_space": "score_space",
    "text_driving": "score_driving",
    "text_range": "score_range",
    "text_appearance": "score_appearance",
    "text_interior": "score_interior",
    "text_value": "score_value",
    "text_smart": "score_smart",
}

ASPECT_BLACKLIST = {
    "text_space": {"空间"},
    "text_driving": {"驾驶", "驾驶感受"},
    "text_range": {"续航"},
    "text_appearance": {"外观", "外观设计"},
    "text_interior": {"内饰"},
    "text_value": {"性价比"},
    "text_smart": {"智能化"},
    "most_satisfied_text": {"满意", "最满意"},
    "most_dissatisfied_text": {"不满意", "最不满意", "满意", "空间", "驾驶感受", "续航", "外观", "内饰", "性价比", "智能化"},
}

NOISE_WORDS = {
    "满意",
    "不满意",
    "喜欢",
    "地方",
    "时候",
    "不是",
    "的话",
    "特别",
    "尤其",
    "一般",
    "普通",
    "无敌",
    "不错",
    "可以",
    "这个",
    "这款",
    "这辆",
    "这车",
    "车子",
    "车型",
    "比亚迪",
    "电车",
    "新能源",
    "现在",
    "感觉",
    "然后",
    "比较",
    "有点",
    "没有",
    "问题",
    "完全",
    "真的",
    "整体",
    "很多",
    "不过",
    "唯一",
    "接受",
    "毕竟",
    "不算",
    "稍微",
}


SENTIMENT_CUE_TOKENS = {
    "异味", "味道", "刺鼻", "异响", "胎噪", "噪音", "噪声", "偏硬", "偏软", "颠", "颠簸", "卡顿",
    "掉电", "虚标", "断网", "迟钝", "延迟", "慢", "不足", "不够", "问题", "故障", "漏风", "开裂",
    "不稳", "顿挫", "老气", "塑料", "廉价", "发热", "黑屏", "死机", "不好", "差", "贵", "低",
    "好", "很好", "优秀", "丝滑", "稳定", "省油", "顺畅", "舒适", "扎实", "高级",
}

NEGATIVE_CUE_TOKENS = {
    "异味", "味道", "刺鼻", "异响", "胎噪", "噪音", "噪声", "偏硬", "颠", "颠簸", "卡顿",
    "掉电", "虚标", "断网", "迟钝", "延迟", "慢", "不足", "不够", "问题", "故障", "漏风", "开裂",
    "不稳", "顿挫", "老气", "塑料", "廉价", "发热", "黑屏", "死机", "不好", "差", "贵", "低",
    "等待", "等车", "太久", "不行", "不高", "不满意",
    "拥挤", "顶头", "憋屈", "顶到", "晃", "抖", "发飘", "漏", "生锈", "掉漆",
}

MIN_NEG_DOC_FREQ = 3
MIN_NEG_POS_DIFF = 0.003
MAX_PHRASES_PER_DOC = 40

MIN_TOKEN_LEN = 2

NEGATIVE_PREFIX_TOKENS = (
    "不够",
    "不足",
    "不好",
    "不行",
    "不高",
    "不佳",
    "不稳",
    "不灵",
    "不顺",
    "不耐",
    "不值",
    "不如",
    "不到",
    "不太",
    "不满",
    "不满意",
    "没电",
    "没信号",
    "没反应",
    "没效果",
    "没优惠",
    "没支撑",
    "没质感",
    "没高级感",
    "没法",
)

FALSE_NEGATIVE_PHRASES = {
    "不用 担心",
    "不会 过时",
    "不会 感到",
    "不失 动感",
    "轻松 不少",
    "升级 不断",
    "不用 钥匙",
    "方便 不用",
}

NON_COMPLAINT_PATTERNS = (
    "没有 不满意",
    "没 什么 不满意",
    "没啥 不满意",
    "没 遇到 不满意",
    "没有 槽点",
    "挑不出 毛病",
    "没 什么 毛病",
    "没啥 毛病",
)

DISPLAY_TOKEN_CANONICAL = {
    "\u5473\u9053": "\u5f02\u5473",
    "\u523a\u9f3b": "\u5f02\u5473",
    "\u8f66\u5185": "\u5f02\u5473",
    "\u76ae\u9769": "\u5f02\u5473",
    "\u5f02\u5473": "\u5f02\u5473",
    "\u566a\u97f3": "\u566a\u97f3",
    "\u566a\u58f0": "\u566a\u97f3",
    "\u80ce\u566a": "\u566a\u97f3",
    "\u98ce\u566a": "\u566a\u97f3",
    "\u5f02\u54cd": "\u566a\u97f3",
    "\u5361\u987f": "\u5361\u987f",
    "\u9ed1\u5c4f": "\u5361\u987f",
    "\u6b7b\u673a": "\u5361\u987f",
    "\u5ef6\u8fdf": "\u5361\u987f",
    "\u8fdf\u949d": "\u5361\u987f",
    "\u6389\u7535": "\u6389\u7535",
    "\u865a\u6807": "\u865a\u6807",
    "\u6ca1\u7535": "\u6ca1\u7535",
    "\u7b49\u8f66": "\u7b49\u8f66",
    "\u7b49\u5f85": "\u7b49\u8f66",
    "\u62e5\u6324": "\u5c40\u4fc3",
    "\u5c40\u4fc3": "\u5c40\u4fc3",
    "\u9876\u5934": "\u9876\u5934",
    "\u9876\u5230": "\u9876\u5934",
    "\u8001\u6c14": "\u8001\u6c14",
    "\u5851\u6599": "\u5851\u6599",
    "\u7c97\u7cd9": "\u7c97\u7cd9",
    "\u5ec9\u4ef7": "\u7c97\u7cd9",
    "\u504f\u786c": "\u504f\u786c",
    "\u98a0\u7c38": "\u98a0\u7c38",
    "\u987f\u632b": "\u987f\u632b",
    "\u65ad\u7f51": "\u65ad\u8054",
    "\u65ad\u8054": "\u65ad\u8054",
    "\u6545\u969c": "\u6545\u969c",
    "\u7ef4\u4fee": "\u6545\u969c",
    "\u8d35": "\u504f\u8d35",
}

SIMPLE_DISPLAY_MAP = {
    "\u5185\u9970\u5f02\u5473": "\u5f02\u5473",
    "\u5851\u6599\u611f": "\u5851\u6599",
    "\u6750\u8d28\u5ec9\u4ef7": "\u5851\u6599",
    "\u8bbe\u8ba1\u6b20\u4f73": "\u6b20\u4f73",
    "\u5185\u9970\u8001\u6c14": "\u8001\u6c14",
    "\u9020\u578b\u8001\u6c14": "\u6b20\u4f73",
    "\u4e0d\u8010\u810f": "\u4e0d\u8010\u810f",
    "\u9ad8\u901f\u6389\u7535": "\u6389\u7535",
    "\u7a7a\u8c03\u6389\u7535": "\u6389\u7535",
    "\u6389\u7535\u8f83\u5feb": "\u6389\u7535",
    "\u7eed\u822a\u7f29\u6c34": "\u7f29\u6c34",
    "\u7535\u91cf\u89c1\u5e95": "\u6ca1\u7535",
    "\u7535\u91cf\u4e0d\u8db3": "\u6ca1\u7535",
    "\u6027\u4ef7\u6bd4\u4e0d\u9ad8": "\u504f\u8d35",
    "\u4ef7\u683c\u504f\u8d35": "\u504f\u8d35",
    "\u4f18\u60e0\u8f83\u5c11": "\u4f18\u60e0\u5c11",
    "\u517b\u8f66\u6210\u672c\u9ad8": "\u6210\u672c\u9ad8",
    "\u8def\u611f\u98a0\u7c38": "\u98a0\u7c38",
    "\u5e95\u76d8\u504f\u786c": "\u504f\u786c",
    "\u80ce\u566a\u98ce\u566a": "\u566a\u97f3",
    "\u8d77\u6b65\u987f\u632b": "\u987f\u632b",
    "\u884c\u9a76\u566a\u97f3": "\u566a\u97f3",
    "\u52a8\u529b\u504f\u5f31": "\u4e4f\u529b",
    "\u7a7a\u95f4\u4e0d\u8db3": "\u5c40\u4fc3",
    "\u7a7a\u95f4\u5c40\u4fc3": "\u5c40\u4fc3",
    "\u4f7f\u7528\u4e0d\u4fbf": "\u4e0d\u4fbf",
    "\u4e58\u5750\u4e0d\u9002": "\u4e0d\u9002",
    "\u5934\u90e8\u9876\u5934": "\u9876\u5934",
    "\u50a8\u7269\u4e0d\u8db3": "\u50a8\u7269\u5c11",
    "\u8f66\u673a\u5361\u987f": "\u5361\u987f",
    "\u8fde\u63a5\u4e0d\u7a33": "\u65ad\u8054",
    "\u6cca\u8f66\u4e00\u822c": "\u6cca\u8f66",
    "\u8bbe\u8ba1\u666e\u901a": "\u6b20\u4f73",
    "\u8f66\u6f06\u504f\u8584": "\u6b20\u4f73",
    "\u9020\u578b\u8fdd\u548c": "\u6b20\u4f73",
    "\u9020\u578b\u8001\u6c14": "\u6b20\u4f73",
}

ASPECT_ALLOWED_DISPLAY_LABELS = {
    "interior": {"异味", "塑料", "老气"},
    "range": {"掉电", "缩水", "没电"},
    "value": {"偏贵", "优惠少"},
    "driving": {"偏硬", "噪音", "颠簸", "乏力", "顿挫"},
    "space": {"局促", "不便", "不适", "顶头"},
    "smart": {"卡顿", "断联"},
    "appearance": {"欠佳"},
}

DisplayKeywordItem = tuple[str, float, str, str]
MIN_DISPLAY_ITEMS_FOR_ASPECT = 2
MIN_FALLBACK_DOC_COUNT = 5
MIN_FALLBACK_SUPPORT_RATIO = 0.03

SATISFIED_WORDCLOUD_THEME_MAP = {
    "颜值": {"颜值", "好看", "时尚", "帅气", "漂亮", "大气", "造型", "线条", "外形", "外观设计"},
    "宽敞": {"宽敞", "很大", "拥挤"},
    "动力": {"动力", "加速", "提速", "超车"},
    "省油": {"油耗", "省油", "省钱", "成本"},
    "舒适": {"舒服", "舒适", "座椅"},
    "配置": {"配置", "功能", "科技", "智能", "智能化"},
    "操控": {"操控", "流畅", "平顺"},
    "续航": {"续航", "充电", "电池"},
    "性价比": {"性价比", "价格"},
}

SATISFIED_WORDCLOUD_STOPWORDS = {
    "外观", "空间", "设计", "内饰", "驾驶", "感受", "表现", "选择",
    "起来", "不用", "担心", "看到", "整个", "试驾", "车型", "新能源",
    "比亚迪", "车身", "车子", "这款", "这车", "这辆", "地方", "时候",
    "喜欢", "满意", "不错", "方便", "使用", "体验", "看起来",
    "公里", "台车", "首先", "用车", "开车", "吸引", "前脸",
    "不会",
}

SATISFIED_WORDCLOUD_RAW_ALLOWLIST = {"豪华", "性能", "运动"}
SATISFIED_WORDCLOUD_SUPPORT_BAN = {"很大", "不会 拥挤", "价格", "油耗", "十足"}
SATISFIED_WORDCLOUD_SUPPORT_MAP = {
    "好看": "好看",
    "时尚": "时尚",
    "大气": "大气",
    "造型": "造型",
    "线条": "线条",
    "帅气": "帅气",
    "漂亮": "漂亮",
    "回头率": "回头率",
    "宽敞": "宽敞",
    "座椅": "座椅",
    "舒服": "舒服",
    "加速": "加速",
    "提速": "提速",
    "起步": "起步",
    "超车": "超车",
    "科技": "科技",
    "功能": "功能",
    "流畅": "流畅",
    "豪华": "豪华",
    "充电": "充电",
    "省钱": "省钱",
    "性能": "性能",
    "运动": "运动",
}

DISSATISFIED_WORDCLOUD_STOPWORDS = {
    "不太", "友好", "要说", "出现", "存在", "明显", "现象",
}

DISSATISFIED_THEME_TOKEN_MAP = {
    "异味": {"异味", "味道"},
    "噪音": {"噪音", "胎噪", "风噪"},
    "卡顿": {"卡顿"},
    "不便": {"不便", "方便"},
    "颠簸": {"颠簸"},
    "等车": {"等车", "等待", "太久"},
}

MIN_WORDCLOUD_SECONDARY_SCORE = 0.002
MAX_SATISFIED_SECONDARY_WORDS = 15
MAX_SATISFIED_SUPPORTS_PER_THEME = 3
MAX_DISSATISFIED_SECONDARY_WORDS = 6


def _is_valid_token(token: str) -> bool:
    t = token.strip()
    if len(t) < MIN_TOKEN_LEN:
        return False
    if t in NOISE_WORDS:
        return False
    # 纯数字/字母/混合ID通常是型号或噪声
    if re.fullmatch(r"[A-Za-z0-9._-]+", t):
        return False
    return True


def _phrase_has_cue(tokens: list[str]) -> bool:
    for tok in tokens:
        if tok in SENTIMENT_CUE_TOKENS:
            return True
        if tok.startswith("不") and len(tok) >= 2:
            return True
        if tok.endswith(("问题", "不足", "不够", "卡顿", "异响", "异味", "噪音", "掉电", "偏硬", "偏软")):
            return True
    return False


def _phrase_has_negative_cue(tokens: list[str]) -> bool:
    if _phrase_is_false_negative(tokens):
        return False
    for tok in tokens:
        if _token_has_negative_cue(tok):
            return True
    return False


def _token_has_negative_cue(tok: str) -> bool:
    if tok in NEGATIVE_CUE_TOKENS:
        return True
    if any(tok.startswith(prefix) for prefix in NEGATIVE_PREFIX_TOKENS):
        return True
    if tok.endswith(("问题", "不足", "不够", "卡顿", "异响", "异味", "噪音", "掉电", "偏硬")):
        return True
    return False


def _phrase_is_false_negative(tokens: list[str]) -> bool:
    phrase = " ".join(tokens)
    if phrase in FALSE_NEGATIVE_PHRASES:
        return True
    if tokens and tokens[0] in {"不会", "不用", "没有", "没什么", "没啥"}:
        return True
    if len(tokens) >= 2 and tokens[0] == "没" and tokens[1] in {"什么", "事", "试"}:
        return True
    return False


def _text_has_negative_cue(text: str) -> bool:
    tokens = [tok for tok in str(text).split() if tok.strip()]
    if not tokens:
        return False
    if _is_non_complaint_doc(text):
        return False
    return any(_token_has_negative_cue(tok) for tok in tokens)


def _is_non_complaint_doc(text: str) -> bool:
    compact = re.sub(r"\s+", " ", str(text)).strip()
    return any(pattern in compact for pattern in NON_COMPLAINT_PATTERNS)


def compact_keyword(term: str, aspect_en: str) -> str:
    tokens = [tok for tok in str(term).split() if tok.strip()]
    if not tokens:
        return ""

    joined = " ".join(tokens)
    has_soft_neg = any(tok in {"\u4e0d\u592a", "\u4e0d\u591f", "\u4e0d\u8db3", "\u4e0d\u597d", "\u4e0d\u884c", "\u4e0d\u4f1a", "\u6ca1\u6709", "\u4e0d\u5230", "\u4e0d\u9ad8", "\u4e0d\u4f73"} for tok in tokens)
    has_negative_cue = has_soft_neg or any(_token_has_negative_cue(tok) for tok in tokens)

    def has_any(words) -> bool:
        words = set(words)
        return any(tok in words for tok in tokens)

    if has_soft_neg and "\u65b9\u4fbf" in tokens:
        return "\u4f7f\u7528\u4e0d\u4fbf"
    if has_soft_neg and "\u53cb\u597d" in tokens:
        return "" if aspect_en == "dissatisfied" else "\u4f53\u9a8c\u4e0d\u53cb\u597d"
    if has_soft_neg and any(tok in {"\u8212\u670d", "\u8212\u9002"} for tok in tokens):
        return "\u4e58\u5750\u4e0d\u9002"
    if has_soft_neg and "\u7406\u60f3" in tokens:
        return ""
    if has_soft_neg and "\u6548\u679c" in tokens:
        return ""

    if aspect_en == "space" or has_any({"\u7a7a\u95f4", "\u5ea7\u6905", "\u540e\u6392", "\u5934\u90e8", "\u817f\u90e8"}):
        if has_any({"\u9876\u5934", "\u9876\u5230"}):
            return "\u5934\u90e8\u9876\u5934"
        if has_any({"\u6df1\u5ea6"}) and (has_any({"\u4e0d\u591f", "\u4e0d\u8db3"}) or has_soft_neg):
            return "\u50a8\u7269\u4e0d\u8db3"
        if has_any({"\u62e5\u6324"}):
            return "\u540e\u6392\u5c40\u4fc3" if has_any({"\u540e\u6392", "\u5ea7\u6905"}) else "\u7a7a\u95f4\u5c40\u4fc3"
        if has_any({"\u5c40\u4fc3"}):
            return "\u7a7a\u95f4\u5c40\u4fc3"
        if has_negative_cue and has_any({"\u7a7a\u95f4", "\u5ea7\u6905", "\u540e\u6392", "\u5934\u90e8", "\u817f\u90e8"}):
            return "\u7a7a\u95f4\u4e0d\u8db3"
        if aspect_en == "space":
            return ""

    if aspect_en == "driving" or has_any({"\u51cf\u9707", "\u60ac\u67b6", "\u52a8\u529b", "\u52a0\u901f", "\u8def\u9762", "\u65b9\u5411\u76d8"}):
        if has_any({"\u80ce\u566a", "\u98ce\u566a"}):
            return "\u80ce\u566a\u98ce\u566a"
        if has_any({"\u566a\u97f3", "\u566a\u58f0", "\u5f02\u54cd"}):
            return "\u884c\u9a76\u566a\u97f3"
        if has_any({"\u98a0\u7c38"}):
            return "\u8def\u611f\u98a0\u7c38"
        if has_any({"\u987f\u632b"}):
            return "\u8d77\u6b65\u987f\u632b"
        if has_any({"\u504f\u786c"}):
            return "\u5e95\u76d8\u504f\u786c"
        if has_any({"\u51cf\u9707", "\u60ac\u67b6"}) and (has_any({"\u504f\u786c", "\u4e0d\u597d", "\u5dee"}) or has_soft_neg):
            return "\u5e95\u76d8\u504f\u786c"
        if has_any({"\u52a8\u529b", "\u52a0\u901f"}) and (has_any({"\u5f31", "\u6162", "\u8089", "\u4e0d\u8db3"}) or has_soft_neg):
            return "\u52a8\u529b\u504f\u5f31"
        if aspect_en == "driving":
            return ""

    if aspect_en == "range" or has_any({"\u7eed\u822a", "\u516c\u91cc", "\u7535\u91cf", "\u7535\u8017", "\u6cb9\u8017", "\u5145\u7535"}):
        if has_any({"\u9ad8\u901f"}) and has_any({"\u6389\u7535"}):
            return "\u9ad8\u901f\u6389\u7535"
        if has_any({"\u7a7a\u8c03"}) and has_any({"\u6389\u7535"}):
            return "\u7a7a\u8c03\u6389\u7535"
        if has_any({"\u6389\u7535"}):
            return "\u6389\u7535\u8f83\u5feb"
        if has_any({"\u865a\u6807"}):
            return "\u7eed\u822a\u865a\u6807"
        if has_any({"\u6ca1\u7535"}):
            return "\u7535\u91cf\u89c1\u5e95"
        if has_any({"\u7535\u91cf"}) and (has_any({"\u4e0d\u5230", "\u4e0d\u591f", "\u504f\u4f4e"}) or has_soft_neg):
            return "\u7535\u91cf\u4e0d\u8db3"
        if has_any({"\u7eed\u822a", "\u516c\u91cc"}) and (has_any({"\u4e0d\u5230", "\u4e0d\u591f", "\u7f29\u6c34", "\u504f\u4f4e", "\u592a\u77ed", "\u8870\u51cf"}) or has_soft_neg):
            return "\u7eed\u822a\u7f29\u6c34"
        if aspect_en == "range":
            return ""

    if aspect_en == "appearance" or has_any({"\u8bbe\u8ba1", "\u9020\u578b", "\u5916\u89c2"}):
        if has_any({"\u8f66\u6f06"}) and has_any({"\u8584", "\u5783\u573e", "\u5dee"}):
            return "\u8f66\u6f06\u504f\u8584"
        if has_any({"\u8001\u6c14", "\u814a\u8089"}):
            return "\u9020\u578b\u8001\u6c14"
        if has_any({"\u8fdd\u548c"}):
            return "\u9020\u578b\u8fdd\u548c"
        if has_any({"\u666e\u901a", "\u5927\u4f17\u5316", "\u7b80\u5355"}):
            return "\u8bbe\u8ba1\u666e\u901a"
        if has_any({"\u989c\u8272"}) and has_any({"\u5c11", "\u4e0d\u591f"}):
            return "\u914d\u8272\u504f\u5c11"
        if has_any({"\u4e11", "\u96be\u770b", "\u571f"}) or (has_negative_cue and has_any({"\u8bbe\u8ba1", "\u9020\u578b", "\u5916\u89c2"})):
            return "\u8bbe\u8ba1\u6b20\u4f73"
        if aspect_en == "appearance":
            return ""

    if aspect_en == "interior" or has_any({"\u5185\u9970", "\u7528\u6599", "\u6750\u8d28", "\u505a\u5de5"}):
        if has_any({"\u5f02\u5473", "\u5473\u9053", "\u523a\u9f3b", "\u76ae\u9769"}):
            return "\u5185\u9970\u5f02\u5473"
        if has_soft_neg and has_any({"\u8010\u810f"}):
            return "\u4e0d\u8010\u810f"
        if has_any({"\u5851\u6599"}):
            return "\u5851\u6599\u611f"
        if has_any({"\u8001\u6c14"}):
            return "\u5185\u9970\u8001\u6c14"
        if has_any({"\u8bbe\u8ba1"}) and (has_any({"\u4e0d\u591f", "\u4e0d\u597d", "\u5dee"}) or has_soft_neg):
            return "\u8bbe\u8ba1\u6b20\u4f73"
        if has_any({"\u7c97\u7cd9", "\u5ec9\u4ef7"}) or (has_any({"\u7528\u6599", "\u6750\u8d28", "\u505a\u5de5", "\u5185\u9970"}) and has_any({"\u5dee", "\u4e0d\u597d", "\u5ec9\u4ef7"})):
            return "\u6750\u8d28\u5ec9\u4ef7"
        if aspect_en == "interior":
            return ""

    if aspect_en == "value" or has_any({"\u6027\u4ef7\u6bd4", "\u4ef7\u683c", "\u4ef7\u4f4d", "\u552e\u4ef7", "\u4f18\u60e0", "\u6210\u672c", "\u4fdd\u517b", "\u8865\u8d34"}):
        # "??" ? "??" ???????/?????????????
        if has_any({"\u7b49\u8f66", "\u7b49\u5f85", "\u6545\u969c", "\u7ef4\u4fee"}):
            return ""
        if "\u6027\u4ef7\u6bd4" in tokens and has_any({"\u4e0d\u9ad8", "\u4f4e", "\u4e0d\u503c", "\u4e00\u822c"}):
            return "\u6027\u4ef7\u6bd4\u4e0d\u9ad8"
        if has_any({"\u4ef7\u683c", "\u4ef7\u4f4d", "\u552e\u4ef7"}) and has_any({"\u8d35", "\u504f\u8d35", "\u592a\u9ad8", "\u4e0d\u4f4e"}):
            return "\u4ef7\u683c\u504f\u8d35"
        if has_any({"\u6210\u672c", "\u4fdd\u517b"}) and has_any({"\u9ad8", "\u8d35"}) and not has_any({"\u4e0d\u9ad8"}):
            return "\u517b\u8f66\u6210\u672c\u9ad8"
        if has_any({"\u4f18\u60e0"}) and (has_any({"\u5c11", "\u4e0d\u591a", "\u4e0d\u7ed9", "\u6ca1\u6709"}) or has_soft_neg):
            return "\u4f18\u60e0\u8f83\u5c11"
        if aspect_en == "value":
            return ""

    if aspect_en == "smart" or has_any({"\u8f66\u673a", "\u7cfb\u7edf", "\u4fe1\u53f7", "\u7f51\u7edc", "\u84dd\u7259", "\u8f66\u4f4d", "\u505c\u8f66"}):
        if has_any({"\u5361\u987f", "\u9ed1\u5c4f", "\u6b7b\u673a", "\u5ef6\u8fdf", "\u8fdf\u949d"}):
            return "\u8f66\u673a\u5361\u987f"
        if has_any({"\u65ad\u8054", "\u65ad\u7f51", "\u6ca1\u4fe1\u53f7"}):
            return "\u8fde\u63a5\u4e0d\u7a33"
        if "\u4fe1\u53f7" in tokens and has_any({"\u4e0d\u597d", "\u5dee", "\u5f31"}):
            return "\u8fde\u63a5\u4e0d\u7a33"
        if has_any({"\u505c\u8f66", "\u6cca\u8f66"}) and (has_soft_neg or has_any({"\u4e0d\u719f\u7ec3", "\u4e00\u822c", "\u6162"})):
            return "\u6cca\u8f66\u4e00\u822c"
        if aspect_en == "smart":
            return ""

    for tok in tokens:
        mapped = DISPLAY_TOKEN_CANONICAL.get(tok)
        if mapped:
            if aspect_en == "dissatisfied" and mapped in {"\u7b49\u8f66"}:
                continue
            return mapped

    if "\u4e0d\u4fbf" in joined:
        return "\u4e0d\u4fbf"
    if "\u4e0d\u53cb\u597d" in joined:
        return "" if aspect_en == "dissatisfied" else "\u4e0d\u53cb\u597d"
    if "\u4e0d\u9002" in joined:
        return "\u4e0d\u9002"

    return ""



def collapse_keyword_items(
    items: list[tuple[str, float]],
    aspect_en: str,
    *,
    top_n: int,
) -> list[DisplayKeywordItem]:
    collapsed: list[DisplayKeywordItem] = []
    seen: dict[str, int] = {}

    for keyword, score in items:
        phrase_display = compact_keyword(keyword, aspect_en)
        if not phrase_display:
            continue
        display = SIMPLE_DISPLAY_MAP.get(phrase_display, phrase_display)
        if display in seen:
            idx = seen[display]
            old_display, old_score, old_raw, old_score_type = collapsed[idx]
            if score > old_score:
                collapsed[idx] = (old_display, score, keyword, old_score_type)
            continue
        seen[display] = len(collapsed)
        collapsed.append((display, score, keyword, "contrastive_tfidf_ngram"))
        if len(collapsed) >= top_n:
            break

    return collapsed


def fallback_compact_keyword_items(
    texts: list[str],
    aspect_en: str,
    *,
    top_n: int,
) -> list[DisplayKeywordItem]:
    allowed_labels = ASPECT_ALLOWED_DISPLAY_LABELS.get(aspect_en)
    label_counts: dict[str, int] = {}
    label_examples: dict[str, str] = {}

    for text in texts:
        tokens = [tok for tok in str(text).split() if tok.strip()]
        if not tokens:
            continue

        seen_in_doc: set[str] = set()
        for n in (1, 2, 3):
            for idx in range(0, len(tokens) - n + 1):
                span_tokens = tokens[idx:idx + n]
                if _phrase_is_false_negative(span_tokens):
                    continue
                span = " ".join(span_tokens).replace("_", " ")
                phrase_label = compact_keyword(span, aspect_en)
                if not phrase_label:
                    continue

                display_label = SIMPLE_DISPLAY_MAP.get(phrase_label, phrase_label)
                if allowed_labels and display_label not in allowed_labels:
                    continue
                if display_label in seen_in_doc:
                    continue
                seen_in_doc.add(display_label)
                label_counts[display_label] = label_counts.get(display_label, 0) + 1
                label_examples.setdefault(display_label, span)

    ranked = sorted(label_counts.items(), key=lambda item: (-item[1], item[0]))
    return [
        (label, float(count), label_examples.get(label, label), "low_score_doc_support")
        for label, count in ranked[:top_n]
    ]


def filter_aspect_consistent_labels(
    items: list[DisplayKeywordItem],
    aspect_en: str,
) -> list[DisplayKeywordItem]:
    allowed_labels = ASPECT_ALLOWED_DISPLAY_LABELS.get(aspect_en)
    if not allowed_labels:
        return items

    score_map: dict[str, tuple[float, str, str]] = {}
    for display_label, score, raw_keyword, score_type in items:
        if display_label not in allowed_labels:
            continue
        old = score_map.get(display_label)
        if old is None or score > old[0]:
            score_map[display_label] = (score, raw_keyword, score_type)

    ranked = sorted(score_map.items(), key=lambda item: (-item[1][0], item[0]))
    return [
        (label, score, raw_keyword, score_type)
        for label, (score, raw_keyword, score_type) in ranked
    ]


def merge_display_keyword_items(
    primary_items: list[DisplayKeywordItem],
    supplement_items: list[DisplayKeywordItem],
    *,
    top_n: int,
) -> list[DisplayKeywordItem]:
    merged: list[DisplayKeywordItem] = []
    seen_display: set[str] = set()

    for item in primary_items + supplement_items:
        display_keyword = item[0]
        if display_keyword in seen_display:
            continue
        seen_display.add(display_keyword)
        merged.append(item)
        if len(merged) >= top_n:
            break

    return merged


def build_phrase_doc(text: str) -> str:
    """
    ??????????/??/??????????????????????
    ????????????2-3gram?????????????
    """
    # ???????????????????????
    sentences = re.split(r'[\u3002\uff01\uff1f\uff1b\uff0c\n]+', str(text))

    feats: list[str] = []

    for sent in sentences:
        tokens = [t for t in sent.split() if _is_valid_token(t)]
        if not tokens:
            continue

        # ????/?????n-gram?????????
        for n in (2, 3):
            if len(tokens) < n:
                continue
            for i in range(0, len(tokens) - n + 1):
                seg = tokens[i:i + n]
                if _phrase_has_cue(seg):
                    feats.append("_".join(seg))

    if feats:
        deduped = list(dict.fromkeys(feats))
        feats = deduped[:MAX_PHRASES_PER_DOC]

    if not feats:
        all_tokens = [t for sent in sentences for t in sent.split() if _is_valid_token(t)]
        feats = all_tokens[:20]

    return " ".join(feats)



def normalize_term(term: str) -> str:
    return term.replace("_", " ")


def choose_chinese_font() -> str | None:
    if not HAS_PLOT_LIBS:
        return None

    for font_path in WC_FONT_CANDIDATES:
        if Path(font_path).exists():
            try:
                font_manager.fontManager.addfont(font_path)
                font_name = font_manager.FontProperties(fname=font_path).get_name()
                plt.rcParams["font.sans-serif"] = [font_name, "SimHei", "DejaVu Sans"]
                print(f"[Font] Matplotlib Chinese font set: {font_name}")
            except Exception as exc:
                print(f"[Font] Failed to register matplotlib font ({font_path}): {exc}")
            print(f"[Font] Using Chinese font: {font_path}")
            return font_path
    print("[Font] No Chinese font found for WordCloud; using font_path=None")
    return None


def get_font_properties(font_path: str | None) -> Any:
    if not HAS_PLOT_LIBS or not font_path:
        return None
    try:
        return fm.FontProperties(fname=font_path)
    except Exception:
        return None


def draw_wordcloud_title(out_file: Path, title: str, font_path: str | None) -> None:
    if Image is None or ImageDraw is None or ImageFont is None or not font_path:
        return

    try:
        image = Image.open(out_file).convert("RGB")
        draw = ImageDraw.Draw(image)
        width, _height = image.size
        title_font = ImageFont.truetype(font_path, 34)
        bbox = draw.textbbox((0, 0), title, font=title_font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = max((width - text_w) // 2, 16)
        y = 16
        draw.rectangle((0, 0, width, y + text_h + 16), fill="white")
        draw.text((x, y), title, fill="black", font=title_font)
        image.save(out_file)
    except Exception as exc:
        print(f"[Warn] Skip title drawing '{title}': {exc}")


def collect_texts(series: pd.Series) -> list[str]:
    cleaned = series.dropna().astype(str).str.strip()
    cleaned = cleaned[cleaned != ""]
    return cleaned.tolist()


def prepare_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    input_csv = INPUT_CSV
    sentiment_csv = SENTIMENT_CSV
    if not input_csv.exists() or not sentiment_csv.exists():
        input_csv = resolve_path("outputs", "data", "tokenized_reviews.csv", legacy=True)
        sentiment_csv = resolve_path("outputs", "data", "sentiment_scores.csv", legacy=True)

    if not input_csv.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")
    if not sentiment_csv.exists():
        raise FileNotFoundError(f"Sentiment CSV not found: {sentiment_csv}")

    print(f"[Load] Reading tokenized data: {input_csv}")
    text_df = pd.read_csv(input_csv, encoding="utf-8-sig")
    print(f"[Load] Reading sentiment data: {sentiment_csv}")
    sent_df = pd.read_csv(sentiment_csv, encoding="utf-8-sig")

    if len(text_df) != len(sent_df):
        raise ValueError(
            f"Row mismatch between tokenized and sentiment data: {len(text_df)} vs {len(sent_df)}"
        )

    return text_df.reset_index(drop=True), sent_df.reset_index(drop=True)


def filter_noise_tokens(text: str) -> str:
    return build_phrase_doc(text)


def collect_low_texts(text_series: pd.Series, sent_series: pd.Series, threshold: float = 0.40) -> list[str]:
    raw_text = text_series.fillna("").astype(str).str.strip()
    score = pd.to_numeric(sent_series, errors="coerce")

    valid_mask = (raw_text != "") & score.notna()
    if valid_mask.sum() < 3:
        return []

    text_valid = raw_text[valid_mask]
    score_valid = score[valid_mask]

    label_mask = score_valid <= threshold
    if int(label_mask.sum()) < 30:
        adaptive = float(score_valid.quantile(0.20))
        label_mask = score_valid <= adaptive

    texts = text_valid[label_mask].map(filter_noise_tokens)
    texts = texts[texts.str.strip() != ""]
    return texts.tolist()


def collect_high_texts(text_series: pd.Series, sent_series: pd.Series, threshold: float = 0.60) -> list[str]:
    raw_text = text_series.fillna("").astype(str).str.strip()
    score = pd.to_numeric(sent_series, errors="coerce")

    valid_mask = (raw_text != "") & score.notna()
    if valid_mask.sum() < 3:
        return []

    text_valid = raw_text[valid_mask]
    score_valid = score[valid_mask]

    label_mask = score_valid >= threshold
    if int(label_mask.sum()) < 30:
        adaptive = float(score_valid.quantile(0.80))
        label_mask = score_valid >= adaptive

    texts = text_valid[label_mask].map(filter_noise_tokens)
    texts = texts[texts.str.strip() != ""]
    return texts.tolist()


def collect_low_texts_dual(
    text_series: pd.Series,
    sent_series: pd.Series,
    score_series: pd.Series,
    sent_threshold: float = 0.45,
) -> list[str]:
    raw_text = text_series.fillna("").astype(str).str.strip()
    sent = pd.to_numeric(sent_series, errors="coerce")
    score = pd.to_numeric(score_series, errors="coerce")

    valid_mask = (raw_text != "") & sent.notna() & score.notna()
    if valid_mask.sum() < 3:
        return []

    text_valid = raw_text[valid_mask]
    sent_valid = sent[valid_mask]
    score_valid = score[valid_mask]

    score_q = float(score_valid.quantile(0.30))
    low_score_cut = min(4.0, score_q)

    label_mask = (sent_valid <= sent_threshold) | (score_valid <= low_score_cut)
    if int(label_mask.sum()) < 30:
        sent_q = float(sent_valid.quantile(0.25))
        score_q2 = float(score_valid.quantile(0.35))
        label_mask = (sent_valid <= sent_q) | (score_valid <= score_q2)

    texts = text_valid[label_mask].map(filter_noise_tokens)
    texts = texts[texts.str.strip() != ""]
    return texts.tolist()


def collect_low_texts_by_score(
    text_series: pd.Series,
    score_series: pd.Series,
    low_score: int = 3,
) -> list[str]:
    raw_text = text_series.fillna("").astype(str).str.strip()
    score = pd.to_numeric(score_series, errors="coerce")

    valid_mask = (raw_text != "") & score.notna()
    if valid_mask.sum() < 3:
        return []

    text_valid = raw_text[valid_mask]
    score_valid = score[valid_mask]

    cue_mask = text_valid.map(_text_has_negative_cue)
    label_mask = (score_valid <= low_score) | ((score_valid <= (low_score + 1)) & cue_mask)
    if int(label_mask.sum()) < 20:
        label_mask = score_valid <= (low_score + 1)

    texts = text_valid[label_mask].map(filter_noise_tokens)
    texts = texts[texts.str.strip() != ""]
    return texts.tolist()


def collect_high_texts_by_score(
    text_series: pd.Series,
    score_series: pd.Series,
    high_score: int = 5,
) -> list[str]:
    raw_text = text_series.fillna("").astype(str).str.strip()
    score = pd.to_numeric(score_series, errors="coerce")

    valid_mask = (raw_text != "") & score.notna()
    if valid_mask.sum() < 3:
        return []

    text_valid = raw_text[valid_mask]
    score_valid = score[valid_mask]

    label_mask = score_valid >= high_score
    if int(label_mask.sum()) < 20:
        label_mask = score_valid >= (high_score - 1)

    texts = text_valid[label_mask].map(filter_noise_tokens)
    texts = texts[texts.str.strip() != ""]
    return texts.tolist()


def collect_labeled_texts(
    text_series: pd.Series,
    *,
    drop_non_complaint: bool = False,
) -> list[str]:
    raw_text = text_series.fillna("").astype(str).str.strip()
    texts = raw_text[raw_text != ""]
    if drop_non_complaint:
        texts = texts[~texts.map(_is_non_complaint_doc)]
    texts = texts.map(filter_noise_tokens)
    texts = texts[texts.str.strip() != ""]
    return texts.tolist()


def collect_high_texts_dual(
    text_series: pd.Series,
    sent_series: pd.Series,
    score_series: pd.Series,
    sent_threshold: float = 0.60,
) -> list[str]:
    raw_text = text_series.fillna("").astype(str).str.strip()
    sent = pd.to_numeric(sent_series, errors="coerce")
    score = pd.to_numeric(score_series, errors="coerce")

    valid_mask = (raw_text != "") & sent.notna() & score.notna()
    if valid_mask.sum() < 3:
        return []

    text_valid = raw_text[valid_mask]
    sent_valid = sent[valid_mask]
    score_valid = score[valid_mask]

    score_q = float(score_valid.quantile(0.70))
    high_score_cut = max(4.0, score_q)

    label_mask = (sent_valid >= sent_threshold) & (score_valid >= high_score_cut)
    if int(label_mask.sum()) < 30:
        sent_q = float(sent_valid.quantile(0.75))
        score_q2 = float(score_valid.quantile(0.65))
        label_mask = (sent_valid >= sent_q) & (score_valid >= score_q2)

    texts = text_valid[label_mask].map(filter_noise_tokens)
    texts = texts[texts.str.strip() != ""]
    return texts.tolist()


def extract_tfidf_keywords(
    texts: list[str], top_n: int = 20, blacklist: set[str] | None = None
) -> tuple[list[tuple[str, float]], dict[str, float]]:
    if len(texts) < 3:
        return [], {}

    vectorizer = TfidfVectorizer(
        max_features=1500,
        min_df=5,
        max_df=0.90,
        analyzer=cast(Any, str.split),
        lowercase=False,
    )

    try:
        tfidf_mat = cast(csr_matrix, vectorizer.fit_transform(texts))
    except ValueError:
        return [], {}

    tfidf_array = np.asarray(tfidf_mat.toarray(), dtype=float)
    mean_scores = tfidf_array.mean(axis=0)
    terms = vectorizer.get_feature_names_out()

    banned = blacklist or set()
    order = np.argsort(mean_scores)[::-1]
    ranked = [
        (normalize_term(str(terms[i])), float(mean_scores[i]))
        for i in order
        if mean_scores[i] > 0 and str(terms[i]) not in banned and normalize_term(str(terms[i])) not in banned
    ]
    return ranked[:top_n], dict(ranked)


def fit_tfidf(texts: list[str]) -> tuple[csr_matrix, np.ndarray, np.ndarray] | None:
    if len(texts) < 3:
        return None

    vectorizer = TfidfVectorizer(
        max_features=1500,
        min_df=5,
        max_df=0.90,
        analyzer=cast(Any, str.split),
        lowercase=False,
    )

    try:
        tfidf_mat = cast(csr_matrix, vectorizer.fit_transform(texts))
    except ValueError:
        return None

    return tfidf_mat, tfidf_mat.toarray(), vectorizer.get_feature_names_out()


def extract_contrastive_keywords(
    negative_texts: list[str],
    positive_texts: list[str],
    *,
    top_n: int = 20,
    blacklist: set[str] | None = None,
    prefer_positive: bool = False,
) -> tuple[list[tuple[str, float]], dict[str, float]]:
    combined = negative_texts + positive_texts
    fit = fit_tfidf(combined)
    if fit is None:
        fallback_texts = positive_texts if prefer_positive else negative_texts
        return extract_tfidf_keywords(fallback_texts, top_n=top_n, blacklist=blacklist)

    _, tfidf_array, terms = fit
    neg_count = len(negative_texts)
    pos_count = len(positive_texts)

    if neg_count == 0 or pos_count == 0:
        texts = positive_texts if prefer_positive else (negative_texts if neg_count else positive_texts)
        return extract_tfidf_keywords(texts, top_n=top_n, blacklist=blacklist)

    neg_array = tfidf_array[:neg_count]
    pos_array = tfidf_array[neg_count:]

    neg_mean = neg_array.mean(axis=0)
    pos_mean = pos_array.mean(axis=0)
    neg_df = (neg_array > 0).sum(axis=0)
    pos_df = (pos_array > 0).sum(axis=0)
    scores = pos_mean - neg_mean if prefer_positive else neg_mean - pos_mean

    banned = blacklist or set()
    ranked: list[tuple[str, float]] = []
    for idx in np.argsort(scores)[::-1]:
        term_raw = str(terms[idx])
        term = normalize_term(term_raw)
        tokens = term_raw.split("_")
        if term_raw in banned or term in banned:
            continue
        if scores[idx] <= 0:
            continue
        if not prefer_positive and not _phrase_has_negative_cue(tokens):
            continue

        neg_df_i = int(neg_df[idx])
        pos_df_i = int(pos_df[idx])
        if neg_df_i < MIN_NEG_DOC_FREQ:
            continue

        neg_ratio = neg_df_i / max(neg_count, 1)
        pos_ratio = pos_df_i / max(pos_count, 1)
        if (neg_ratio - pos_ratio) < MIN_NEG_POS_DIFF:
            continue

        if prefer_positive:
            if pos_mean[idx] <= neg_mean[idx] * 1.05:
                continue
        elif neg_mean[idx] <= pos_mean[idx] * 1.05:
            continue
        ranked.append((term, float(scores[idx])))

    return ranked[:top_n], dict(ranked)


def extract_negative_cue_keywords(
    texts: list[str],
    *,
    top_n: int = 20,
    blacklist: set[str] | None = None,
) -> tuple[list[tuple[str, float]], dict[str, float]]:
    fit = fit_tfidf(texts)
    if fit is None:
        return [], {}

    _, tfidf_array, terms = fit
    mean_scores = tfidf_array.mean(axis=0)
    doc_freq = (tfidf_array > 0).sum(axis=0)
    banned = blacklist or set()

    ranked: list[tuple[str, float]] = []
    for idx in np.argsort(mean_scores)[::-1]:
        if mean_scores[idx] <= 0:
            continue
        if int(doc_freq[idx]) < MIN_NEG_DOC_FREQ:
            continue

        term_raw = str(terms[idx])
        term = normalize_term(term_raw)
        tokens = term_raw.split("_")
        if term_raw in banned or term in banned:
            continue
        if not _phrase_has_negative_cue(tokens):
            continue
        ranked.append((term, float(mean_scores[idx])))

    return ranked[:top_n], dict(ranked)


def gradient_colors(n: int) -> list[tuple[float, float, float, float]]:
    if not HAS_PLOT_LIBS:
        return []

    cmap = LinearSegmentedColormap.from_list("main_palette", PALETTE)
    if n <= 1:
        return [cmap(0.7)]
    return [cmap(i / (n - 1)) for i in range(n)]


def _rects_overlap(a: tuple[int, int, int, int], b: tuple[int, int, int, int], pad: int = 18) -> bool:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    return not (
        ax2 + pad < bx1
        or bx2 + pad < ax1
        or ay2 + pad < by1
        or by2 + pad < ay1
    )


def _word_cloud_candidates(width: int, height: int) -> list[tuple[int, int]]:
    points: list[tuple[int, int]] = []
    center_x = width // 2
    center_y = height // 2 + 10
    for y in range(130, height - 90, 56):
        for x in range(120, width - 120, 72):
            points.append((x, y))
    points.sort(key=lambda p: ((p[0] - center_x) ** 2 + (p[1] - center_y) ** 2, abs(p[1] - center_y)))
    return points


def _word_cloud_anchor_positions(width: int, height: int, n: int) -> list[tuple[int, int]]:
    layout = [
        (0.26, 0.56),
        (0.73, 0.56),
        (0.50, 0.31),
        (0.50, 0.79),
        (0.18, 0.28),
        (0.82, 0.28),
        (0.18, 0.78),
        (0.82, 0.78),
        (0.36, 0.18),
        (0.64, 0.18),
        (0.34, 0.50),
        (0.66, 0.50),
        (0.38, 0.88),
        (0.62, 0.88),
        (0.08, 0.50),
        (0.92, 0.50),
        (0.10, 0.17),
        (0.90, 0.17),
        (0.10, 0.88),
        (0.90, 0.88),
    ]
    anchors = [(int(width * x), int(height * y)) for x, y in layout[:min(len(layout), n)]]
    if len(anchors) >= n:
        return anchors

    seen = set(anchors)
    for pt in _word_cloud_candidates(width, height):
        if pt in seen:
            continue
        anchors.append(pt)
        seen.add(pt)
        if len(anchors) >= n:
            break
    return anchors


def _match_dissatisfied_theme(norm: str) -> str | None:
    tokens = [tok for tok in norm.split() if tok.strip()]
    for theme, vocab in DISSATISFIED_THEME_TOKEN_MAP.items():
        if any(tok in vocab for tok in tokens):
            return theme
    return None


def _match_satisfied_theme(norm: str) -> str | None:
    tokens = [tok for tok in norm.split() if tok.strip()]
    for theme, vocab in SATISFIED_WORDCLOUD_THEME_MAP.items():
        if any(tok in vocab for tok in tokens):
            return theme
    return None


def _canonicalize_satisfied_support(norm: str) -> str | None:
    norm = str(norm).strip()
    if not norm or norm in SATISFIED_WORDCLOUD_SUPPORT_BAN:
        return None

    compact = norm.replace(" ", "")
    if compact in SATISFIED_WORDCLOUD_SUPPORT_MAP:
        return SATISFIED_WORDCLOUD_SUPPORT_MAP[compact]

    tokens = [tok for tok in norm.split() if tok.strip()]
    for tok in tokens:
        if tok in SATISFIED_WORDCLOUD_SUPPORT_BAN or tok in SATISFIED_WORDCLOUD_STOPWORDS:
            continue
        mapped = SATISFIED_WORDCLOUD_SUPPORT_MAP.get(tok)
        if mapped:
            return mapped
    return None


def build_wordcloud(
    freq_dict: dict[str, float], title: str, out_file: Path, font_path: str | None
) -> None:
    if Image is None or ImageDraw is None or ImageFont is None or not font_path:
        return

    try:
        width, height = 1680, 960
        image = Image.new("RGB", (width, height), "#f8f4ed")
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((24, 24, width - 24, height - 24), radius=34, outline="#d8cfbf", width=2, fill="#fffaf2")

        items = sorted(freq_dict.items(), key=lambda item: item[1], reverse=True)
        if not items:
            image.save(out_file)
            return

        values = [float(score) for _, score in items]
        v_max = max(values)
        v_min = min(values)
        palette = ["#274060", "#2c7a7b", "#3e8f63", "#7aa53b", "#d6a419", "#6c5dd3"]
        placed_rects: list[tuple[int, int, int, int]] = []
        anchors = _word_cloud_anchor_positions(width, height, len(items))
        candidates = _word_cloud_candidates(width, height)

        for idx, (label, score) in enumerate(items):
            text = str(label).replace(" ", "")
            if not text:
                continue

            if v_max == v_min:
                norm = 1.0
            else:
                norm = (float(score) - v_min) / (v_max - v_min)
            font_size = int(34 + (norm ** 0.78) * 150)
            if idx >= 8:
                font_size = min(font_size, 92)
            if idx >= 14:
                font_size = min(font_size, 72)
            if idx >= 20:
                font_size = min(font_size, 56)

            placed = False
            while font_size >= 22 and not placed:
                font = ImageFont.truetype(font_path, font_size)
                bbox = draw.textbbox((0, 0), text, font=font)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
                candidate_points = [anchors[idx]] + [pt for pt in candidates if pt != anchors[idx]]
                for cx, cy in candidate_points:
                    left = int(cx - text_w / 2)
                    top = int(cy - text_h / 2)
                    rect = (left, top, left + text_w, top + text_h)
                    if rect[0] < 56 or rect[1] < 56 or rect[2] > width - 56 or rect[3] > height - 56:
                        continue
                    if any(_rects_overlap(rect, existing) for existing in placed_rects):
                        continue

                    color = palette[idx % len(palette)]
                    shadow = (rect[0] + 3, rect[1] + 3)
                    draw.text(shadow, text, font=font, fill="#e8e0d2")
                    draw.text((rect[0], rect[1]), text, font=font, fill=color)
                    placed_rects.append(rect)
                    placed = True
                    break
                if not placed:
                    font_size = int(font_size * 0.9)

        image.save(out_file)
    except Exception as exc:
        print(f"[Warn] Skip wordcloud '{title}': {exc}")


def collapse_wordcloud_freqs(
    freq_dict: dict[str, float],
    aspect_en: str,
    *,
    allow_raw_fallback: bool = False,
) -> dict[str, float]:
    collapsed: dict[str, float] = {}

    for raw_term, score in sorted(freq_dict.items(), key=lambda item: item[1], reverse=True):
        phrase_display = compact_keyword(raw_term, aspect_en)
        if phrase_display:
            display = SIMPLE_DISPLAY_MAP.get(phrase_display, phrase_display)
        elif allow_raw_fallback:
            display = normalize_term(raw_term)
        else:
            continue

        display = str(display).strip()
        if not display or display in NOISE_WORDS:
            continue
        collapsed[display] = collapsed.get(display, 0.0) + float(score)

    return dict(sorted(collapsed.items(), key=lambda item: item[1], reverse=True))


def count_compact_keyword_supports(
    texts: list[str],
    aspect_en: str,
) -> dict[str, int]:
    allowed_labels = ASPECT_ALLOWED_DISPLAY_LABELS.get(aspect_en)
    label_counts: dict[str, int] = {}

    for text in texts:
        tokens = [tok for tok in str(text).split() if tok.strip()]
        if not tokens:
            continue

        seen_in_doc: set[str] = set()
        for n in (1, 2, 3):
            for idx in range(0, len(tokens) - n + 1):
                span_tokens = tokens[idx:idx + n]
                if _phrase_is_false_negative(span_tokens):
                    continue
                span = " ".join(span_tokens).replace("_", " ")
                phrase_label = compact_keyword(span, aspect_en)
                if not phrase_label:
                    continue

                display_label = SIMPLE_DISPLAY_MAP.get(phrase_label, phrase_label)
                if allowed_labels and display_label not in allowed_labels:
                    continue
                if display_label in seen_in_doc:
                    continue

                seen_in_doc.add(display_label)
                label_counts[display_label] = label_counts.get(display_label, 0) + 1

    return dict(sorted(label_counts.items(), key=lambda item: (-item[1], item[0])))


def build_negative_aspect_wordcloud_freqs(
    df: pd.DataFrame,
    sent_df: pd.DataFrame,
) -> dict[str, float]:
    combined: dict[str, float] = {}

    for column, aspect_en, _aspect_cn in ASPECT_SPECS:
        series = df[column]
        if isinstance(series, pd.DataFrame):
            series = series.iloc[:, 0]

        score_col = TEXT_TO_SCORE_COL.get(column)
        if score_col and score_col in df.columns:
            negative_texts = collect_low_texts_by_score(series, df[score_col])
        else:
            negative_texts = collect_low_texts(series, sent_df[TEXT_TO_SENTIMENT_COL[column]])

        label_counts = count_compact_keyword_supports(negative_texts, aspect_en)
        for label, count in label_counts.items():
            if count < 4:
                continue
            combined[label] = combined.get(label, 0.0) + float(np.log1p(count))

    return dict(sorted(combined.items(), key=lambda item: item[1], reverse=True))


def build_satisfied_wordcloud_freqs(
    texts: list[str],
    *,
    top_n: int,
    blacklist: set[str],
) -> dict[str, float]:
    ranked, all_freqs = extract_tfidf_keywords(
        texts,
        top_n=max(top_n, 80),
        blacklist=blacklist,
    )
    source_freqs = dict(all_freqs)
    if not source_freqs and ranked:
        source_freqs = {term: score for term, score in ranked}

    theme_freqs: dict[str, float] = {}
    raw_kept: dict[str, float] = {}
    theme_supports: dict[str, dict[str, float]] = {}

    for raw_term, score in sorted(source_freqs.items(), key=lambda item: item[1], reverse=True):
        norm = normalize_term(raw_term).strip()
        if not norm:
            continue

        tokens = [tok for tok in norm.split() if tok.strip()]
        if any(tok in SATISFIED_WORDCLOUD_STOPWORDS for tok in tokens):
            continue

        matched_theme = _match_satisfied_theme(norm)
        support_label = _canonicalize_satisfied_support(norm)

        if matched_theme is not None:
            theme_freqs[matched_theme] = theme_freqs.get(matched_theme, 0.0) + float(score)
            if (
                support_label
                and support_label != matched_theme
                and len(tokens) <= 2
                and score >= MIN_WORDCLOUD_SECONDARY_SCORE
            ):
                theme_supports.setdefault(matched_theme, {})
                theme_supports[matched_theme][support_label] = max(
                    theme_supports[matched_theme].get(support_label, 0.0),
                    float(score),
                )
            continue

        if (
            len(tokens) == 1
            and tokens[0] in SATISFIED_WORDCLOUD_RAW_ALLOWLIST
            and score >= 0.005
        ):
            raw_kept[tokens[0]] = raw_kept.get(tokens[0], 0.0) + float(score)
        elif (
            support_label
            and len(tokens) <= 2
            and score >= MIN_WORDCLOUD_SECONDARY_SCORE
        ):
            raw_kept[support_label] = raw_kept.get(support_label, 0.0) + float(score)

    combined = {**raw_kept}
    for theme, score in theme_freqs.items():
        combined[theme] = combined.get(theme, 0.0) + score
    for theme, support_map in theme_supports.items():
        support_items = sorted(support_map.items(), key=lambda item: item[1], reverse=True)
        for label, score in support_items[:MAX_SATISFIED_SUPPORTS_PER_THEME]:
            if label == theme:
                continue
            combined[label] = combined.get(label, 0.0) + score

    ordered = sorted(combined.items(), key=lambda item: item[1], reverse=True)
    theme_names = set(SATISFIED_WORDCLOUD_THEME_MAP)
    selected: list[tuple[str, float]] = []
    secondary_count = 0
    for label, score in ordered:
        if label in theme_names:
            selected.append((label, score))
            continue
        if secondary_count >= MAX_SATISFIED_SECONDARY_WORDS:
            continue
        secondary_count += 1
        selected.append((label, score))

    return dict(selected[:top_n])


def build_dissatisfied_wordcloud_freqs(
    ranked_items: list[tuple[str, float]],
    freq_dict: dict[str, float],
    *,
    aspect_theme_freqs: dict[str, float] | None = None,
    top_n: int,
) -> dict[str, float]:
    combined = dict(aspect_theme_freqs or {})
    if aspect_theme_freqs:
        return dict(sorted(combined.items(), key=lambda item: item[1], reverse=True)[:top_n])
    if not combined:
        combined = collapse_wordcloud_freqs(freq_dict, "dissatisfied")
    support_by_theme: dict[str, tuple[str, float]] = {}

    for raw_term, score in ranked_items:
        norm = normalize_term(raw_term).strip()
        if not norm or score < MIN_WORDCLOUD_SECONDARY_SCORE:
            continue
        tokens = [tok for tok in norm.split() if tok.strip()]
        if not tokens:
            continue
        if any(tok in DISSATISFIED_WORDCLOUD_STOPWORDS for tok in tokens):
            continue
        if len(tokens) > 3:
            continue
        if _phrase_is_false_negative(tokens):
            continue
        theme = _match_dissatisfied_theme(norm)
        if theme is not None:
            if aspect_theme_freqs and theme not in aspect_theme_freqs:
                continue
            label = SIMPLE_DISPLAY_MAP.get(compact_keyword(norm, "dissatisfied"), norm.replace(" ", ""))
            old = support_by_theme.get(theme)
            if label == theme:
                continue
            if old is None or score > old[1]:
                support_by_theme[theme] = (label, float(score))
            continue

    for theme, (label, score) in support_by_theme.items():
        if theme not in combined:
            combined[theme] = score
        if label != theme:
            combined[label] = score

    return dict(sorted(combined.items(), key=lambda item: item[1], reverse=True)[:top_n])


def plot_wordcloud_grid(
    aspect_freqs: dict[str, dict[str, float]],
    aspect_labels: dict[str, str],
    font_path: str | None,
) -> None:
    if not HAS_PLOT_LIBS:
        return

    try:
        fig, axes = plt.subplots(4, 2, figsize=(14, 16), dpi=200)
        axes_flat = axes.ravel()

        for idx, (_, aspect_en, aspect_cn) in enumerate(ASPECT_SPECS):
            ax = axes_flat[idx]
            freqs = aspect_freqs.get(aspect_en, {})
            if freqs:
                wc = WordCloud(
                    font_path=font_path,
                    width=800,
                    height=400,
                    background_color="white",
                    colormap="viridis",
                ).generate_from_frequencies(freqs)
                ax.imshow(wc, interpolation="bilinear")
            ax.set_title(aspect_labels.get(aspect_en, aspect_cn))
            ax.axis("off")

        for idx in range(len(ASPECT_SPECS), len(axes_flat)):
            axes_flat[idx].axis("off")

        plt.tight_layout()
        fig.savefig(FIG_DIR / "fig_wordcloud_grid.png", dpi=200, bbox_inches="tight")
        plt.close(fig)
    except Exception as exc:
        print(f"[Warn] Skip wordcloud grid: {exc}")


def plot_keyword_bars(
    top_keywords: dict[str, list[DisplayKeywordItem]], aspect_labels: dict[str, str]
) -> None:
    if not HAS_PLOT_LIBS:
        return

    try:
        plot_items: list[tuple[str, list[DisplayKeywordItem]]] = []
        for _, aspect_en, aspect_cn in ASPECT_SPECS:
            collapsed_items = top_keywords.get(aspect_en, [])[:5]
            if collapsed_items:
                plot_items.append((aspect_labels.get(aspect_en, aspect_cn), collapsed_items))

        if not plot_items:
            return

        ncols = 2
        nrows = int(np.ceil(len(plot_items) / ncols))
        fig, axes = plt.subplots(nrows, ncols, figsize=(14, 4.2 * nrows), dpi=200)
        axes_flat = np.atleast_1d(axes).ravel()

        for idx, (title, collapsed_items) in enumerate(plot_items):
            ax = axes_flat[idx]

            if collapsed_items:
                words = [display for display, _, _, _ in collapsed_items]
                scores = [score for _, score, _, _ in collapsed_items]
                colors = gradient_colors(len(collapsed_items))
                if not colors:
                    colors = ["#4C78A8"] * len(collapsed_items)
                ax.barh(words[::-1], scores[::-1], color=colors)

            ax.set_title(title)
            ax.set_xlabel("关键词得分")

        for idx in range(len(plot_items), len(axes_flat)):
            axes_flat[idx].axis("off")

        plt.tight_layout()
        fig.savefig(FIG_DIR / "fig_keywords_bar.png", dpi=200, bbox_inches="tight")
        plt.close(fig)
    except Exception as exc:
        print(f"[Warn] Skip keyword bar plot: {exc}")


def main() -> None:
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    df, sent_df = prepare_inputs()

    required_cols = [c for c, _, _ in ASPECT_SPECS + EXTRA_SPECS]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise KeyError(f"Missing required columns: {missing_cols}")

    required_sent_cols = [TEXT_TO_SENTIMENT_COL[c] for c in required_cols]
    missing_sent_cols = [c for c in required_sent_cols if c not in sent_df.columns]
    if missing_sent_cols:
        raise KeyError(f"Missing sentiment columns: {missing_sent_cols}")

    font_path = choose_chinese_font()

    table_aspect_keys = {aspect_en for _, aspect_en, _ in ASPECT_SPECS}
    rows: list[dict[str, object]] = []
    final_keywords: dict[str, list[DisplayKeywordItem]] = {}
    ranked_keywords: dict[str, list[tuple[str, float]]] = {}
    tfidf_freqs: dict[str, dict[str, float]] = {}
    aspect_labels: dict[str, str] = {}
    candidate_top_n = 60

    for column, aspect_en, aspect_cn in ASPECT_SPECS + EXTRA_SPECS:
        series = df[column]
        if isinstance(series, pd.DataFrame):
            series = series.iloc[:, 0]

        sent_col = TEXT_TO_SENTIMENT_COL[column]
        if column == "most_satisfied_text":
            positive_texts = collect_labeled_texts(series)
            negative_texts = collect_labeled_texts(
                df["most_dissatisfied_text"],
                drop_non_complaint=True,
            )
        elif column == "most_dissatisfied_text":
            negative_texts = collect_labeled_texts(series, drop_non_complaint=True)
            positive_texts = collect_labeled_texts(df["most_satisfied_text"])
        else:
            score_col = TEXT_TO_SCORE_COL.get(column)
            if score_col and score_col in df.columns:
                negative_texts = collect_low_texts_by_score(series, df[score_col])
                positive_texts = collect_high_texts_by_score(series, df[score_col])
            else:
                negative_texts = collect_low_texts(series, sent_df[sent_col])
                positive_texts = collect_high_texts(series, sent_df[sent_col])

        blacklist = set(NOISE_WORDS) | ASPECT_BLACKLIST.get(column, set())
        top20, all_freqs = extract_contrastive_keywords(
            negative_texts,
            positive_texts,
            top_n=candidate_top_n,
            blacklist=blacklist,
            prefer_positive=(column == "most_satisfied_text"),
        )

        if not top20 and column == "most_satisfied_text":
            fallback = [filter_noise_tokens(t) for t in collect_texts(series)]
            fallback = [t for t in fallback if t.strip()]
            top20, all_freqs = extract_contrastive_keywords(
                fallback,
                [],
                top_n=candidate_top_n,
                blacklist=blacklist,
            )
        elif not top20:
            top20, all_freqs = extract_negative_cue_keywords(
                negative_texts,
                top_n=candidate_top_n,
                blacklist=blacklist,
            )

        ranked_keywords[aspect_en] = top20
        tfidf_freqs[aspect_en] = all_freqs
        aspect_labels[aspect_en] = aspect_cn
        display_items = collapse_keyword_items(top20, aspect_en, top_n=20)
        display_items = filter_aspect_consistent_labels(display_items, aspect_en)
        if (
            aspect_en in ASPECT_ALLOWED_DISPLAY_LABELS
            and aspect_en not in {"satisfied", "dissatisfied"}
            and len(display_items) < MIN_DISPLAY_ITEMS_FOR_ASPECT
        ):
            min_support = max(
                MIN_FALLBACK_DOC_COUNT,
                int(np.ceil(len(negative_texts) * MIN_FALLBACK_SUPPORT_RATIO)),
            )
            fallback_items = [
                item
                for item in fallback_compact_keyword_items(
                    negative_texts,
                    aspect_en,
                    top_n=20,
                )
                if item[1] >= min_support
            ]
            display_items = merge_display_keyword_items(
                display_items,
                fallback_items,
                top_n=20,
            )
            display_items = filter_aspect_consistent_labels(display_items, aspect_en)

        final_keywords[aspect_en] = display_items

        if aspect_en not in table_aspect_keys:
            continue

        for rank, (display_keyword, score, raw_keyword, score_type) in enumerate(display_items, start=1):
            kw_type = "positive_theme_phrase" if column == "most_satisfied_text" else "negative_theme_phrase"
            rows.append(
                {
                    "aspect": aspect_en,
                    "aspect_cn": aspect_cn,
                    "rank": rank,
                    "keyword": display_keyword,
                    "keyword_raw": raw_keyword,
                    "keyword_display": display_keyword,
                    "tfidf_score": score,
                    "score_type": score_type,
                    "keyword_type": kw_type,
                }
            )

    keywords_df = pd.DataFrame(
        rows,
        columns=[
            "aspect",
            "aspect_cn",
            "rank",
            "keyword",
            "keyword_raw",
            "keyword_display",
            "tfidf_score",
            "score_type",
            "keyword_type",
        ],
    )
    keywords_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    try:
        with pd.ExcelWriter(OUTPUT_XLSX) as writer:
            keywords_df.to_excel(writer, index=False, sheet_name="keywords_top")
    except Exception as exc:
        print(f"[Warn] Skip Excel export: {exc}")

    print()
    print("[Top Keywords]")
    for _, aspect_en, aspect_cn in ASPECT_SPECS:
        items = final_keywords.get(aspect_en, [])
        if not items:
            print()
            print(f"{aspect_cn} ({aspect_en}): no keywords extracted")
            continue
        print()
        print(f"{aspect_cn} ({aspect_en})")
        for rank, (keyword, score, _raw_keyword, score_type) in enumerate(items, start=1):
            print(f"{rank:>4} {keyword:<12} {score:.6f} [{score_type}]")

    enable_plots = os.environ.get("ENABLE_PLOTS", "0") == "1"
    if HAS_PLOT_LIBS and enable_plots:
        display_freqs = {
            aspect_en: {display: score for display, score, _raw_keyword, _score_type in items}
            for aspect_en, items in final_keywords.items()
            if aspect_en in table_aspect_keys
        }
        plot_wordcloud_grid(
            aspect_freqs=display_freqs,
            aspect_labels=aspect_labels,
            font_path=font_path,
        )
        plot_keyword_bars(
            top_keywords={k: v for k, v in final_keywords.items() if k in table_aspect_keys},
            aspect_labels=aspect_labels,
        )

        satisfied_freqs = build_satisfied_wordcloud_freqs(
            collect_labeled_texts(df["most_satisfied_text"]),
            top_n=24,
            blacklist=set(NOISE_WORDS) | ASPECT_BLACKLIST.get("most_satisfied_text", set()),
        )
        if not satisfied_freqs:
            satisfied_freqs = (
                collapse_wordcloud_freqs(
                    tfidf_freqs.get("satisfied", {}),
                    "satisfied",
                    allow_raw_fallback=True,
                )
                or tfidf_freqs.get("satisfied", {})
            )
        aspect_negative_freqs = build_negative_aspect_wordcloud_freqs(df, sent_df)
        build_wordcloud(
            satisfied_freqs,
            "最满意词云",
            FIG_DIR / "fig_wordcloud_satisfied.png",
            font_path,
        )
        dissatisfied_freqs = build_dissatisfied_wordcloud_freqs(
            ranked_keywords.get("dissatisfied", []),
            tfidf_freqs.get("dissatisfied", {}),
            aspect_theme_freqs=aspect_negative_freqs,
            top_n=24,
        )
        if not dissatisfied_freqs:
            dissatisfied_freqs = {
                display: score
                for display, score, _raw_keyword, _score_type in final_keywords.get("dissatisfied", [])
            }
        build_wordcloud(
            dissatisfied_freqs,
            "最不满意词云",
            FIG_DIR / "fig_wordcloud_dissatisfied.png",
            font_path,
        )
    else:
        print("[Warn] Plotting skipped (set ENABLE_PLOTS=1 to enable). CSV output generated.")

    print()
    print("[Method] Contrastive TF-IDF over phrase n-grams (1-3), with cue-based filtering")
    print(f"[Done] Keywords saved: {OUTPUT_CSV}")
    print(f"[Done] Figures saved in: {FIG_DIR}")


if __name__ == "__main__":
    main()
