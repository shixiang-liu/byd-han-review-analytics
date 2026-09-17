<script setup lang="ts">
/**
 * StatCard - Professional ToB statistic card component
 * Follows shadcn Card patterns with Header/Content/Footer structure
 */
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    title: string;
    value: string | number;
    description?: string;
    trend?: "up" | "down" | "neutral";
    trendValue?: string;
    variant?: "default" | "accent" | "success" | "warning" | "danger";
    clickable?: boolean;
    icon?: string;
  }>(),
  {
    description: "",
    trend: "neutral",
    trendValue: "",
    variant: "default",
    clickable: false,
    icon: "",
  }
);

const emit = defineEmits<{
  click: [];
}>();

const formatValue = computed(() => {
  if (typeof props.value === "number") {
    return props.value.toLocaleString();
  }
  return props.value;
});

const variantClass = computed(() => `stat-card--${props.variant}`);
const trendClass = computed(() => `stat-card__trend--${props.trend}`);

const handleClick = () => {
  if (props.clickable) {
    emit("click");
  }
};
</script>

<template>
  <div
    class="stat-card"
    :class="[variantClass, { 'stat-card--clickable': clickable }]"
    @click="handleClick"
  >
    <!-- Card Header -->
    <div class="stat-card__header">
      <div class="stat-card__header-content">
        <div v-if="icon" class="stat-card__icon">{{ icon }}</div>
        <h3 class="stat-card__title">{{ title }}</h3>
      </div>
      <div v-if="trendValue" class="stat-card__trend-badge" :class="trendClass">
        <span v-if="trend === 'up'" class="trend-arrow">↑</span>
        <span v-if="trend === 'down'" class="trend-arrow">↓</span>
        <span>{{ trendValue }}</span>
      </div>
    </div>

    <!-- Card Content - Main Value -->
    <div class="stat-card__content">
      <div class="stat-card__value">{{ formatValue }}</div>
      <p v-if="description" class="stat-card__description">{{ description }}</p>
    </div>

    <!-- Card Footer - Additional info -->
    <div v-if="$slots.footer" class="stat-card__footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<style scoped>
.stat-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  transition: all 0.2s ease;
}

.stat-card--clickable {
  cursor: pointer;
}

.stat-card--clickable:hover {
  border-color: #d1d5db;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.stat-card--accent {
  border-left: 3px solid #2563eb;
}

.stat-card--success {
  border-left: 3px solid #10b981;
}

.stat-card--warning {
  border-left: 3px solid #f59e0b;
}

.stat-card--danger {
  border-left: 3px solid #ef4444;
}

/* Header */
.stat-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.stat-card__header-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-card__icon {
  font-size: 20px;
  color: #6b7280;
}

.stat-card__title {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin: 0;
}

.stat-card__trend-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}

.stat-card__trend--up {
  background: #dcfce7;
  color: #16a34a;
}

.stat-card__trend--down {
  background: #fee2e2;
  color: #dc2626;
}

.stat-card__trend--neutral {
  background: #f3f4f6;
  color: #6b7280;
}

.trend-arrow {
  font-size: 10px;
}

/* Content */
.stat-card__content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-card__value {
  font-size: 28px;
  font-weight: 700;
  color: #111827;
  line-height: 1.2;
}

.stat-card--accent .stat-card__value {
  color: #2563eb;
}

.stat-card--success .stat-card__value {
  color: #10b981;
}

.stat-card--warning .stat-card__value {
  color: #f59e0b;
}

.stat-card--danger .stat-card__value {
  color: #ef4444;
}

.stat-card__description {
  font-size: 13px;
  color: #6b7280;
  margin: 0;
  line-height: 1.4;
}

/* Footer */
.stat-card__footer {
  padding-top: 12px;
  border-top: 1px solid #f3f4f6;
  font-size: 12px;
  color: #9ca3af;
}
</style>