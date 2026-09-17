<script setup lang="ts">
import { computed } from "vue";
import MetricCard from "../components/MetricCard.vue";
import PageHero from "../components/PageHero.vue";
import SectionCard from "../components/SectionCard.vue";
import BaseChart from "../components/charts/BaseChart.vue";
import InsightTag from "../components/InsightTag.vue";
import AppLayout from "../layouts/AppLayout.vue";
import { usePageData } from "../composables/usePageData";
import type {
  StrategyCityTierComparison,
  StrategyPriceRangeComparison,
  StrategyPowertrainComparison,
  StrategySandbox,
} from "../types/data";

const menuItems = [
  { path: "/", label: "平台总览" },
  { path: "/data-overview", label: "基础数据看板" },
  { path: "/insight", label: "情感计算看板" },
  { path: "/decision", label: "决策分析中心" },
  { path: "/strategy", label: "策略建议沙盘" },
];

const { data, loading, error } = usePageData<StrategySandbox>(
  "strategy-sandbox.json",
);

const priorityActions = computed(() =>
  [...(data.value?.priorityActions ?? [])].sort(
    (left, right) => left.priorityRank - right.priorityRank,
  ),
);

const totalKeywords = computed(() =>
  priorityActions.value.reduce(
    (total, item) => total + item.keywords.length,
    0,
  ),
);

const leadingAction = computed(() => priorityActions.value[0] ?? null);

const comparisonBlocks = computed(() => {
  const comparisons = data.value?.segmentComparisons;

  if (!comparisons) {
    return [];
  }

  return [
    {
      key: "powertrain",
      title: "动力类型对比",
      subtitle: "观察 DM-i、DM-p、EV 与 Other 的全维度表现差异",
      rows: comparisons.powertrain,
      columns: [
        { key: "space", label: "空间" },
        { key: "driving", label: "驾控" },
        { key: "range", label: "续航" },
        { key: "appearance", label: "外观" },
        { key: "interior", label: "内饰" },
        { key: "value", label: "性价比" },
        { key: "smart", label: "智能" },
      ],
    },
    {
      key: "cityTier",
      title: "城市级别对比",
      subtitle: "看不同城市层级在续航、性价比与智能体验上的差别",
      rows: comparisons.cityTier,
      columns: [
        { key: "range", label: "续航" },
        { key: "value", label: "性价比" },
        { key: "smart", label: "智能" },
      ],
    },
    {
      key: "priceRange",
      title: "价格区间对比",
      subtitle: "定位不同价位段的价值与内饰表现",
      rows: comparisons.priceRange,
      columns: [
        { key: "value", label: "性价比" },
        { key: "interior", label: "内饰" },
      ],
    },
  ];
});

function formatSampleSize(value: number | undefined) {
  return typeof value === "number" ? value.toLocaleString("zh-CN") : "--";
}

function getComparisonScore(
  row:
    | StrategyPowertrainComparison
    | StrategyCityTierComparison
    | StrategyPriceRangeComparison,
  key: string,
) {
  const value = row[key as keyof typeof row];
  return typeof value === "number" ? value.toFixed(4) : "--";
}
</script>

<template>
  <AppLayout :menu-items="menuItems">
    <div class="page-stack">
      <PageHero
        section="行动总览"
        title="策略建议沙盘"
        description="把决策结论整理为优先策略、适用场景与分群执行依据。"
      />

      <section v-if="loading" class="section-card">
        <p class="page-description">正在加载数据...</p>
      </section>

      <section v-else-if="error" class="section-card">
        <p class="page-description">{{ error }}</p>
      </section>

      <template v-else-if="data">
        <section class="metric-grid">
          <MetricCard
            title="优先策略"
            :value="priorityActions.length"
            trend="行动输出"
          />
          <MetricCard
            title="首要建议"
            :value="leadingAction ? leadingAction.aspectCn : '--'"
            :subtitle="
              leadingAction
                ? `Priority ${leadingAction.priorityRank} · ${leadingAction.aspect}`
                : '暂无建议'
            "
          />
          <MetricCard
            title="关键词总数"
            :value="totalKeywords"
            trend="证据标签"
            tone="accent"
          />
          <MetricCard
            title="对比维度"
            :value="3"
            subtitle="powertrain / cityTier / priceRange"
          />
        </section>

        <SectionCard
          title="优先策略"
          subtitle="按 priorityRank 展示最值得执行的动作"
        >
          <BaseChart
            :empty="priorityActions.length === 0"
            empty-text="暂无优先建议数据"
          >
            <div class="strategy-list">
              <article
                v-for="item in priorityActions"
                :key="item.aspect"
                class="strategy-card"
              >
                <div class="strategy-card__header">
                  <div>
                    <h3 class="strategy-card__title">{{ item.aspectCn }}</h3>
                    <p class="strategy-card__subtitle">{{ item.aspect }}</p>
                  </div>
                  <InsightTag
                    :label="`Priority ${item.priorityRank}`"
                    tone="accent"
                  />
                </div>

                <p class="strategy-card__action">{{ item.action }}</p>

                <div class="strategy-card__keywords">
                  <InsightTag
                    v-for="keyword in item.keywords"
                    :key="keyword"
                    :label="keyword"
                  />
                </div>
              </article>
            </div>
          </BaseChart>
        </SectionCard>

        <section class="comparison-grid">
          <SectionCard
            v-for="(block, index) in comparisonBlocks"
            :key="block.key"
            :title="index === 0 ? '细分对比' : block.title"
            :subtitle="index === 0 ? '动力、城市层级与价格带结构差异' : block.subtitle"
          >
            <BaseChart
              :empty="block.rows.length === 0"
              empty-text="暂无对比数据"
            >
              <div class="comparison-list">
                <article
                  v-for="row in block.rows"
                  :key="row.segment"
                  class="comparison-card"
                >
                  <div class="comparison-card__header">
                    <div>
                      <h3 class="comparison-card__title">{{ row.segment }}</h3>
                      <p class="comparison-card__subtitle">
                        样本 {{ formatSampleSize(row.sampleSize) }}
                      </p>
                    </div>
                  </div>

                  <div class="comparison-card__metrics">
                    <div
                      v-for="column in block.columns"
                      :key="column.key"
                      class="comparison-metric"
                    >
                      <span>{{ column.label }}</span>
                      <strong>{{ getComparisonScore(row, column.key) }}</strong>
                    </div>
                  </div>
                </article>
              </div>
            </BaseChart>
          </SectionCard>
        </section>
      </template>
    </div>
  </AppLayout>
</template>

<style scoped>
.strategy-list,
.comparison-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.strategy-card,
.comparison-card {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 16px;
  border: 1px solid var(--color-border);
  border-radius: 14px;
  background: var(--color-bg-elevated);
}

.strategy-card__header,
.comparison-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.strategy-card__title,
.comparison-card__title {
  margin: 0;
  font-size: 18px;
  color: var(--color-text-heading);
}

.strategy-card__subtitle,
.comparison-card__subtitle,
.strategy-card__action {
  margin: 0;
  color: var(--color-text-muted);
}

.strategy-card__subtitle,
.comparison-card__subtitle,
.strategy-card__action {
  font-size: 13px;
}

.strategy-card__action {
  line-height: 1.7;
}

.strategy-card__keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.comparison-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
}

.comparison-card__metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(84px, 1fr));
  gap: 10px;
}

.comparison-metric {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 10px 12px;
  border-radius: 12px;
  background: var(--color-bg);
}

.comparison-metric span {
  color: var(--color-text-muted);
  font-size: 12px;
}

.comparison-metric strong {
  font-size: 15px;
  color: var(--color-text-heading);
}

@media (max-width: 1180px) {
  .comparison-grid {
    grid-template-columns: 1fr;
  }
}
</style>
