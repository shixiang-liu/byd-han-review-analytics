<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue';
import * as echarts from 'echarts';
import type { SentimentTrendData } from '@/types/data';

const props = defineProps<{
  data: SentimentTrendData | null;
  title?: string;
  height?: string;
  selectedAspects?: string[];
}>();

const chartRef = ref<HTMLDivElement | null>(null);
let chartInstance: echarts.ECharts | null = null;

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

  const trend = props.data.trend;
  const aspects = props.selectedAspects || props.data.aspects;

  // 构建xAxis数据（月份）
  const months = trend.map((t) => t.month);

  // 构建series数据
  const series = aspects.map((aspect) => ({
    name: props.data?.aspectNames[aspect] || aspect,
    type: 'line',
    smooth: true,
    symbol: 'none',
    lineStyle: {
      width: 2,
      color: aspectColors[aspect] || '#64748b',
    },
    itemStyle: {
      color: aspectColors[aspect] || '#64748b',
    },
    data: trend.map((t) => t.aspects[aspect] || null),
    emphasis: {
      focus: 'series',
    },
  }));

  // 添加总体平均线
  series.push({
    name: '总体平均',
    type: 'line',
    smooth: true,
    symbol: 'none',
    lineStyle: {
      width: 3,
      color: '#334155',
      type: 'solid',
    },
    itemStyle: {
      color: '#334155',
    },
    data: trend.map((t) => t.overall),
    emphasis: {
      focus: 'series',
    },
  });

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
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
      },
      formatter: (params: any) => {
        let html = `<div style="padding: 8px;"><div style="font-weight: 600; font-size: 14px;">${params[0].axisValue}</div>`;
        params.forEach((p: any) => {
          if (p.value != null) {
            html += `<div style="margin-top: 4px;">
              <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${p.color};margin-right:6px;"></span>
              <span style="color: #64748b;">${p.seriesName}:</span>
              <span style="font-weight: 500;">${p.value.toFixed(2)}</span>
            </div>`;
          }
        });
        html += '</div>';
        return html;
      },
    },
    legend: {
      data: series.map((s) => s.name),
      bottom: 10,
      textStyle: {
        fontSize: 11,
        color: '#64748b',
      },
      type: 'scroll',
    },
    grid: {
      left: 60,
      right: 40,
      top: 50,
      bottom: 80,
    },
    xAxis: {
      type: 'category',
      data: months,
      boundaryGap: false,
      axisLine: {
        lineStyle: { color: '#e2e8f0' },
      },
      axisLabel: {
        color: '#64748b',
        fontSize: 10,
        rotate: 45,
        formatter: (value: string) => {
          // 只显示年份和月份，简化显示
          const parts = value.split('-');
          return parts.length === 2 ? `${parts[0].slice(2)}-${parts[1]}` : value;
        },
      },
      splitLine: {
        show: false,
      },
    },
    yAxis: {
      type: 'value',
      min: 4,
      max: 5,
      name: '评分',
      nameLocation: 'middle',
      nameGap: 40,
      nameTextStyle: {
        fontSize: 12,
        color: '#64748b',
      },
      axisLine: {
        lineStyle: { color: '#e2e8f0' },
      },
      axisLabel: {
        color: '#64748b',
        formatter: (value: number) => value.toFixed(1),
      },
      splitLine: {
        lineStyle: { color: '#f1f5f9', type: 'dashed' },
      },
    },
    series,
  };

  chartInstance.setOption(option);

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

watch(
  () => props.selectedAspects,
  () => {
    if (chartInstance) {
      chartInstance.dispose();
    }
    initChart();
  }
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