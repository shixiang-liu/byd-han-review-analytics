<script setup lang="ts">
import { computed } from "vue";
import MetricCard from "../components/MetricCard.vue";
import InsightTag from "../components/InsightTag.vue";
import PageHero from "../components/PageHero.vue";
import SectionCard from "../components/SectionCard.vue";
import BaseChart from "../components/charts/BaseChart.vue";
import { usePageData } from "../composables/usePageData";
import AppLayout from "../layouts/AppLayout.vue";
import { formatPercent } from "../utils/format";
import type { MonthlyTrendPoint, SentimentInsight } from "../types/data";

const menuItems = [
  { path: "/", label: "平台总览" },
  { path: "/data-overview", label: "基础数据看板" },
  { path: "/insight", label: "情感计算看板" },
  { path: "/decision", label: "决策分析中心" },
  { path: "/strategy", label: "策略建议看板" },
];

const { data, loading, error } = usePageData<SentimentInsight>(
  "sentiment-insight.json",
);

const overallMetrics = computed(() =>
  data.value
    ? [
        {
          eyebrow: "总体情绪",
          title: "正向均值",
          value: formatPercent(data.value.overallSentiment.positiveMean),
          subtitle: "整体口碑中的正向表达强度",
          tone: "positive" as const,
        },
        {
          eyebrow: "总体情绪",
          title: "负向均值",
          value: formatPercent(data.value.overallSentiment.negativeMean),
          subtitle: "负面表达与问题密度",
          tone: "warning" as const,
        },
        {
          eyebrow: "分析维度",
          title: "覆盖维数",
          value: String(data.value.aspectSentiment.length),
          subtitle: "当前情感计算纳入的核心维度数",
          tone: "accent" as const,
        },
      ]
    : [],
);

const aspectRows = computed(() =>
  [...(data.value?.aspectSentiment ?? [])].sort(
    (left, right) => right.performance - left.performance,
  ),
);

const negativeThemes = computed(() =>
  [...(data.value?.negativeKeywords ?? [])].sort((left, right) => {
    const leftWeight = left.keywords[0]?.weight ?? 0;
    const rightWeight = right.keywords[0]?.weight ?? 0;
    return rightWeight - leftWeight;
  }),
);

const latestTrend = computed(() => data.value?.monthlyTrend.at(-1) ?? null);

const trendValues = computed(() => {
  const row = latestTrend.value;

  if (!row) {
    return [];
  }

  return Object.entries(row)
    .filter(([key, value]) => key !== "month" && typeof value === "number")
    .map(([aspect, value]) => ({
      aspect,
      value: value as number,
    }))
    .sort((left, right) => right.value - left.value);
});

const latestTrendInsight = computed(() => {
  const strongest = trendValues.value[0] ?? null;
  const weakest = trendValues.value[trendValues.value.length - 1] ?? null;

  return {
    month: latestTrend.value?.month ?? "--",
    strongest,
    weakest,
  };
});

const aspectLabels: Record<Exclude<keyof MonthlyTrendPoint, "month">, string> = {
  space: "空间",
  driving: "驾驶感受",
  range: "续航",
  appearance: "外观",
  interior: "内饰",
  value: "性价比",
  smart: "智能化",
};

const themeLabels: Record<string, string> = {
  space: "空间",
  driving: "驾驶感受",
  range: "续航",
  appearance: "外观",
  interior: "内饰",
  value: "性价比",
  smart: "智能化",
};

const getAspectLabel = (aspect: string) =>
  aspectLabels[aspect as keyof typeof aspectLabels] ?? aspect;

const getThemeLabel = (aspect: string) => themeLabels[aspect] ?? aspect;
</script>

<template>
  <AppLayout :menu-items="menuItems">
    <div class="page-stack">
      <PageHero
        section="情感智能"
        title="情感计算看板"
        description="围绕整体情绪、维度表现、负向主题与月度走势，提炼可直接行动的情感信号。"
      />

      <section v-if="loading" class="section-card">
        <p class="page-description">正在加载情感计算数据...</p>
      </section>

      <section v-else-if="error" class="section-card">
        <p class="page-description">{{ error }}</p>
      </section>

      <template v-else-if="data">
        <section class="metric-grid">
          <MetricCard
            v-for="metric in overallMetrics"
            :key="metric.title"
            :eyebrow="metric.eyebrow"
            :title="metric.title"
            :value="metric.value"
            :subtitle="metric.subtitle"
            :tone="metric.tone"
          />
        </section>

        <section class="insight-grid">
          <SectionCard
            title="维度情感表现"
            subtitle="按照维度表现排序，快速定位情感强弱和样本支撑量。"
          >
            <BaseChart :empty="aspectRows.length === 0" empty-text="暂无维度情感数据">
              <div class="insight-list">
                <article
                  v-for="item in aspectRows"
                  :key="item.aspect"
                  class="insight-row"
                >
                  <div class="insight-row__main">
                    <div class="insight-row__title">
                      <strong>{{ item.aspectCn }}</strong>
                      <span>{{ item.aspect }}</span>
                    </div>
                    <p class="insight-row__meta">
                      {{ item.nSentiment }} 条情感样本 · 均分 {{ item.scoreMean.toFixed(2) }}
                    </p>
                  </div>
                  <div class="insight-row__values">
                    <InsightTag
                      :label="`表现 ${Math.round(item.performance * 100)}%`"
                      tone="accent"
                    />
                    <InsightTag
                      :label="`情绪 ${Math.round(item.sentimentMean * 100)}%`"
                      tone="success"
                    />
                  </div>
                </article>
              </div>
            </BaseChart>
          </SectionCard>

          <SectionCard
            title="负向主题聚类"
            subtitle="按主题权重排序，查看每个维度的负向表达集中在哪些词上。"
          >
            <BaseChart
              :empty="negativeThemes.length === 0"
              empty-text="暂无负向主题数据"
            >
              <div class="theme-list">
                <article
                  v-for="theme in negativeThemes"
                  :key="theme.aspect"
                  class="theme-card"
                >
                  <div class="theme-card__header">
                    <div>
                      <strong>{{ theme.aspectCn }}</strong>
                      <p>{{ theme.aspect }}</p>
                    </div>
                    <InsightTag
                      :label="`${theme.keywords.length} 个高频词`"
                      tone="warning"
                    />
                  </div>
                  <div class="theme-keywords">
                    <InsightTag
                      v-for="keyword in theme.keywords.slice(0, 3)"
                      :key="keyword.keyword"
                      :label="`${keyword.rank}. ${keyword.keyword}`"
                    />
                  </div>
                </article>
              </div>
            </BaseChart>
          </SectionCard>
        </section>

        <SectionCard
          title="月度趋势洞察"
          subtitle="以最新月份为焦点，识别当前情感最强和最弱的维度。"
        >
          <BaseChart :empty="!latestTrend" empty-text="暂无月度趋势数据">
            <div v-if="latestTrend" class="trend-summary">
              <article class="trend-summary__card">
                <p class="trend-summary__label">最新月份</p>
                <strong>{{ latestTrendInsight.month }}</strong>
              </article>
              <article class="trend-summary__card">
                <p class="trend-summary__label">最强维度</p>
                <strong>
                  {{
                    latestTrendInsight.strongest
                      ? `${getAspectLabel(latestTrendInsight.strongest.aspect)} ${latestTrendInsight.strongest.value.toFixed(2)}`
                      : "--"
                  }}
                </strong>
              </article>
              <article class="trend-summary__card">
                <p class="trend-summary__label">最弱维度</p>
                <strong>
                  {{
                    latestTrendInsight.weakest
                      ? `${getAspectLabel(latestTrendInsight.weakest.aspect)} ${latestTrendInsight.weakest.value.toFixed(2)}`
                      : "--"
                  }}
                </strong>
              </article>
            </div>

            <div v-if="latestTrend" class="trend-detail">
              <article
                v-for="item in trendValues"
                :key="item.aspect"
                class="trend-detail__row"
              >
                <span>{{ getThemeLabel(item.aspect) }}</span>
                <strong>{{ item.value.toFixed(2) }}</strong>
              </article>
            </div>
          </BaseChart>
        </SectionCard>
      </template>
    </div>
  </AppLayout>
</template>

<style scoped>
.insight-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

.insight-list,
.theme-list,
.trend-summary,
.trend-detail {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.insight-row,
.theme-card,
.trend-summary__card,
.trend-detail__row {
  padding: 14px 16px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  border-radius: 14px;
  background: rgba(15, 23, 42, 0.35);
}

.insight-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.insight-row__main {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.insight-row__title {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.insight-row__title span,
.insight-row__meta,
.theme-card p,
.trend-summary__label {
  color: var(--color-text-muted);
}

.insight-row__meta,
.theme-card p {
  margin: 0;
  font-size: 13px;
}

.insight-row__values,
.theme-keywords {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.theme-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.theme-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.trend-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.trend-summary__card,
.trend-detail__row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.trend-summary__card {
  flex-direction: column;
}

.trend-summary__card strong {
  font-size: 18px;
}

.trend-detail__row span {
  color: var(--color-text-muted);
}

@media (max-width: 1180px) {
  .insight-grid,
  .trend-summary {
    grid-template-columns: 1fr;
  }
}
</style>
