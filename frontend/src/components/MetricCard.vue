<script setup lang="ts">
import { computed } from "vue";
import { formatNumber } from "../utils/format";

const props = withDefaults(
  defineProps<{
    eyebrow?: string;
    title: string;
    value: string | number;
    subtitle?: string;
    trend?: string;
    tone?: "neutral" | "accent" | "positive" | "warning" | "critical";
    clickable?: boolean;
  }>(),
  {
    eyebrow: "",
    subtitle: "",
    trend: "",
    tone: "neutral",
    clickable: false,
  },
);

const emit = defineEmits<{
  click: [];
}>();

const displayValue = computed(() =>
  typeof props.value === "number" ? formatNumber(props.value) : props.value,
);

const handleClick = () => {
  if (props.clickable) {
    emit('click');
  }
};
</script>

<template>
  <section
    class="metric-card"
    :class="[`metric-card--${tone}`, { 'metric-card--clickable': clickable }]"
    @click="handleClick"
  >
    <div v-if="eyebrow || trend" class="metric-card__meta">
      <p v-if="eyebrow" class="metric-card__eyebrow">{{ eyebrow }}</p>
      <span v-if="trend" class="metric-card__trend">{{ trend }}</span>
    </div>

    <div class="metric-card__header">
      <p class="metric-title">{{ title }}</p>
      <span class="metric-card__tone" :class="`metric-card__tone--${tone}`" />
    </div>

    <div class="metric-value">{{ displayValue }}</div>
    <p v-if="subtitle" class="metric-subtitle">{{ subtitle }}</p>
    <slot />
  </section>
</template>

<style scoped>
.metric-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.metric-card__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.metric-card__eyebrow {
  color: var(--color-text-muted);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.metric-card__trend {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  padding: 0 10px;
  border-radius: 999px;
  color: var(--color-primary-strong);
  background: var(--color-primary-soft);
  font-size: 12px;
  font-weight: 700;
}

.metric-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.metric-card__tone {
  width: 12px;
  height: 12px;
  border-radius: 999px;
  flex-shrink: 0;
}

.metric-card__tone--neutral {
  background: linear-gradient(135deg, #94a3b8, #cbd5e1);
}

.metric-card__tone--accent {
  background: linear-gradient(135deg, #0b5bd3, #6ea8ff);
}

.metric-card__tone--positive {
  background: linear-gradient(135deg, #059669, #34d399);
}

.metric-card__tone--warning {
  background: linear-gradient(135deg, #d97706, #fbbf24);
}

.metric-card__tone--critical {
  background: linear-gradient(135deg, #dc2626, #fb7185);
}

.metric-card--clickable {
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.metric-card--clickable:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.metric-card--clickable:active {
  transform: translateY(0);
}
</style>
