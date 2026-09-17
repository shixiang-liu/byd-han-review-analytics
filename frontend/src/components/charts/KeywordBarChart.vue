<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue';
import * as echarts from 'echarts';
import type { KeywordAnalysisData } from '@/types/data';

const props = defineProps<{
  data: KeywordAnalysisData | null;
  title?: string;
  height?: string;
  topN?: number;
}>();

const chartRef = ref<HTMLDivElement | null>(null);
let chartInstance: echarts.ECharts | null = null;
let resizeObserver: ResizeObserver | null = null;

const aspectColors: Record<string, string> = {
  space: '#10b981',
  driving: '#0b5bd3',
  range: '#ef4444',
  appearance: '#f59e0b',
  interior: '#8b5cf6',
  value: '#ec4899',
  smart: '#06b6d4',
};

const initChart = () => {
  if (!chartRef.value || !props.data) return;

  chartInstance = echarts.init(chartRef.value);

  const topN = props.topN || 10;
  const keywords = [...props.data.keywords]
    .sort((a, b) => b.tfidfScore - a.tfidfScore)
    .slice(0, topN);

  const option: echarts.EChartsOption = {
    title: {
      text: props.title || '',
      left: 'center',
      top: 10,
      textStyle: {
        fontSize: 14,
        fontWeight: 600,
        color: '#334155',
      },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
      formatter: (params: any) => {
        const point = params[0];
        return `
          <div style="padding: 8px;">
            <div style="font-weight: 600; font-size: 14px;">${point.name}</div>
            <div style="margin-top: 6px;">
              <span style="color: #64748b;">TF-IDF 权重:</span>
              <span style="font-weight: 500;">${point.value.toFixed(4)}</span>
            </div>
            <div style="font-size: 11px; color: #94a3b8;">
              维度: ${keywords[point.dataIndex]?.aspectCn}
            </div>
          </div>
        `;
      },
    },
    grid: {
      left: 56,
      right: 20,
      top: 12,
      bottom: 8,
      containLabel: true,
    },
    xAxis: {
      type: 'value',
      name: 'TF-IDF',
      nameLocation: 'end',
      nameTextStyle: {
        fontSize: 11,
        color: '#64748b',
      },
      axisLine: {
        lineStyle: { color: '#e2e8f0' },
      },
      axisLabel: {
        color: '#64748b',
        fontSize: 10,
      },
      splitLine: {
        lineStyle: { color: '#f1f5f9', type: 'dashed' },
      },
    },
    yAxis: {
      type: 'category',
      data: keywords.map((item) => item.keyword),
      inverse: true,
      axisLine: {
        lineStyle: { color: '#e2e8f0' },
      },
      axisLabel: {
        color: '#334155',
        fontSize: 12,
        fontWeight: 500,
      },
    },
    series: [
      {
        type: 'bar',
        data: keywords.map((item) => ({
          value: item.tfidfScore,
          itemStyle: {
            color: aspectColors[item.aspect] || '#64748b',
            borderRadius: [0, 4, 4, 0],
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.2)',
            },
          },
        })),
        barWidth: '60%',
        label: {
          show: true,
          position: 'right',
          formatter: (params: any) => keywords[params.dataIndex]?.aspectCn ?? '',
          fontSize: 10,
          color: '#64748b',
          distance: 8,
        },
      },
    ],
  };

  chartInstance.setOption(option);

  resizeObserver?.disconnect();
  resizeObserver = new ResizeObserver(() => {
    chartInstance?.resize();
  });
  resizeObserver.observe(chartRef.value);
};

const resizeChart = () => {
  chartInstance?.resize();
};

onMounted(() => {
  initChart();
  window.addEventListener('resize', resizeChart);
});

onUnmounted(() => {
  window.removeEventListener('resize', resizeChart);
  resizeObserver?.disconnect();
  chartInstance?.dispose();
});

watch(
  () => props.data,
  () => {
    chartInstance?.dispose();
    initChart();
  },
  { deep: true },
);
</script>

<template>
  <div
    ref="chartRef"
    class="chart-container"
    :style="{ height: height || '320px' }"
  ></div>
</template>

<style scoped>
.chart-container {
  width: 100%;
  background: transparent;
}
</style>
