<script setup lang="ts">
import { computed } from "vue";
import MetricCard from "../components/MetricCard.vue";
import PageHero from "../components/PageHero.vue";
import SectionCard from "../components/SectionCard.vue";
import BaseChart from "../components/charts/BaseChart.vue";
import { usePageData } from "../composables/usePageData";
import AppLayout from "../layouts/AppLayout.vue";
import { formatPercent } from "../utils/format";
import type { BreakdownItem, DataOverview, ScoreCoverageItem } from "../types/data";

const menuItems = [
  { path: "/", label: "平台总览" },
  { path: "/data-overview", label: "基础数据看板" },
  { path: "/insight", label: "情感计算看板" },
  { path: "/decision", label: "决策分析中心" },
  { path: "/strategy", label: "策略建议看板" },
];

const { data, loading, error } = usePageData<DataOverview>("data-overview.json");

const timeline = computed(() => data.value?.reviewTimeline ?? []);

const firstMonth = computed(() => timeline.value[0]?.month ?? "--");

const latestMonth = computed(
  () => timeline.value.at(-1)?.month ?? "--",
);

const peakMonth = computed(() =>
  timeline.value.reduce(
    (current, item) => (item.count > current.count ? item : current),
    timeline.value[0] ?? { month: "--", count: 0 },
  ),
);

const sortByCount = <T extends BreakdownItem>(items: T[]) =>
  [...items].sort((left, right) => right.count - left.count);

const topModels = computed(() => sortByCount(data.value?.modelBreakdown ?? []));
const topCities = computed(() => sortByCount(data.value?.cityBreakdown ?? []));
const priceBands = computed(() => sortByCount(data.value?.priceBreakdown ?? []));
const coverageRows = computed(
  () => data.value?.scoreCoverage ?? [],
);

const weakestCoverage = computed(() =>
  coverageRows.value.reduce(
    (current: ScoreCoverageItem, item) =>
      item.share < current.share ? item : current,
    coverageRows.value[0] ?? {
      aspect: "--",
      aspectCn: "--",
      count: 0,
      share: 0,
    },
  ),
);

const coverageSummary = computed(() => {
  const total = coverageRows.value.length;
  const covered = coverageRows.value.filter((item) => item.count > 0).length;
  const averageShare = total
    ? coverageRows.value.reduce((sum, item) => sum + item.share, 0) / total
    : 0;

  return {
    covered,
    total,
    averageShare,
  };
});
</script>

<template>
  <AppLayout :menu-items="menuItems">
    <div class="page-stack">
      <PageHero
        section="数据基础"
        title="基础数据看板"
        description="围绕样本规模、采样跨度、车型与城市分布，以及评分字段覆盖，建立数据资产可信度底座。"
      />

      <section v-if="loading" class="section-card">
        <p class="page-description">正在加载基础数据...</p>
      </section>

      <section v-else-if="error" class="section-card">
        <p class="page-description">{{ error }}</p>
      </section>

      <template v-else-if="data">
        <section class="metric-grid">
          <MetricCard
            eyebrow="可信度底座"
            title="样本总量"
            :value="data.sampleCount"
            subtitle="真实评论样本的规模基础"
          />
          <MetricCard
            eyebrow="采样跨度"
            title="时间窗口"
            :value="`${firstMonth} 至 ${latestMonth}`"
            :subtitle="`峰值月：${peakMonth.month} / ${peakMonth.count}`"
          />
          <MetricCard
            eyebrow="字段完整性"
            title="评分字段覆盖"
            :value="`${coverageSummary.covered}/${coverageSummary.total}`"
            :subtitle="`平均覆盖率 ${formatPercent(coverageSummary.averageShare)}`"
          />
        </section>

        <section class="overview-grid">
          <SectionCard
            title="车型样本分布"
            subtitle="按评论样本量排序，查看头部车型版本的真实占比。"
          >
            <BaseChart :empty="topModels.length === 0" empty-text="暂无车型分布数据">
              <div class="rank-list">
                <article
                  v-for="item in topModels"
                  :key="item.label"
                  class="rank-row"
                >
                  <span>{{ item.label }}</span>
                  <strong>{{ item.count }}</strong>
                </article>
              </div>
            </BaseChart>
          </SectionCard>

          <SectionCard
            title="城市样本分布"
            subtitle="按评论样本量排序，确认数据是否集中在核心城市。"
          >
            <BaseChart :empty="topCities.length === 0" empty-text="暂无城市分布数据">
              <div class="rank-list">
                <article
                  v-for="item in topCities"
                  :key="item.label"
                  class="rank-row"
                >
                  <span>{{ item.label }}</span>
                  <strong>{{ item.count }}</strong>
                </article>
              </div>
            </BaseChart>
          </SectionCard>
        </section>

        <section class="overview-grid">
          <SectionCard
            title="价格带分布"
            subtitle="观察不同价格区间的样本积累，判断分析结论的覆盖范围。"
          >
            <BaseChart :empty="priceBands.length === 0" empty-text="暂无价格带数据">
              <div class="rank-list">
                <article
                  v-for="item in priceBands"
                  :key="item.label"
                  class="rank-row"
                >
                  <span>{{ item.label }}</span>
                  <strong>{{ item.count }}</strong>
                </article>
              </div>
            </BaseChart>
          </SectionCard>

          <SectionCard
            title="评分字段覆盖"
            subtitle="所有核心维度的覆盖程度，以及当前最弱维度的可信边界。"
          >
            <BaseChart
              :empty="coverageRows.length === 0"
              empty-text="暂无评分字段覆盖数据"
            >
              <div class="coverage-list">
                <article
                  v-for="item in coverageRows"
                  :key="item.aspect"
                  class="coverage-row"
                >
                  <div>
                    <p class="coverage-name">{{ item.aspectCn }}</p>
                    <p class="coverage-meta">
                      {{ item.count }} 条记录 · 覆盖率 {{ formatPercent(item.share) }}
                    </p>
                  </div>
                  <strong>{{ item.aspect }}</strong>
                </article>
              </div>
            </BaseChart>
          </SectionCard>
        </section>

        <SectionCard
          title="数据可信结论"
          subtitle="把样本规模、覆盖程度和时间跨度放在一起看，确认后续分析的地基是否稳定。"
        >
          <BaseChart :empty="false" height="auto">
            <div class="confidence-grid">
              <article class="confidence-card">
                <p>样本规模</p>
                <strong>{{ data.sampleCount.toLocaleString("zh-CN") }} 条</strong>
              </article>
              <article class="confidence-card">
                <p>时间跨度</p>
                <strong>{{ firstMonth }} - {{ latestMonth }}</strong>
              </article>
              <article class="confidence-card">
                <p>最弱维度</p>
                <strong>{{ weakestCoverage.aspectCn }}</strong>
                <span>{{ formatPercent(weakestCoverage.share) }}</span>
              </article>
            </div>
          </BaseChart>
        </SectionCard>
      </template>
    </div>
  </AppLayout>
</template>

<style scoped>
.overview-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

.rank-list,
.coverage-list,
.confidence-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.rank-row,
.coverage-row,
.confidence-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 16px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  border-radius: 14px;
  background: rgba(15, 23, 42, 0.35);
}

.coverage-name,
.confidence-card p {
  margin: 0;
  font-weight: 600;
}

.coverage-meta,
.confidence-card span {
  margin: 4px 0 0;
  color: var(--color-text-muted);
  font-size: 13px;
}

.confidence-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.confidence-card {
  flex-direction: column;
  align-items: flex-start;
}

@media (max-width: 1180px) {
  .overview-grid,
  .confidence-grid {
    grid-template-columns: 1fr;
  }
}
</style>
