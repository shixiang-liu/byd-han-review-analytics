<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue';
import * as echarts from 'echarts';
import type { PerformanceScoresData } from '@/types/data';

const props = defineProps<{
  data: PerformanceScoresData | null;
  title?: string;
  height?: string;
}>();

const emit = defineEmits<{
  aspectClick: [aspect: string];
}>();

const chartRef = ref<HTMLDivElement | null>(null);
let chartInstance: echarts.ECharts | null = null;

const aspectNames: Record<string, string> = {
  space: '空间',
  driving: '驾驶感受',
  range: '续航',
  appearance: '外观',
  interior: '内饰',
  value: '性价比',
  smart: '智能化',
};

const initChart = () => {
  if (!chartRef.value || !props.data) return;

  chartInstance = echarts.init(chartRef.value);

  const items = props.data.items;

  const indicators = items.map((item) => ({
    name: item.aspectCn,
    max: 1,
    aspect: item.aspect,
  }));

  const performanceValues = items.map((item) => item.performance);
  const scoreNormValues = items.map((item) => item.scoreNorm);
  const sentimentNormValues = items.map((item) => item.sentimentNorm);

  const option: echarts.EChartsOption = {
    title: {
      text: props.title || '',
      left: 'center',
      top: 10,
      textStyle: {
        fontSize: 16,
        fontWeight: 600,
        color: '#334155',
      },
    },
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        const dataIndex = params.dataIndex || 0;
        const item = items[dataIndex];
        return `
          <div style="padding: 8px;">
            <div style="font-weight: 600; font-size: 14px;">${item.aspectCn}</div>
            <div style="margin-top: 6px;">
              <span style="color: #64748b;">综合绩效:</span>
              <span style="font-weight: 500; color: #0b5bd3;">${(item.performance * 100).toFixed(1)}%</span>
            </div>
            <div>
              <span style="color: #64748b;">评分归一:</span>
              <span style="font-weight: 500;">${(item.scoreNorm * 100).toFixed(1)}%</span>
            </div>
            <div>
              <span style="color: #64748b;">情感归一:</span>
              <span style="font-weight: 500;">${(item.sentimentNorm * 100).toFixed(1)}%</span>
            </div>
          </div>
        `;
      },
    },
    legend: {
      data: ['综合绩效', '评分归一', '情感归一'],
      bottom: 10,
      textStyle: {
        fontSize: 12,
        color: '#64748b',
      },
    },
    radar: {
      indicator: indicators,
      shape: 'polygon',
      splitNumber: 5,
      center: ['50%', '50%'],
      radius: '65%',
      axisName: {
        color: '#334155',
        fontSize: 12,
        fontWeight: 500,
      },
      splitLine: {
        lineStyle: {
          color: '#e2e8f0',
        },
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: ['#f8fafc', '#f1f5f9', '#e2e8f0', '#f1f5f9', '#f8fafc'],
        },
      },
      axisLine: {
        lineStyle: {
          color: '#cbd5e1',
        },
      },
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: performanceValues,
            name: '综合绩效',
            areaStyle: {
              color: 'rgba(11, 91, 211, 0.2)',
            },
            lineStyle: {
              color: '#0b5bd3',
              width: 2,
            },
            itemStyle: {
              color: '#0b5bd3',
            },
          },
          {
            value: scoreNormValues,
            name: '评分归一',
            areaStyle: {
              color: 'rgba(16, 185, 129, 0.15)',
            },
            lineStyle: {
              color: '#10b981',
              width: 2,
            },
            itemStyle: {
              color: '#10b981',
            },
          },
          {
            value: sentimentNormValues,
            name: '情感归一',
            areaStyle: {
              color: 'rgba(245, 158, 11, 0.15)',
            },
            lineStyle: {
              color: '#f59e0b',
              width: 2,
            },
            itemStyle: {
              color: '#f59e0b',
            },
          },
        ],
      },
    ],
  };

  chartInstance.setOption(option);

  // 点击事件
  chartInstance.on('click', (params: any) => {
    if (params.componentType === 'series' && params.name) {
      emit('aspectClick', params.name);
    }
  });

  // Resize处理
  const resizeObserver = new ResizeObserver(() => {
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
  chartInstance?.dispose();
});

watch(
  () => props.data,
  () => {
    if (chartInstance) {
      chartInstance.dispose();
    }
    initChart();
  },
  { deep: true }
);
</script>

<template>
  <div
    ref="chartRef"
    class="chart-container"
    :style="{ height: height || '360px' }"
  ></div>
</template>

<style scoped>
.chart-container {
  width: 100%;
  background: transparent;
}
</style>