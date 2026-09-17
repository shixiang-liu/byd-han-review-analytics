<script setup lang="ts">
import { computed, ref } from "vue";
import IpaScatterChart from "../components/charts/IpaScatterChart.vue";
import RadarChart from "../components/charts/RadarChart.vue";
import TrendLineChart from "../components/charts/TrendLineChart.vue";
import KeywordBarChart from "../components/charts/KeywordBarChart.vue";
import CausalEffectChart from "../components/charts/CausalEffectChart.vue";
import KpiDetailDrawer from "../components/dialogs/KpiDetailDrawer.vue";
import AspectDetailDrawer from "../components/dialogs/AspectDetailDrawer.vue";
import StatCard from "../components/StatCard.vue";
import ChartCard from "../components/ChartCard.vue";
import { usePageData } from "../composables/usePageData";
import AppLayout from "../layouts/AppLayout.vue";
import type {
  DashboardMetrics,
  IpaQuadrantData,
  KeywordAnalysisData,
  PerformanceScoresData,
  SentimentTrendData,
  CausalEffectData,
  DecisionRecommendations,
  DataOverview,
  PrcaRecommendations,
} from "../types/data";

const menuItems = [{ path: "/", label: "决策支持平台" }];

// 加载所有真实数据
const metricsState = usePageData<DashboardMetrics>("dashboard-metrics.json");
const ipaState = usePageData<IpaQuadrantData>("ipa-quadrant.json");
const keywordsState = usePageData<KeywordAnalysisData>("keywords-analysis.json");
const performanceState = usePageData<PerformanceScoresData>("performance-scores.json");
const trendState = usePageData<SentimentTrendData>("sentiment-trend.json");
const causalState = usePageData<CausalEffectData>("causal-effects.json");
const recommendationsState = usePageData<DecisionRecommendations>("decision-recommendations.json");
const dataOverviewState = usePageData<DataOverview>("data-overview.json");
const prcaState = usePageData<PrcaRecommendations>("prca-recommendations.json");

const metrics = computed(() => metricsState.data.value);
const ipaData = computed(() => ipaState.data.value);
const keywordsData = computed(() => keywordsState.data.value);
const performanceData = computed(() => performanceState.data.value);
const trendData = computed(() => trendState.data.value);
const causalData = computed(() => causalState.data.value);
const recommendations = computed(() => recommendationsState.data.value);
const dataOverview = computed(() => dataOverviewState.data.value);
const prcaData = computed(() => prcaState.data.value);

const isLoading = computed(() => metricsState.loading.value);

// 弹窗状态
const kpiDrawerVisible = ref(false);
const activeKpiType = ref<string | null>(null);
const aspectDrawerVisible = ref(false);
const activeAspect = ref<string | null>(null);

const handleKpiClick = (type: string) => {
  activeKpiType.value = type;
  kpiDrawerVisible.value = true;
};

const handleAspectClick = (aspect: string) => {
  activeAspect.value = aspect;
  aspectDrawerVisible.value = true;
};

const closeKpiDrawer = () => {
  kpiDrawerVisible.value = false;
  activeKpiType.value = null;
};

const closeAspectDrawer = () => {
  aspectDrawerVisible.value = false;
  activeAspect.value = null;
};

// PRCA颜色
const getPrcaColor = (c: string) => {
  if (c.includes("Hygiene")) return "#64748b";
  if (c.includes("期望")) return "#2563eb";
  if (c.includes("兴奋")) return "#10b981";
  return "#64748b";
};

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

// 问题维度（Q2）- 按优先级排序
const problemAspects = computed(() =>
  ipaData.value?.items.filter(i => i.quadrant === "Q2").sort((a, b) => a.priorityRank - b.priorityRank) || []
);

// 优势维度（Q1）
const strengthAspects = computed(() => ipaData.value?.items.filter(i => i.quadrant === "Q1") || []);

// 峰值月份
const peakMonth = computed(() => {
  if (!dataOverview.value) return null;
  return dataOverview.value.reviewTimeline.reduce((max, i) => i.count > max.count ? i : max, dataOverview.value.reviewTimeline[0]);
});

// TOP车型/城市
const topModels = computed(() => dataOverview.value ? [...dataOverview.value.modelBreakdown].sort((a, b) => b.count - a.count).slice(0, 3) : []);
const topCities = computed(() => dataOverview.value ? [...dataOverview.value.cityBreakdown].sort((a, b) => b.count - a.count).slice(0, 5) : []);
</script>

<template>
  <AppLayout :menu-items="menuItems">
    <div class="dashboard-container">
      <!-- Loading State -->
      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <p class="loading-text">正在加载分析数据...</p>
      </div>

      <template v-else-if="metrics && ipaData">
        <!-- Page Header -->
        <header class="page-header">
          <div class="page-header__content">
            <h1 class="page-title">比亚迪汉口碑分析决策支持系统</h1>
            <p class="page-subtitle">
              基于 <strong>汽车之家</strong> {{ metrics.sampleCount?.toLocaleString() || '0' }} 条真实用户口碑数据
              <span class="time-range">{{ metrics.analysisWindow?.start || '未知' }} ~ {{ metrics.analysisWindow?.end || '未知' }}</span>
            </p>
          </div>
        </header>

        <!-- KPI Summary Cards -->
        <section class="kpi-section">
          <StatCard
            title="样本规模"
            :value="metrics.sampleCount"
            description="真实用户评价数据"
            variant="accent"
            clickable
            icon="📊"
            @click="handleKpiClick('sampleCount')"
          />
          <StatCard
            title="分析维度"
            :value="metrics.analysisDimensions"
            description="核心评价指标体系"
            variant="default"
            clickable
            icon="🔍"
            @click="handleKpiClick('analysisDimensions')"
          />
          <StatCard
            title="重点问题"
            :value="metrics.priorityIssues"
            description="Q2象限需改进项"
            variant="danger"
            clickable
            icon="⚠️"
            @click="handleKpiClick('priorityIssues')"
          />
          <StatCard
            title="优势维度"
            :value="metrics.actionCount"
            description="Q1象限可保持项"
            variant="success"
            clickable
            icon="✅"
            @click="handleKpiClick('actionCount')"
          />
        </section>

        <!-- Core Analysis Section: IPA + Radar -->
        <section class="core-analysis">
          <ChartCard
            title="IPA 重要性-表现分析"
            description="识别改进优先级的四象限分布"
            class="ipa-card"
          >
            <IpaScatterChart :data="ipaData" height="340px" @point-click="handleAspectClick" />
            <template #footer>
              <div class="quadrant-legend">
                <span class="legend-item legend-item--success">● Q1 优势保持区</span>
                <span class="legend-item legend-item--danger">● Q2 重点改进区</span>
                <span class="legend-item legend-item--neutral">● Q3 低优先区</span>
                <span class="legend-item legend-item--warning">● Q4 过度投入区</span>
              </div>
            </template>
          </ChartCard>
          <ChartCard
            title="七维度绩效雷达图"
            description="各维度表现度综合评分"
          >
            <RadarChart :data="performanceData" height="340px" />
          </ChartCard>
        </section>

        <!-- Priority Recommendations -->
        <section class="recommendations-section">
          <div class="section-header">
            <h2 class="section-title">改进建议排序</h2>
            <p class="section-desc">基于IPA分析的战略行动建议</p>
          </div>
          <div class="recommendations-grid">
            <!-- Q2 重点改进区 -->
            <div class="recommendation-group recommendation-group--danger">
              <div class="group-header">
                <span class="group-badge group-badge--danger">重点改进区 (Q2)</span>
                <span class="group-count">{{ problemAspects.length }}项</span>
              </div>
              <div class="recommendation-list">
                <div
                  v-for="item in problemAspects"
                  :key="item.aspect"
                  class="recommendation-card recommendation-card--danger"
                  @click="handleAspectClick(item.aspect)"
                >
                  <div class="card-header">
                    <span class="priority-rank">#{{ item.priorityRank }}</span>
                    <span class="aspect-name">{{ item.aspectCn }}</span>
                  </div>
                  <div class="metrics-bars">
                    <div class="bar-item">
                      <span class="bar-label">表现度</span>
                      <div class="bar-track">
                        <div class="bar-fill bar-fill--danger" :style="{ width: (item.performance * 100) + '%' }"></div>
                      </div>
                      <span class="bar-value">{{ (item.performance * 100).toFixed(1) }}%</span>
                    </div>
                    <div class="bar-item">
                      <span class="bar-label">重要性</span>
                      <div class="bar-track">
                        <div class="bar-fill bar-fill--accent" :style="{ width: (item.importance * 100) + '%' }"></div>
                      </div>
                      <span class="bar-value">{{ (item.importance * 100).toFixed(1) }}%</span>
                    </div>
                  </div>
                  <p class="action-text">{{ item.action }}</p>
                </div>
              </div>
            </div>
            <!-- Q1 优势保持区 -->
            <div class="recommendation-group recommendation-group--success">
              <div class="group-header">
                <span class="group-badge group-badge--success">优势保持区 (Q1)</span>
                <span class="group-count">{{ strengthAspects.length }}项</span>
              </div>
              <div class="recommendation-list">
                <div
                  v-for="item in strengthAspects"
                  :key="item.aspect"
                  class="recommendation-card recommendation-card--success"
                  @click="handleAspectClick(item.aspect)"
                >
                  <div class="card-header">
                    <span class="aspect-name">{{ item.aspectCn }}</span>
                    <span class="status-badge status-badge--success">优势</span>
                  </div>
                  <div class="metrics-bars">
                    <div class="bar-item">
                      <span class="bar-label">表现度</span>
                      <div class="bar-track">
                        <div class="bar-fill bar-fill--success" :style="{ width: (item.performance * 100) + '%' }"></div>
                      </div>
                      <span class="bar-value">{{ (item.performance * 100).toFixed(1) }}%</span>
                    </div>
                    <div class="bar-item">
                      <span class="bar-label">重要性</span>
                      <div class="bar-track">
                        <div class="bar-fill bar-fill--accent" :style="{ width: (item.importance * 100) + '%' }"></div>
                      </div>
                      <span class="bar-value">{{ (item.importance * 100).toFixed(1) }}%</span>
                    </div>
                  </div>
                  <p class="action-text">{{ item.action }}</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Keywords + Causal Effect -->
        <section class="analysis-row">
          <ChartCard
            title="问题关键词 TOP10"
            description="对比性TF-IDF提取高频问题词"
            height="280px"
            noPadding
          >
            <KeywordBarChart :data="keywordsData" :top-n="10" height="280px" />
          </ChartCard>
          <ChartCard
            title="因果效应分析 (DML)"
            description="双重机器学习估计真实因果效应"
            height="280px"
            noPadding
          >
            <CausalEffectChart :data="causalData" height="280px" />
          </ChartCard>
        </section>

        <!-- Trend + PRCA -->
        <section class="analysis-row">
          <ChartCard
            title="口碑情感趋势 (2020-2026)"
            description="月度情感评分变化追踪"
            height="260px"
            class="trend-card"
          >
            <TrendLineChart :data="trendData" height="260px" />
          </ChartCard>
          <ChartCard
            title="PRCA 分类分析"
            description="Penalty-Reward对比分析，Kano三分类"
            height="260px"
          >
            <div class="prca-list">
              <div v-for="item in prcaData?.recommendations" :key="item.aspect" class="prca-item">
                <div class="prca-header">
                  <span class="prca-name">{{ aspectCnMap[item.aspect] || item.aspect }}</span>
                  <span class="prca-badge" :style="{ backgroundColor: getPrcaColor(item.classification) + '20', color: getPrcaColor(item.classification), borderColor: getPrcaColor(item.classification) }">
                    {{ item.classification }}
                  </span>
                </div>
                <div class="prca-metrics">
                  <span>惩罚 {{ (item.penaltyWeight * 100).toFixed(1) }}%</span>
                  <span class="metric-divider">|</span>
                  <span>奖励 {{ (item.rewardWeight * 100).toFixed(1) }}%</span>
                </div>
                <div class="prca-performance">评分 {{ item.performance.toFixed(2) }}</div>
              </div>
            </div>
          </ChartCard>
        </section>

        <!-- Data Distribution -->
        <section class="data-distribution" v-if="dataOverview">
          <div class="section-header">
            <h2 class="section-title">样本数据分布</h2>
            <p class="section-desc">数据来源与覆盖范围概览</p>
          </div>
          <div class="distribution-grid">
            <div class="distribution-card">
              <h3 class="card-title">时间分布</h3>
              <div class="peak-highlight">
                <span class="peak-label">峰值月份</span>
                <span class="peak-value">{{ peakMonth?.month }}</span>
                <span class="peak-count">{{ peakMonth?.count }}条</span>
              </div>
              <p class="coverage-note">覆盖 {{ dataOverview.reviewTimeline.length }} 个月份</p>
            </div>
            <div class="distribution-card">
              <h3 class="card-title">车型分布 TOP3</h3>
              <div class="ranking-list">
                <div v-for="m in topModels" :key="m.label" class="ranking-item">
                  <span class="rank-name">{{ m.label }}</span>
                  <span class="rank-count">{{ m.count }}</span>
                  <div class="rank-bar">
                    <div class="rank-fill" :style="{ width: (m.count / dataOverview.sampleCount * 100) + '%' }"></div>
                  </div>
                </div>
              </div>
            </div>
            <div class="distribution-card">
              <h3 class="card-title">地域分布 TOP5</h3>
              <div class="ranking-list">
                <div v-for="c in topCities" :key="c.label" class="ranking-item">
                  <span class="rank-name">{{ c.label }}</span>
                  <span class="rank-count">{{ c.count }}</span>
                  <div class="rank-bar">
                    <div class="rank-fill" :style="{ width: (c.count / dataOverview.sampleCount * 100) + '%' }"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Methods Reference -->
        <section class="methods-reference">
          <div class="methods-grid">
            <div class="method-card">
              <span class="method-icon">📊</span>
              <h4 class="method-title">IPA分析</h4>
              <p class="method-desc">重要性-表现分析，识别改进优先级</p>
            </div>
            <div class="method-card">
              <span class="method-icon">🔬</span>
              <h4 class="method-title">因果推断</h4>
              <p class="method-desc">DML双重机器学习估计真实因果效应</p>
            </div>
            <div class="method-card">
              <span class="method-icon">📝</span>
              <h4 class="method-title">TF-IDF</h4>
              <p class="method-desc">对比性TF-IDF提取问题关键词</p>
            </div>
            <div class="method-card">
              <span class="method-icon">🎯</span>
              <h4 class="method-title">PRCA</h4>
              <p class="method-desc">Penalty-Reward分析，Kano三分类</p>
            </div>
          </div>
        </section>
      </template>

      <!-- Drawers -->
      <KpiDetailDrawer
        :visible="kpiDrawerVisible"
        :kpi-type="activeKpiType || ''"
        :metrics-data="metrics"
        :ipa-data="ipaData"
        :performance-data="performanceData"
        @update:visible="kpiDrawerVisible = $event"
        @close="closeKpiDrawer"
      />
      <AspectDetailDrawer
        :visible="aspectDrawerVisible"
        :aspect="activeAspect || ''"
        :ipa-data="ipaData"
        :keywords-data="keywordsData"
        :performance-data="performanceData"
        :recommendations="recommendations?.recommendations ?? null"
        @update:visible="aspectDrawerVisible = $event"
        @close="closeAspectDrawer"
      />
    </div>
  </AppLayout>
</template>

<style scoped>
/* === Container === */
.dashboard-container {
  padding: 24px 32px;
  max-width: 1440px;
  margin: 0 auto;
  min-height: calc(100vh - 120px);
}

/* === Loading State === */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  gap: 16px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e7eb;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 15px;
  color: #6b7280;
}

/* === Page Header === */
.page-header {
  margin-bottom: 32px;
}

.page-header__content {
  text-align: center;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #111827;
  margin: 0 0 8px;
}

.page-subtitle {
  font-size: 15px;
  color: #6b7280;
  margin: 0;
}

.page-subtitle strong {
  color: #2563eb;
  font-weight: 600;
}

.time-range {
  margin-left: 8px;
  padding: 4px 12px;
  background: #f3f4f6;
  border-radius: 6px;
  font-size: 13px;
  color: #374151;
}

/* === KPI Section === */
.kpi-section {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

/* === Core Analysis === */
.core-analysis {
  display: grid;
  grid-template-columns: 1.3fr 1fr;
  gap: 24px;
  margin-bottom: 32px;
}

.ipa-card {
  /* IPA gets more space */
}

/* === Recommendations Section === */
.recommendations-section {
  margin-bottom: 32px;
}

.section-header {
  margin-bottom: 20px;
}

.section-title {
  font-size: 18px;
  font-weight: 700;
  color: #111827;
  margin: 0 0 4px;
}

.section-desc {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.recommendations-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.recommendation-group {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
}

.recommendation-group--danger {
  border-top: 3px solid #ef4444;
}

.recommendation-group--success {
  border-top: 3px solid #10b981;
}

.group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.group-badge {
  font-size: 14px;
  font-weight: 600;
  padding: 6px 14px;
  border-radius: 6px;
}

.group-badge--danger {
  background: #fef2f2;
  color: #dc2626;
}

.group-badge--success {
  background: #f0fdf4;
  color: #16a34a;
}

.group-count {
  font-size: 13px;
  color: #9ca3af;
}

.recommendation-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recommendation-card {
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.recommendation-card:hover {
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.recommendation-card--danger {
  border-left: 3px solid #ef4444;
  background: #fef2f2;
}

.recommendation-card--success {
  border-left: 3px solid #10b981;
  background: #f0fdf4;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.priority-rank {
  font-size: 12px;
  font-weight: 700;
  color: #ef4444;
  background: #fee2e2;
  padding: 2px 8px;
  border-radius: 4px;
}

.aspect-name {
  font-size: 15px;
  font-weight: 600;
  color: #111827;
}

.status-badge {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 999px;
  font-weight: 500;
}

.status-badge--success {
  background: #dcfce7;
  color: #16a34a;
}

.metrics-bars {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.bar-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.bar-label {
  color: #6b7280;
  min-width: 48px;
}

.bar-track {
  flex: 1;
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
}

.bar-fill {
  height: 100%;
  border-radius: 3px;
}

.bar-fill--danger { background: #ef4444; }
.bar-fill--success { background: #10b981; }
.bar-fill--accent { background: #2563eb; }

.bar-value {
  color: #374151;
  min-width: 48px;
  font-weight: 500;
}

.action-text {
  font-size: 13px;
  color: #4b5563;
  line-height: 1.5;
  margin: 0;
}

/* === Analysis Row === */
.analysis-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 32px;
}

.trend-card {
  /* wider */
}

/* === Quadrant Legend === */
.quadrant-legend {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.legend-item {
  font-size: 12px;
  color: #4b5563;
  display: flex;
  align-items: center;
  gap: 4px;
}

.legend-item--success { color: #10b981; }
.legend-item--danger { color: #ef4444; }
.legend-item--neutral { color: #6b7280; }
.legend-item--warning { color: #f59e0b; }

/* === PRCA List === */
.prca-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 260px;
  overflow-y: auto;
}

.prca-item {
  padding: 12px 16px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.prca-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.prca-name {
  font-size: 14px;
  font-weight: 600;
  color: #111827;
}

.prca-badge {
  font-size: 11px;
  padding: 3px 10px;
  border-radius: 6px;
  border: 1px solid;
}

.prca-metrics {
  font-size: 12px;
  color: #6b7280;
}

.metric-divider {
  margin: 0 8px;
  color: #d1d5db;
}

.prca-performance {
  font-size: 12px;
  color: #2563eb;
  margin-top: 4px;
}

/* === Data Distribution === */
.data-distribution {
  margin-bottom: 32px;
}

.distribution-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.distribution-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 16px;
}

.peak-highlight {
  padding: 16px;
  background: linear-gradient(135deg, #eff6ff, #f0f9ff);
  border-radius: 10px;
  text-align: center;
}

.peak-label {
  font-size: 11px;
  color: #6b7280;
}

.peak-value {
  font-size: 24px;
  font-weight: 700;
  color: #2563eb;
  display: block;
  margin-top: 4px;
}

.peak-count {
  font-size: 12px;
  color: #6b7280;
}

.coverage-note {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 12px;
}

.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.rank-name {
  color: #374151;
  min-width: 80px;
}

.rank-count {
  color: #6b7280;
  min-width: 50px;
}

.rank-bar {
  flex: 1;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
}

.rank-fill {
  height: 100%;
  background: linear-gradient(90deg, #2563eb, #60a5fa);
  border-radius: 4px;
}

/* === Methods Reference === */
.methods-reference {
  margin-bottom: 24px;
}

.methods-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.method-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}

.method-icon {
  font-size: 28px;
  display: block;
  margin-bottom: 8px;
}

.method-title {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 6px;
}

.method-desc {
  font-size: 12px;
  color: #6b7280;
  line-height: 1.4;
  margin: 0;
}

/* === Responsive === */
@media (max-width: 1200px) {
  .kpi-section { grid-template-columns: repeat(2, 1fr); }
  .core-analysis { grid-template-columns: 1fr; }
  .recommendations-grid { grid-template-columns: 1fr; }
  .analysis-row { grid-template-columns: 1fr; }
  .distribution-grid { grid-template-columns: 1fr 1fr; }
  .methods-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 600px) {
  .dashboard-container { padding: 16px; }
  .kpi-section { grid-template-columns: 1fr; }
  .distribution-grid { grid-template-columns: 1fr; }
  .methods-grid { grid-template-columns: 1fr; }
  .page-title { font-size: 22px; }
}
</style>
