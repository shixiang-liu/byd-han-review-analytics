<script setup lang="ts">
import { computed } from 'vue';
import type { IpaQuadrantData, KeywordAnalysisData, PerformanceScoresData, RecommendationItem } from '@/types/data';

const props = defineProps<{
  visible: boolean;
  aspect: string;
  ipaData: IpaQuadrantData | null;
  keywordsData: KeywordAnalysisData | null;
  performanceData: PerformanceScoresData | null;
  recommendations: RecommendationItem[] | null;
}>();

const emit = defineEmits<{
  'update:visible': [value: boolean];
  close: [];
}>();

// 使用computed getter/setter来处理v-model
const drawerVisible = computed({
  get: () => props.visible,
  set: (value: boolean) => {
    emit('update:visible', value);
    if (!value) {
      emit('close');
    }
  },
});

const aspectInfo = computed(() => {
  if (!props.ipaData || !props.aspect) return null;
  return props.ipaData.items.find((item) => item.aspect === props.aspect);
});

const aspectPerformance = computed(() => {
  if (!props.performanceData || !props.aspect) return null;
  return props.performanceData.items.find((item) => item.aspect === props.aspect);
});

const aspectKeywords = computed(() => {
  if (!props.keywordsData || !props.aspect) return [];
  const keywords = props.keywordsData.byAspect[props.aspect] || [];
  return keywords.slice(0, 5);
});

const aspectRecommendation = computed(() => {
  if (!props.recommendations || !props.aspect) return null;
  return props.recommendations.find((r) => r.aspect === props.aspect);
});

const quadrantColor = computed(() => {
  if (!aspectInfo.value) return '#64748b';
  const colors: Record<string, string> = {
    Q1: '#10b981',
    Q2: '#ef4444',
    Q3: '#64748b',
    Q4: '#f59e0b',
  };
  return colors[aspectInfo.value.quadrant] || '#64748b';
});
</script>

<template>
  <el-drawer
    v-model="drawerVisible"
    :title="aspectInfo?.aspectCn || '维度详情'"
    direction="rtl"
    :size="480"
    :with-header="true"
    class="aspect-detail-drawer"
  >
    <div v-if="aspectInfo" class="drawer-content">
      <!-- 象限定位 -->
      <div class="quadrant-badge" :style="{ backgroundColor: quadrantColor + '20', borderColor: quadrantColor }">
        <div class="quadrant-name" :style="{ color: quadrantColor }">
          {{ aspectInfo.quadrantName }}
        </div>
        <div class="quadrant-desc">
          {{ aspectInfo.quadrant }}象限 | 优先级 #{{ aspectInfo.priorityRank }}
        </div>
      </div>

      <!-- 核心指标 -->
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-label">表现度 (P)</div>
          <div class="metric-value">{{ (aspectInfo.performance * 100).toFixed(1) }}%</div>
          <div class="metric-bar">
            <div
              class="metric-bar-fill"
              :style="{ width: (aspectInfo.performance * 100) + '%', backgroundColor: quadrantColor }"
            ></div>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-label">重要性 (I)</div>
          <div class="metric-value">{{ (aspectInfo.importance * 100).toFixed(1) }}%</div>
          <div class="metric-bar">
            <div
              class="metric-bar-fill"
              :style="{ width: (aspectInfo.importance * 100) + '%', backgroundColor: '#0b5bd3' }"
            ></div>
          </div>
        </div>
      </div>

      <!-- 评分与情感 -->
      <div v-if="aspectPerformance" class="score-section">
        <div class="section-title">评分与情感</div>
        <div class="score-grid">
          <div class="score-item">
            <span class="score-label">平均评分</span>
            <span class="score-value">{{ aspectPerformance.scoreMean.toFixed(2) }}</span>
          </div>
          <div class="score-item">
            <span class="score-label">情感均值</span>
            <span class="score-value">{{ (aspectPerformance.sentimentMean * 100).toFixed(1) }}%</span>
          </div>
          <div class="score-item">
            <span class="score-label">评分样本</span>
            <span class="score-value">{{ aspectPerformance.nScore }}</span>
          </div>
          <div class="score-item">
            <span class="score-label">情感样本</span>
            <span class="score-value">{{ aspectPerformance.nSentiment }}</span>
          </div>
        </div>
      </div>

      <!-- 关键词 -->
      <div v-if="aspectKeywords.length > 0" class="keywords-section">
        <div class="section-title">问题关键词 TOP5</div>
        <div class="keywords-list">
          <div
            v-for="(kw, index) in aspectKeywords"
            :key="index"
            class="keyword-item"
          >
            <div class="keyword-rank">#{{ kw.rank }}</div>
            <div class="keyword-text">{{ kw.keyword }}</div>
            <div class="keyword-score">{{ kw.tfidfScore.toFixed(3) }}</div>
          </div>
        </div>
      </div>

      <!-- 改进建议 -->
      <div v-if="aspectRecommendation" class="recommendation-section">
        <div class="section-title">改进建议</div>
        <div class="recommendation-card">
          <div class="recommendation-text">{{ aspectRecommendation.recommendation }}</div>
          <div v-if="aspectRecommendation.keywords.length > 0" class="recommendation-tags">
            <span
              v-for="(kw, index) in aspectRecommendation.keywords"
              :key="index"
              class="tag"
            >
              {{ kw }}
            </span>
          </div>
        </div>
      </div>

      <!-- 行动建议 -->
      <div class="action-section">
        <div class="section-title">行动建议</div>
        <div class="action-text">{{ aspectInfo.action }}</div>
      </div>
    </div>
  </el-drawer>
</template>

<style scoped>
.drawer-content {
  padding: 0 24px;
}

.quadrant-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  border-radius: 12px;
  border: 2px solid;
  margin-bottom: 24px;
}

.quadrant-name {
  font-size: 18px;
  font-weight: 700;
}

.quadrant-desc {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.metric-card {
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
}

.metric-label {
  font-size: 12px;
  color: #64748b;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: #334155;
  margin-top: 4px;
}

.metric-bar {
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  margin-top: 8px;
}

.metric-bar-fill {
  height: 100%;
  border-radius: 3px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 12px;
}

.score-section {
  margin-bottom: 24px;
}

.score-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.score-item {
  display: flex;
  justify-content: space-between;
  padding: 12px;
  background: #f8fafc;
  border-radius: 6px;
}

.score-label {
  font-size: 12px;
  color: #64748b;
}

.score-value {
  font-size: 14px;
  font-weight: 600;
  color: #0b5bd3;
}

.keywords-section {
  margin-bottom: 24px;
}

.keywords-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.keyword-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background: #fef2f2;
  border-radius: 6px;
  gap: 12px;
}

.keyword-rank {
  font-size: 12px;
  font-weight: 600;
  color: #ef4444;
  min-width: 32px;
}

.keyword-text {
  font-size: 14px;
  font-weight: 500;
  color: #334155;
}

.keyword-score {
  font-size: 12px;
  color: #64748b;
}

.recommendation-section {
  margin-bottom: 24px;
}

.recommendation-card {
  padding: 16px;
  background: #f0f9ff;
  border-radius: 8px;
  border-left: 4px solid #0b5bd3;
}

.recommendation-text {
  font-size: 14px;
  color: #334155;
  line-height: 1.6;
}

.recommendation-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.tag {
  font-size: 12px;
  padding: 4px 10px;
  background: #e0f2fe;
  color: #0369a1;
  border-radius: 999px;
}

.action-section {
  margin-bottom: 24px;
}

.action-text {
  font-size: 14px;
  color: #475569;
  line-height: 1.6;
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
}
</style>