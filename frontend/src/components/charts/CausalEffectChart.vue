<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue';
import * as echarts from 'echarts';
import type { CausalEffectData } from '@/types/data';

const props = defineProps<{
  data: CausalEffectData | null;
  title?: string;
  height?: string;
}>();

const chartRef = ref<HTMLDivElement | null>(null);
let chartInstance: echarts.ECharts | null = null;
let resizeObserver: ResizeObserver | null = null;

const initChart = () => {
  if (!chartRef.value) return;

  chartInstance = echarts.init(chartRef.value);

  if (!props.data || props.data.effects.length === 0) {
    chartInstance.setOption({
      title: {
        text: '暂无因果效应数据',
        left: 'center',
        top: 'middle',
        textStyle: {
          color: '#64748b',
          fontSize: 14,
        },
      },
    });
    return;
  }

  const effects = props.data.effects;
  const thetaValues = effects.map((effect) => effect.theta);
  const minTheta = Math.min(...thetaValues);
  const maxTheta = Math.max(...thetaValues);
  const axisPadding = Math.max((maxTheta - minTheta) * 0.18, 0.0025);

  const barData = effects.map((effect) => ({
    value: [effect.ciLower, effect.ciUpper, effect.theta],
    name: effect.aspectCn,
    aspect: effect.aspect,
  }));

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
      trigger: 'item',
      axisPointer: {
        type: 'shadow',
      },
      formatter: (params: any) => {
        const effect = effects[params.dataIndex];
        return `
          <div style="padding: 8px;">
            <div style="font-weight: 600; font-size: 14px;">${effect.aspectCn}</div>
            <div style="margin-top: 6px;">
              <span style="color: #64748b;">因果效应:</span>
              <span style="font-weight: 500; color: #0b5bd3;">${effect.theta.toFixed(4)}</span>
            </div>
            <div>
              <span style="color: #64748b;">置信区间:</span>
              <span style="font-weight: 500;">[${effect.ciLower.toFixed(4)}, ${effect.ciUpper.toFixed(4)}]</span>
            </div>
            <div style="font-size: 11px; color: #94a3b8;">
              标准误差: ${effect.se.toFixed(4)} | 样本数: ${effect.nUsed}
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
      name: '因果效应 (θ)',
      nameLocation: 'end',
      nameTextStyle: {
        fontSize: 11,
        color: '#64748b',
      },
      min: Math.max(0, Number((minTheta - axisPadding).toFixed(4))),
      max: Number((maxTheta + axisPadding).toFixed(4)),
      axisLine: {
        lineStyle: { color: '#e2e8f0' },
      },
      axisLabel: {
        color: '#64748b',
        fontSize: 10,
        formatter: (value: number) => value.toFixed(2),
      },
      splitLine: {
        lineStyle: { color: '#f1f5f9', type: 'dashed' },
      },
    },
    yAxis: {
      type: 'category',
      data: effects.map((effect) => effect.aspectCn),
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
        type: 'custom',
        renderItem: (params: any, api: any) => {
          const low = api.value(0);
          const high = api.value(1);
          const point = api.value(2);

          const lowCoord = api.coord([low, params.dataIndex]);
          const highCoord = api.coord([high, params.dataIndex]);
          const pointCoord = api.coord([point, params.dataIndex]);

          return {
            type: 'group',
            children: [
              {
                type: 'line',
                shape: {
                  x1: lowCoord[0],
                  y1: lowCoord[1],
                  x2: highCoord[0],
                  y2: highCoord[1],
                },
                style: {
                  stroke: '#94a3b8',
                  lineWidth: 2,
                },
              },
              {
                type: 'line',
                shape: {
                  x1: lowCoord[0],
                  y1: lowCoord[1] - 5,
                  x2: lowCoord[0],
                  y2: lowCoord[1] + 5,
                },
                style: {
                  stroke: '#94a3b8',
                  lineWidth: 2,
                },
              },
              {
                type: 'line',
                shape: {
                  x1: highCoord[0],
                  y1: highCoord[1] - 5,
                  x2: highCoord[0],
                  y2: highCoord[1] + 5,
                },
                style: {
                  stroke: '#94a3b8',
                  lineWidth: 2,
                },
              },
              {
                type: 'circle',
                shape: {
                  cx: pointCoord[0],
                  cy: pointCoord[1],
                  r: 5,
                },
                style: {
                  fill: '#0b5bd3',
                  stroke: '#fff',
                  lineWidth: 2,
                },
                emphasis: {
                  style: {
                    fill: '#053b93',
                    r: 7,
                  },
                },
              },
            ],
          };
        },
        data: barData,
        emphasis: {
          focus: 'self',
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
    :style="{ height: height || '280px' }"
  ></div>
</template>

<style scoped>
.chart-container {
  width: 100%;
  background: transparent;
}
</style>
