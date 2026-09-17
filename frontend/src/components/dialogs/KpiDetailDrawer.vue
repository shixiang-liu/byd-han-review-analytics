<script setup lang="ts">
import { computed } from 'vue';
import type { DashboardMetrics, IpaQuadrantData, PerformanceScoresData } from '@/types/data';

const props = defineProps<{
  visible: boolean;
  kpiType: string;
  metricsData: DashboardMetrics | null;
  ipaData: IpaQuadrantData | null;
  performanceData: PerformanceScoresData | null;
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

const kpiTitle = computed(() => {
  const titles: Record<string, string> = {
    sampleCount: '样本规模',
    analysisDimensions: '分析维度',
    priorityIssues: '重点问题',
    actionCount: '决策抓手',
  };
  return titles[props.kpiType] || '详情';
});

const kpiValue = computed(() => {
  if (!props.metricsData) return 0;
  return props.metricsData[props.kpiType as keyof DashboardMetrics] || 0;
});

const kpiDescription = computed(() => {
  const descriptions: Record<string, string> = {
    sampleCount: '本次分析基于比亚迪汉车主在各大汽车论坛、电商平台评价等渠道的真实口碑数据，经过严格的数据清洗和标准化处理后获得高质量样本。',
    analysisDimensions: '从用户口碑文本中通过NLP技术提取出7个核心评价维度：空间、驾驶感受、续航、外观、内饰、性价比、智能化。',
    priorityIssues: '根据IPA重要性-表现分析，识别出落入Q2象限（高重要性+低表现）的维度，这些是需要紧急投入资源改进的重点问题。',
    actionCount: '根据IPA分析，识别出落入Q1象限（高重要性+高表现）的维度，这些是企业的竞争优势，应继续保持并作为宣传重点。',
  };
  return descriptions[props.kpiType] || '';
});

const detailItems = computed(() => {
  if (props.kpiType === 'analysisDimensions' && props.performanceData) {
    return props.performanceData.items.map((item) => ({
      label: item.aspectCn,
      value: `${(item.performance * 100).toFixed(1)}%`,
      subValue: `评分: ${item.scoreMean.toFixed(2)} | 情感: ${(item.sentimentMean * 100).toFixed(1)}%`,
    }));
  }

  if (props.kpiType === 'priorityIssues' && props.ipaData) {
    return props.ipaData.items
      .filter((item) => item.quadrant === 'Q2')
      .sort((a, b) => a.priorityRank - b.priorityRank)
      .map((item) => ({
        label: item.aspectCn,
        value: `优先级 #${item.priorityRank}`,
        subValue: `表现: ${(item.performance * 100).toFixed(1)}% | 重要性: ${(item.importance * 100).toFixed(1)}%`,
        tone: 'critical',
      }));
  }

  if (props.kpiType === 'actionCount' && props.ipaData) {
    return props.ipaData.items
      .filter((item) => item.quadrant === 'Q1')
      .map((item) => ({
        label: item.aspectCn,
        value: `优势维度`,
        subValue: `表现: ${(item.performance * 100).toFixed(1)}% | 重要性: ${(item.importance * 100).toFixed(1)}%`,
        tone: 'positive',
      }));
  }

  return [];
});
</script>

<template>
  <el-drawer
    v-model="drawerVisible"
    :title="kpiTitle"
    direction="rtl"
    :size="480"
    :with-header="true"
    class="kpi-detail-drawer"
  >
    <div class="drawer-content">
      <!-- 核心指标 -->
      <div class="kpi-header">
        <div class="kpi-value">{{ kpiValue }}</div>
        <div class="kpi-type-label">{{ kpiTitle }}</div>
      </div>

      <!-- 说明文字 -->
      <div class="kpi-description">
        {{ kpiDescription }}
      </div>

      <!-- 详情列表 -->
      <div v-if="detailItems.length > 0" class="detail-list">
        <div class="detail-list-title">详细数据</div>
        <div class="detail-items">
          <div
            v-for="(item, index) in detailItems"
            :key="index"
            class="detail-item"
            :class="`detail-item--${item.tone || 'neutral'}`"
          >
            <div class="detail-item-label">{{ item.label }}</div>
            <div class="detail-item-value">{{ item.value }}</div>
            <div class="detail-item-sub">{{ item.subValue }}</div>
          </div>
        </div>
      </div>

      <!-- 样本规模特殊内容 -->
      <div v-if="kpiType === 'sampleCount'" class="sample-stats">
        <div class="sample-stats-title">数据来源分布</div>
        <div class="sample-stats-grid">
          <div class="stat-card">
            <div class="stat-value">汽车之家</div>
            <div class="stat-label">主要来源</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">2020-2026</div>
            <div class="stat-label">时间跨度</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">全国</div>
            <div class="stat-label">地域覆盖</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">多车型</div>
            <div class="stat-label">车型覆盖</div>
          </div>
        </div>
      </div>
    </div>
  </el-drawer>
</template>

<style scoped>
.drawer-content {
  padding: 0 24px;
}

.kpi-header {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 20px 0;
  border-bottom: 1px solid #e2e8f0;
}

.kpi-value {
  font-size: 36px;
  font-weight: 700;
  color: #0b5bd3;
  line-height: 1.2;
}

.kpi-type-label {
  font-size: 14px;
  color: #64748b;
  margin-top: 8px;
}

.kpi-description {
  font-size: 14px;
  color: #475569;
  line-height: 1.6;
  padding: 20px 0;
}

.detail-list {
  padding-top: 20px;
}

.detail-list-title {
  font-size: 14px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 12px;
}

.detail-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
  border-left: 4px solid #64748b;
}

.detail-item--critical {
  border-left-color: #ef4444;
  background: #fef2f2;
}

.detail-item--positive {
  border-left-color: #10b981;
  background: #f0fdf4;
}

.detail-item-label {
  font-size: 14px;
  font-weight: 600;
  color: #334155;
}

.detail-item-value {
  font-size: 12px;
  color: #0b5bd3;
  margin-top: 4px;
}

.detail-item-sub {
  font-size: 11px;
  color: #64748b;
  margin-top: 2px;
}

.sample-stats {
  padding-top: 20px;
}

.sample-stats-title {
  font-size: 14px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 12px;
}

.sample-stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.stat-card {
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
  text-align: center;
}

.stat-value {
  font-size: 14px;
  font-weight: 600;
  color: #0b5bd3;
}

.stat-label {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}
</style>