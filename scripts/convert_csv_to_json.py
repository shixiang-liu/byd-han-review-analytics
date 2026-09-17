#!/usr/bin/env python3
"""
CSV to JSON Converter for BYD Han Dashboard
将outputs/tables中的CSV文件转换为public/data中的JSON文件
"""

import csv
import json
import os
from pathlib import Path

# 路径配置
BASE_DIR = Path(__file__).parent.parent
CSV_DIR = BASE_DIR / "outputs" / "tables"
JSON_DIR = BASE_DIR / "frontend" / "public" / "data"


def ensure_dir(path: Path):
    """确保目录存在"""
    path.mkdir(parents=True, exist_ok=True)


def read_csv(filename: str) -> list[dict]:
    """读取CSV文件，返回字典列表"""
    filepath = CSV_DIR / filename
    if not filepath.exists():
        print(f"警告: {filepath} 不存在")
        return []

    with open(filepath, "r", encoding="utf-8-sig") as f:
        # 使用utf-8-sig处理BOM标记
        reader = csv.DictReader(f)
        return list(reader)


def convert_ipa_results():
    """转换IPA四象限数据"""
    data = read_csv("ipa_results.csv")

    items = []
    for row in data:
        items.append({
            "aspect": row["aspect"],
            "aspectCn": row["aspect_cn"],
            "performance": float(row["P"]),
            "importance": float(row["I"]),
            "quadrant": row["quadrant"],
            "quadrantName": row["quadrant_name"],
            "action": row["action"],
            "priorityScore": float(row["priority_score"]),
            "priorityRank": int(row["priority_rank"])
        })

    result = {
        "items": items,
        "quadrantDefinitions": {
            "Q1": {"name": "优势保持区", "description": "高重要性+高表现，保持并宣传", "color": "#10b981"},
            "Q2": {"name": "重点改进区", "description": "高重要性+低表现，紧急投入改进", "color": "#ef4444"},
            "Q3": {"name": "低优先区", "description": "低重要性+低表现，暂不处理", "color": "#64748b"},
            "Q4": {"name": "过度投入区", "description": "低重要性+高表现，调整资源", "color": "#f59e0b"}
        }
    }

    output_path = JSON_DIR / "ipa-quadrant.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"已生成: {output_path}")
    return items


def convert_performance_scores():
    """转换绩效得分数据"""
    data = read_csv("performance_scores.csv")

    items = []
    for row in data:
        items.append({
            "aspect": row["aspect"],
            "aspectCn": row["aspect_cn"],
            "scoreMean": float(row["score_mean"]),
            "sentimentMean": float(row["sentiment_mean"]),
            "nScore": int(row["n_score"]),
            "nSentiment": int(row["n_sentiment"]),
            "scoreNorm": float(row["score_norm"]),
            "sentimentNorm": float(row["sentiment_norm"]),
            "performance": float(row["performance"])
        })

    result = {"items": items}

    output_path = JSON_DIR / "performance-scores.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"已生成: {output_path}")
    return items


def convert_keywords():
    """转换关键词数据"""
    data = read_csv("keywords_top.csv")

    keywords = []
    for row in data:
        keywords.append({
            "aspect": row["aspect"],
            "aspectCn": row["aspect_cn"],
            "rank": int(row["rank"]),
            "keyword": row["keyword_display"],
            "keywordRaw": row["keyword_raw"],
            "tfidfScore": float(row["tfidf_score"]) if row["tfidf_score"] else 0,
            "scoreType": row["score_type"],
            "keywordType": row["keyword_type"]
        })

    # 按aspect分组
    by_aspect = {}
    for kw in keywords:
        aspect = kw["aspect"]
        if aspect not in by_aspect:
            by_aspect[aspect] = []
        by_aspect[aspect].append(kw)

    result = {
        "keywords": keywords,
        "byAspect": by_aspect,
        "totalCount": len(keywords)
    }

    output_path = JSON_DIR / "keywords-analysis.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"已生成: {output_path}")


def convert_sentiment_trend():
    """转换情感趋势数据"""
    data = read_csv("aug_sentiment_trend.csv")

    trend = []
    aspects = ["space", "driving", "range", "appearance", "interior", "value", "smart"]
    aspect_names = {
        "space": "空间",
        "driving": "驾驶感受",
        "range": "续航",
        "appearance": "外观",
        "interior": "内饰",
        "value": "性价比",
        "smart": "智能化"
    }

    for row in data:
        # 构建月份字符串
        month = f"{row['review_year']}-{row['review_month']}"

        # 计算各维度得分
        aspect_scores = {}
        valid_scores = []
        for aspect in aspects:
            col_name = f"score_{aspect}"
            if col_name in row and row[col_name]:
                score = float(row[col_name])
                aspect_scores[aspect] = score
                valid_scores.append(score)

        # 计算总体平均
        overall = sum(valid_scores) / len(valid_scores) if valid_scores else 0

        trend.append({
            "month": month,
            "year": int(row["review_year"]),
            "monthNum": int(row["review_month"]),
            "overall": round(overall, 2),
            "aspects": aspect_scores
        })

    result = {
        "trend": trend,
        "aspects": aspects,
        "aspectNames": aspect_names,
        "totalCount": len(trend)
    }

    output_path = JSON_DIR / "sentiment-trend.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"已生成: {output_path}")


def convert_causal_effects():
    """转换因果效应数据"""
    data = read_csv("dml_results.csv")

    effects = []
    for row in data:
        effects.append({
            "aspect": row["aspect"],
            "aspectCn": row["aspect_cn"],
            "theta": float(row["theta"]),
            "se": float(row["se"]),
            "ciLower": float(row["ci_lower"]),
            "ciUpper": float(row["ci_upper"]),
            "pValue": float(row["p_value"]),
            "nUsed": int(row["n_used"])
        })

    # 按theta排序
    effects.sort(key=lambda x: x["theta"], reverse=True)

    result = {
        "effects": effects,
        "totalCount": len(effects)
    }

    output_path = JSON_DIR / "causal-effects.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"已生成: {output_path}")


def convert_prca_results():
    """转换PRCA决策建议数据"""
    data = read_csv("deep_prca_results.csv")

    recommendations = []
    for row in data:
        recommendations.append({
            "aspect": row["aspect"],
            "penaltyWeight": float(row["penalty_weight"]),
            "rewardWeight": float(row["reward_weight"]),
            "classification": row["classification"],
            "performance": float(row["performance"]),
            "doi": float(row["doi"]) if row["doi"] else 0
        })

    result = {
        "recommendations": recommendations,
        "totalCount": len(recommendations)
    }

    output_path = JSON_DIR / "prca-recommendations.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"已生成: {output_path}")


def create_dashboard_metrics(ipa_items: list):
    """创建Dashboard KPI汇总数据"""
    # 从IPA数据中统计
    q2_count = len([i for i in ipa_items if i["quadrant"] == "Q2"])
    q1_count = len([i for i in ipa_items if i["quadrant"] == "Q1"])

    result = {
        "sampleCount": 8424,
        "analysisDimensions": 7,
        "priorityIssues": q2_count,
        "actionCount": q1_count,
        "analysisWindow": {
            "start": "2020-08",
            "end": "2026-02"
        },
        "projectName": "比亚迪汉口碑分析"
    }

    output_path = JSON_DIR / "dashboard-metrics.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"已生成: {output_path}")


def create_decision_recommendations(ipa_items: list, keywords_data: dict):
    """创建决策建议数据"""
    # 从IPA数据构建建议
    recommendations = []

    for item in ipa_items:
        aspect = item["aspect"]
        keywords = []

        # 获取该维度的关键词
        if aspect in keywords_data:
            keywords = [kw["keyword"] for kw in keywords_data[aspect][:5]]

        recommendations.append({
            "aspect": item["aspect"],
            "aspectCn": item["aspectCn"],
            "quadrant": item["quadrant"],
            "quadrantName": item["quadrantName"],
            "priorityRank": item["priorityRank"],
            "recommendation": item["action"],
            "keywords": keywords
        })

    # 按优先级排序
    recommendations.sort(key=lambda x: x["priorityRank"])

    result = {
        "recommendations": recommendations,
        "totalCount": len(recommendations)
    }

    output_path = JSON_DIR / "decision-recommendations.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"已生成: {output_path}")


def main():
    """主函数"""
    print("=" * 50)
    print("CSV to JSON Converter")
    print("=" * 50)

    # 确保输出目录存在
    ensure_dir(JSON_DIR)

    # 转换各数据文件
    ipa_items = convert_ipa_results()
    performance_items = convert_performance_scores()
    convert_keywords()
    convert_sentiment_trend()
    convert_causal_effects()
    convert_prca_results()

    # 读取关键词数据用于构建决策建议
    keywords_data = {}
    keywords_path = JSON_DIR / "keywords-analysis.json"
    if keywords_path.exists():
        with open(keywords_path, "r", encoding="utf-8") as f:
            keywords_json = json.load(f)
            keywords_data = keywords_json.get("byAspect", {})

    # 创建汇总数据
    create_dashboard_metrics(ipa_items)
    create_decision_recommendations(ipa_items, keywords_data)

    print("=" * 50)
    print("转换完成!")
    print("=" * 50)


if __name__ == "__main__":
    main()