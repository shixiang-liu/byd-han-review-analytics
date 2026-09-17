<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue';
import * as echarts from 'echarts';
import type { IpaQuadrantData } from '@/types/data';

const props = defineProps<{
  data: IpaQuadrantData | null;
  title?: string;
  height?: string;
}>();

const emit = defineEmits<{
  pointClick: [aspect: string];
}>();

const chartRef = ref<HTMLDivElement | null>(null);
let chartInstance: echarts.ECharts | null = null;

const quadrantColors = {
  Q1: '#10b981', // 绿色 - 优势保持区
  Q2: '#ef4444', // 红色 - 重点改进区
  Q3: '#64748b', // 灰色 - 低优先区
  Q4: '#f59e0b', // 橙色 - 过度投入区
};

const initChart = () => {
  if (!chartRef.value || !props.data) return;

  chartInstance = echarts.init(chartRef.value);

  const scatterData = props.data.items.map((item) => ({
    value: [item.performance, item.importance],
    name: item.aspectCn,
    aspect: item.aspect,
    quadrant: item.quadrant,
    itemStyle: {
      color: quadrantColors[item.quadrant as keyof typeof quadrantColors],
    },
    symbolSize: 24,
    emphasis: {
      scale: 1.5,
      itemStyle: {
        shadowBlur: 10,
        shadowColor: 'rgba(0, 0, 0, 0.3)',
      },
    },
  }));

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
        const data = params.data;
        return `
          <div style="padding: 8px;">
            <div style="font-weight: 600; font-size: 14px;">${data.name}</div>
            <div style="margin-top: 6px;">
              <span style="color: #64748b;">表现度:</span>
              <span style="font-weight: 500;">${(data.value[0] * 100).toFixed(1)}%</span>
            </div>
            <div>
              <span style="color: #64748b;">重要性:</span>
              <span style="font-weight: 500;">${(data.value[1] * 100).toFixed(1)}%</span>
            </div>
            <div style="margin-top: 4px; color: ${quadrantColors[data.quadrant as keyof typeof quadrantColors]};">
              ${props.data?.quadrantDefinitions[data.quadrant]?.name}
            </div>
          </div>
        `;
      },
    },
    grid: {
      left: 60,
      right: 60,
      top: 50,
      bottom: 60,
    },
    xAxis: {
      type: 'value',
      min: 0,
      max: 1,
      name: '表现度 (P)',
      nameLocation: 'middle',
      nameGap: 35,
      nameTextStyle: {
        fontSize: 12,
        color: '#64748b',
      },
      axisLine: {
        lineStyle: { color: '#e2e8f0' },
      },
      axisLabel: {
        formatter: (value: number) => `${(value * 100).toFixed(0)}%`,
        color: '#64748b',
      },
      splitLine: {
        lineStyle: { color: '#f1f5f9', type: 'dashed' },
      },
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 1,
      name: '重要性 (I)',
      nameLocation: 'middle',
      nameGap: 45,
      nameTextStyle: {
        fontSize: 12,
        color: '#64748b',
      },
      axisLine: {
        lineStyle: { color: '#e2e8f0' },
      },
      axisLabel: {
        formatter: (value: number) => `${(value * 100).toFixed(0)}%`,
        color: '#64748b',
      },
      splitLine: {
        lineStyle: { color: '#f1f5f9', type: 'dashed' },
      },
    },
    series: [
      {
        type: 'scatter',
        data: scatterData,
        label: {
          show: true,
          formatter: (params: any) => params.data.name,
          position: 'top',
          fontSize: 11,
          color: '#334155',
          distance: 8,
        },
        emphasis: {
          focus: 'self',
        },
      },
    ],
    graphic: [
      // 象限分隔线
      {
        type: 'line',
        shape: {
          x1: 0.5,
          y1: 0,
          x2: 0.5,
          y2: 1,
        },
        style: {
          stroke: '#cbd5e1',
          lineWidth: 1,
          lineDash: [4, 4],
        },
        z: -10,
      },
      {
        type: 'line',
        shape: {
          x1: 0,
          y1: 0.5,
          x2: 1,
          y2: 0.5,
        },
        style: {
          stroke: '#cbd5e1',
          lineWidth: 1,
          lineDash: [4, 4],
        },
        z: -10,
      },
      // 象限标签
      {
        type: 'text',
        left: '75%',
        top: '15%',
        style: {
          text: '优势保持区',
          fill: '#10b981',
          fontSize: 12,
          fontWeight: 500,
          textAlign: 'center',
        },
        z: -10,
      },
      {
        type: 'text',
        left: '25%',
        top: '15%',
        style: {
          text: '重点改进区',
          fill: '#ef4444',
          fontSize: 12,
          fontWeight: 500,
          textAlign: 'center',
        },
        z: -10,
      },
      {
        type: 'text',
        left: '25%',
        top: '80%',
        style: {
          text: '低优先区',
          fill: '#64748b',
          fontSize: 12,
          fontWeight: 500,
          textAlign: 'center',
        },
        z: -10,
      },
      {
        type: 'text',
        left: '75%',
        top: '80%',
        style: {
          text: '过度投入区',
          fill: '#f59e0b',
          fontSize: 12,
          fontWeight: 500,
          textAlign: 'center',
        },
        z: -10,
      },
    ],
  };

  chartInstance.setOption(option);

  // 点击事件
  chartInstance.on('click', (params: any) => {
    if (params.componentType === 'series' && params.data.aspect) {
      emit('pointClick', params.data.aspect);
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