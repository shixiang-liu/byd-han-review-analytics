<script setup lang="ts">
/**
 * ChartCard - Professional chart container following shadcn Card patterns
 */
defineProps<{
  title: string;
  description?: string;
  height?: string;
  noPadding?: boolean;
}>();
</script>

<template>
  <div class="chart-card">
    <!-- Card Header -->
    <div class="chart-card__header">
      <div class="chart-card__header-left">
        <h3 class="chart-card__title">{{ title }}</h3>
        <p v-if="description" class="chart-card__description">{{ description }}</p>
      </div>
      <div v-if="$slots.actions" class="chart-card__actions">
        <slot name="actions" />
      </div>
    </div>

    <!-- Card Content -->
    <div
      class="chart-card__content"
      :class="{ 'chart-card__content--no-padding': noPadding }"
      :style="height ? { height } : {}"
    >
      <slot />
    </div>

    <!-- Card Footer -->
    <div v-if="$slots.footer" class="chart-card__footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<style scoped>
.chart-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
}

/* Header */
.chart-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 20px 24px 16px;
  border-bottom: 1px solid #f3f4f6;
}

.chart-card__header-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.chart-card__title {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.chart-card__description {
  font-size: 13px;
  color: #6b7280;
  margin: 0;
}

.chart-card__actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Content */
.chart-card__content {
  padding: 16px 24px;
  min-height: 200px;
}

.chart-card__content--no-padding {
  padding: 0;
}

/* Footer */
.chart-card__footer {
  padding: 16px 24px;
  border-top: 1px solid #f3f4f6;
  background: #f9fafb;
  font-size: 12px;
  color: #6b7280;
}
</style>