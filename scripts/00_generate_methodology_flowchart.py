from __future__ import annotations

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIGURE_PATH = PROJECT_ROOT / "figures" / "fig_methodology_flowchart.png"

# 更沉稳清晰的学术色系设置
COLORS = {
    "bg": "#FAFAFA",
    "stage": "#F0F2F5",
    "edge": "#CBD5E1",
    "shadow": "#94A3B8",
    "text": "#1E293B",
    "subtitle": "#475569",
    "muted": "#64748B",
    "line": "#94A3B8",
    "theme_blue": "#0284C7",   
    "theme_teal": "#0F766E",  
    "theme_purple": "#7C3AED", 
    "theme_gold": "#B45309",   
}

def configure_fonts():
    chinese_candidates = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/msyhbd.ttc",
        "C:/Windows/Fonts/simhei.ttf",
    ]
    chinese = None
    for candidate in chinese_candidates:
        path = Path(candidate)
        if not path.exists(): continue
        try:
            font_manager.fontManager.addfont(str(path))
            chinese = font_manager.FontProperties(fname=str(path))
            break
        except Exception: continue

    if chinese:
        family = chinese.get_name()
        plt.rcParams["font.family"] = family
        plt.rcParams["font.sans-serif"] = [family, "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

def draw_stage(ax, y_top, y_bottom, num, title):
    # 横向浅色大背景分隔带
    band = FancyBboxPatch(
        (0.02, y_bottom), 0.96, y_top - y_bottom,
        boxstyle="round,pad=0", edgecolor="none", facecolor=COLORS["stage"], alpha=0.4, zorder=0
    )
    ax.add_patch(band)
    
    # 阶段序号与标题 (置于左侧)
    badge_w, badge_h = 0.08, 0.06
    badge_x = 0.025
    badge_y = y_top - badge_h - 0.015

    badge = FancyBboxPatch(
        (badge_x, badge_y), badge_w, badge_h,
        boxstyle="round,pad=0.005", lw=0.5, edgecolor=COLORS["edge"], facecolor=COLORS["theme_blue"], zorder=2
    )
    ax.add_patch(badge)
    
    ax.text(badge_x + badge_w/2, badge_y + badge_h/2, f"Stage {num}\n{title}", 
            color="#FFFFFF", fontweight="bold", fontsize=10, ha="center", va="center", zorder=3, linespacing=1.3)

def card(ax, cx, cy, w, h, title, body, theme, hl=False):
    x, y = cx - w/2, cy - h/2
    
    # 底部阴影
    shadow = FancyBboxPatch((x+0.004, y-0.005), w, h, boxstyle="round,pad=0.005",
                            lw=0, facecolor=COLORS["shadow"], alpha=0.15, zorder=1)
    ax.add_patch(shadow)
    
    # 主面板
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.005",
                         lw=1.5 if hl else 1.0, edgecolor=COLORS[theme] if hl else COLORS["edge"], facecolor="#FFFFFF", zorder=2)
    ax.add_patch(box)
    
    # 顶部彩条标识类属
    ax.plot([x+0.01, x+w-0.01], [y+h-0.002, y+h-0.002], color=COLORS[theme], linewidth=4, solid_capstyle="round", zorder=3)
    
    # 文本与标题
    ax.text(cx, cy + h*0.20, title, ha="center", va="center", color=COLORS["text"], fontweight="bold", fontsize=12, zorder=4)
    ax.text(cx, cy - h*0.18, body, ha="center", va="center", color=COLORS["muted"], fontsize=9.5, linespacing=1.6, zorder=4)

def draw_arrow(ax, x1, y1, x2, y2, style="arc3,rad=0.0", color=COLORS["line"]):
    # 如果完全垂直
    if abs(x1 - x2) < 0.001:
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", lw=1.5, color=color, shrinkA=0, shrinkB=0,
                                    connectionstyle=style), zorder=1)
    # 如果需要直线折叠（先垂直后水平等），采用简单直线绘制然后带箭头
    else:
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", lw=1.5, color=color, shrinkA=0, shrinkB=0,
                                    connectionstyle=style), zorder=1)

def draw_line(ax, x1, y1, x2, y2, color=COLORS["line"]):
    ax.plot([x1, x2], [y1, y2], color=color, lw=1.5, zorder=1)

def main():
    configure_fonts()
    fig, ax = plt.subplots(figsize=(16, 12), dpi=300)
    fig.patch.set_facecolor(COLORS["bg"])
    ax.set_facecolor(COLORS["bg"])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # === Header ===
    ax.text(0.05, 0.97, "研 究 技 术 路 线 与 实 施 流 程", fontsize=24, color=COLORS["text"], fontweight="heavy")
    ax.text(0.05, 0.94, "Methodology Framework of the Sentiment-driven and Causal-Enhanced Decision Research", 
            fontsize=12, color=COLORS["subtitle"], fontfamily="sans-serif")

    # 定义 5 个 Stage 背景横向分割
    draw_stage(ax, 0.92, 0.78, "01", "多源数据采集")
    draw_stage(ax, 0.77, 0.63, "02", "清洗与预处理")
    draw_stage(ax, 0.62, 0.40, "03", "量化建模与校验")
    draw_stage(ax, 0.39, 0.24, "04", "整合矩阵诊断")
    draw_stage(ax, 0.23, 0.06, "05", "产品迭代决策")

    # === 列定义与节点精确坐标 === (采用极其规整的四阵列)
    C1, C2, C3, C4 = 0.22, 0.44, 0.66, 0.88
    
    nodes = {
        # S1 (y=0.85) 横向并列
        "raw":    (C1, 0.85, 0.17, 0.08, "原始评价长文本", "汽车之家车主原始发帖\n(标题 Title 与内容 Content)", "theme_blue"),
        "struct": (C2, 0.85, 0.17, 0.08, "车型与发帖元数据", "购买的具体车型配置 (Model)\n评价发布的日期时间 (Date)", "theme_blue"),
        "dict":   (C4, 0.85, 0.17, 0.08, "分词停用词库", "中文通用停用词表\n(stopwords.txt 文件加载)", "theme_blue"),

        # S2 (y=0.70)
        "nlp": (C1, 0.70, 0.17, 0.08, "自然语言分词", "基于关键词词库的分词处理\n剔除无意义的语气助词", "theme_blue"),
        "eda": (C2, 0.70, 0.17, 0.08, "原始数据清洗", "车型分类标签的合并归一化\n时间序列数据格式转化", "theme_blue"),

        # S3 (双排: y=0.55 和 y=0.46)
        # 上排
        "tfidf": (C1, 0.55, 0.17, 0.08, "TF-IDF 文本特征化", "将核心业务词汇转化为向量\n(将发帖转化为可计算结构)", "theme_teal"),
        "sent":  (C2, 0.55, 0.17, 0.08, "RoBERTa 情感推断", "利用深度学习测算文本极性\n(弥补缺失的口碑评分环节)", "theme_teal"),
        "xgb":   (C3, 0.55, 0.17, 0.08, "XGBoost + SHAP", "训练总体情感预测回归模型\n(得出各个特征的基准贡献)", "theme_purple"),
        # 下排
        "perf":  (C2, 0.45, 0.17, 0.08, "隐性满意度拟合", "将情绪极性作为 P 轴指标\n(评估车主对各维度的感观)", "theme_teal", True),
        "dml":   (C3, 0.45, 0.17, 0.08, "DML 因果效应提取", "剥离由于车型选择带来的偏误\n(客观校准 I 轴实际干预权重)", "theme_purple", True),
        "prca":  (C4, 0.45, 0.17, 0.08, "PRCA 非对称分析", "探测“抱怨”与“惊喜”间的差异\n(细化 I 轴关键影响边界)", "theme_purple", True),

        # S4 (综合汇总，横跨中央区域)
        "ipa": (0.55, 0.315, 0.65, 0.08, "因果增强型四象限 IPA 产品需求诊断模型", "以重构绩效 (P) 为横轴，以经 DML 因果推断与 PRCA 分析双重校准的特征权重 (I) 为纵轴\n构建 IPA 矩阵判定优先级，并通过 TF-IDF 表征结果进行现象级溯源", "theme_gold", True),

        # S5 (落点并列)
        "o1": (0.25, 0.145, 0.17, 0.08, "重点改进区", "针对高权重低满意度特征\n(集中资源改善内饰异味)", "theme_teal"),
        "o2": (0.45, 0.145, 0.17, 0.08, "优势保持区", "针对高权重高满意度特征\n(维持当前底盘及动力标准)", "theme_teal"),
        "o3": (0.65, 0.145, 0.17, 0.08, "延缓观察区", "针对低权重低满意度特征\n(暂缓资源投入/次优级监控)", "theme_blue"),
        "o4": (0.85, 0.145, 0.17, 0.08, "供给冗余区", "针对低权重高满意度特征\n(剥离冗余成本/适度精简)", "theme_blue"),
    }

    # 绘制对象
    for k, v in nodes.items():
        is_hl = v[7] if len(v) > 7 else False
        card(ax, v[0], v[1], v[2], v[3], v[4], v[5], v[6], hl=is_hl)

    # =============== 箭矢连线逻辑 (绝不交叉碰撞的工程绘图流) ===============
    
    # 纵向主体骨架
    aw = 0.04 # 距边界的安全裕度
    
    # S1 -> S2的纵向与结合
    draw_arrow(ax, C1, 0.81, C1, 0.74) # raw -> nlp
    draw_arrow(ax, C2, 0.81, C2, 0.74) # struct -> eda
    # dict 向横进入 nlp 上端
    draw_line(ax, C4, 0.78, C4, 0.76)
    draw_line(ax, C4, 0.76, C1+0.04, 0.76)
    draw_arrow(ax, C1+0.04, 0.76, C1+0.04, 0.74)

    # S2 -> S3 主流
    # nlp -> tfidf | sent | xgb
    draw_arrow(ax, C1, 0.66, C1, 0.59) # nlp -> tfidf
    draw_line(ax, C1, 0.63, C3-0.03, 0.63) # nlp 横向供线
    draw_arrow(ax, C2, 0.63, C2, 0.59)   # to sent
    draw_arrow(ax, C3-0.03, 0.63, C3-0.03, 0.59) # to xgb
    
    # eda 被供给给 xgb
    draw_line(ax, C2, 0.66, C2, 0.65)
    draw_line(ax, C2, 0.65, C3+0.03, 0.65)
    draw_arrow(ax, C3+0.03, 0.65, C3+0.03, 0.59) # to xgb

    # S3 内部上下级推理流传
    # sent -> perf
    draw_arrow(ax, C2, 0.51, C2, 0.49)
    # xgb -> dml 和 prca
    draw_arrow(ax, C3, 0.51, C3, 0.49) # to dml
    draw_line(ax, C3+0.04, 0.51, C3+0.04, 0.48)
    draw_line(ax, C3+0.04, 0.48, C4, 0.48)
    draw_arrow(ax, C4, 0.48, C4, 0.49) # to prca

    # S3 -> S4 矩阵汇聚
    y_汇聚 = 0.38
    draw_line(ax, C1, 0.51, C1, y_汇聚)
    draw_line(ax, C2, 0.41, C2, y_汇聚)
    draw_line(ax, C3, 0.41, C3, y_汇聚)
    draw_line(ax, C4, 0.41, C4, y_汇聚)
    
    bus_x1, bus_x2 = C1, C4
    draw_line(ax, bus_x1, y_汇聚, bus_x2, y_汇聚)
    
    # 集中注入 IPA
    draw_arrow(ax, 0.55, y_汇聚, 0.55, 0.355)

    # S4 -> S5 散发流出
    y_散发 = 0.21
    draw_line(ax, 0.55, 0.275, 0.55, y_散发)
    draw_line(ax, 0.25, y_散发, 0.85, y_散发)
    
    draw_arrow(ax, 0.25, y_散发, 0.25, 0.185)
    draw_arrow(ax, 0.45, y_散发, 0.45, 0.185)
    draw_arrow(ax, 0.65, y_散发, 0.65, 0.185)
    draw_arrow(ax, 0.85, y_散发, 0.85, 0.185)

    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE_PATH, bbox_inches="tight", pad_inches=0.015, facecolor=COLORS["bg"])
    plt.close(fig)
    print(f"Flowchart successfully updated at: {FIGURE_PATH}")

if __name__ == "__main__":
    main()
