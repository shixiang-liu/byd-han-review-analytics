<script setup lang="ts">
import { computed } from "vue";
import MetricCard from "../components/MetricCard.vue";
import PageHero from "../components/PageHero.vue";
import SectionCard from "../components/SectionCard.vue";
import BaseChart from "../components/charts/BaseChart.vue";
import InsightTag from "../components/InsightTag.vue";
import { usePageData } from "../composables/usePageData";
import AppLayout from "../layouts/AppLayout.vue";
import type { DecisionAnalysis } from "../types/data";

const menuItems = [
  { path: "/", label: "平台总览" },
  { path: "/data-overview", label: "基础数据看板" },
  { path: "/insight", label: "情感计算看板" },
  { path: "/decision", label: "决策分析中心" },
  { path: "/strategy", label: "策略建议沙盘" },
];

const { data, loading, error } = usePageData<DecisionAnalysis>(
  "decision-analysis.json",
);

// 维度中文名映射
const aspectCnMap: Record<string, string> = {
  space: '空间',
  driving: '驾驶感受',
  range: '续航',
  appearance: '外观',
  interior: '内饰',
  value: '性价比',
  smart: '智能化',
};

const ipaFocusItems = computed(
  () => data.value?.ipaMatrix.filter((item) => item.quadrant === "Q2") ?? [],
);
const causalEffects = computed(() => data.value?.causalEffects ?? []);
const penaltyRewardItems = computed(() => data.value?.penaltyReward ?? []);
const innovationPriorityItems = computed(
  () => data.value?.innovationPriority ?? [],
);

const topIpaItem = computed(() => {
  const items = data.value?.ipaMatrix ?? [];
  return items.find((item) => item.quadrant === "Q2") ?? items[0] ?? null;
});

const strongestEffect = computed(() => {
  const effects = data.value?.causalEffects ?? [];
  return (
    [...effects].sort((left, right) => right.theta - left.theta)[0] ?? null
  );
});
</script>

<template>
  <AppLayout :menu-items="menuItems">
    <div class="page-stack">
      <PageHero
        section="核心结论"
        title="决策分析中心"
        description="用 IPA、因果效应与奖惩证据回答为什么优先改这些问题。"
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
            title="首要改进对象"
            :value="topIpaItem ? topIpaItem.aspectCn : '--'"
            trend="IPA 重点改进"
            tone="warning"
            :subtitle="topIpaItem ? topIpaItem.quadrantName : '暂无 IPA 结果'"
          />
          <MetricCard
            title="最强因果抓手"
            :value="strongestEffect ? strongestEffect.theta.toFixed(3) : '--'"
            trend="因果效应强度"
            tone="accent"
            :subtitle="
              strongestEffect
                ? `${strongestEffect.aspectCn} · ${strongestEffect.ciLower.toFixed(3)} ~ ${strongestEffect.ciUpper.toFixed(3)}`
                : '暂无 DML 结果'
            "
          />
        </section>

        <section class="analysis-grid">
          <SectionCard
            title="IPA 重点改进"
            subtitle="优先跟进的 Q2 维度"
          >
            <BaseChart :empty="ipaFocusItems.length === 0">
              <div class="analysis-list">
                <article
                  v-for="item in ipaFocusItems"
                  :key="item.aspect"
                  class="analysis-row"
                >
                  <div class="analysis-row__main">
                    <div class="analysis-row__title">
                      <strong>{{ item.aspectCn }}</strong>
                      <span>{{ item.aspect }}</span>
                    </div>
                    <p class="analysis-row__text">{{ item.action }}</p>
                  </div>
                  <div class="analysis-row__meta">
                    <InsightTag :label="item.quadrantName" tone="warning" />
                    <InsightTag
                      :label="`Priority ${item.priorityRank}`"
                      tone="accent"
                    />
                  </div>
                </article>
              </div>
            </BaseChart>
          </SectionCard>

          <SectionCard
            title="因果效应强度"
            subtitle="theta 与置信区间"
          >
            <BaseChart :empty="causalEffects.length === 0">
              <div class="analysis-list">
                <article
                  v-for="effect in causalEffects"
                  :key="effect.aspect"
                  class="effect-row"
                >
                  <div class="analysis-row__main">
                    <div class="analysis-row__title">
                      <strong>{{ effect.aspectCn }}</strong>
                      <span>{{ effect.aspect }}</span>
                    </div>
                    <p class="analysis-row__text">{{ effect.nUsed }} 条样本</p>
                  </div>
                  <div class="effect-row__values">
                    <strong>{{ effect.theta.toFixed(3) }}</strong>
                    <span
                      >{{ effect.ciLower.toFixed(3) }} ~
                      {{ effect.ciUpper.toFixed(3) }}</span
                    >
                  </div>
                </article>
              </div>
            </BaseChart>
          </SectionCard>
        </section>

        <SectionCard
          title="证据链"
          subtitle="Penalty-Reward 与 Innovation Priority 汇总"
        >
          <BaseChart
            :empty="
              penaltyRewardItems.length === 0 &&
              innovationPriorityItems.length === 0
            "
          >
            <div class="evidence-stack">
              <div class="evidence-block">
                <h3 class="mini-title">Penalty-Reward</h3>
                <article
                  v-for="item in penaltyRewardItems.slice(0, 4)"
                  :key="item.aspect"
                  class="evidence-row"
                >
                  <div>
                    <strong>{{ aspectCnMap[item.aspect] || item.aspect }}</strong>
                    <p>{{ item.classification }}</p>
                  </div>
                  <div class="evidence-row__values">
                    <span>penalty {{ item.penaltyWeight.toFixed(3) }}</span>
                    <span>reward {{ item.rewardWeight.toFixed(3) }}</span>
                  </div>
                </article>
              </div>

              <div class="evidence-block">
                <h3 class="mini-title">Innovation Priority</h3>
                <article
                  v-for="item in innovationPriorityItems.slice(0, 4)"
                  :key="item.aspect"
                  class="evidence-row"
                >
                  <div>
                    <strong>{{ aspectCnMap[item.aspect] || item.aspect }}</strong>
                    <p>importance {{ item.importance.toFixed(3) }}</p>
                  </div>
                  <div class="evidence-row__values">
                    <span>innovation {{ item.innovationZ.toFixed(3) }}</span>
                    <span>expect {{ item.expectRate.toFixed(3) }}</span>
                  </div>
                </article>
              </div>
            </div>
          </BaseChart>
        </SectionCard>
      </template>
    </div>
  </AppLayout>
</template>

<style scoped>
.analysis-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

.analysis-list,
.evidence-stack {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.analysis-row,
.effect-row,
.evidence-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 16px;
  border: 1px solid var(--color-border);
  border-radius: 14px;
  background: var(--color-bg-elevated);
}

.analysis-row__main {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.analysis-row__title {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.analysis-row__title span,
.analysis-row__text,
.evidence-row p,
.evidence-row__values span {
  color: var(--color-text-muted);
}

.analysis-row__text,
.evidence-row p {
  margin: 0;
  font-size: 13px;
}

.analysis-row__meta,
.evidence-row__values {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.effect-row__values {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.effect-row__values strong {
  font-size: 20px;
  color: var(--color-text-heading);
}

.evidence-stack {
  gap: 16px;
}

.evidence-block {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mini-title {
  margin: 0;
  font-size: 16px;
  color: var(--color-text-heading);
}
</style>
