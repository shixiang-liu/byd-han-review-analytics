<script setup lang="ts">
withDefaults(
  defineProps<{
    title?: string;
    description?: string;
    height?: string;
    empty?: boolean;
    emptyText?: string;
  }>(),
  {
    title: "",
    description: "",
    height: "280px",
    empty: false,
    emptyText: "No data available",
  },
);
</script>

<template>
  <section class="base-chart" :style="{ minHeight: height }">
    <header v-if="title || description || $slots.toolbar" class="base-chart__header">
      <div v-if="title || description" class="base-chart__titles">
        <h3 v-if="title" class="section-title">{{ title }}</h3>
        <p v-if="description" class="section-subtitle">{{ description }}</p>
      </div>
      <div v-if="$slots.toolbar" class="base-chart__toolbar">
        <slot name="toolbar" />
      </div>
    </header>

    <div class="base-chart__frame">
      <div v-if="empty" class="base-chart__empty">
        <p class="base-chart__empty-label">Nothing to render</p>
        <p class="base-chart__empty-text">{{ emptyText }}</p>
      </div>
      <div v-else class="base-chart__body">
        <slot />
      </div>
    </div>
  </section>
</template>

<style scoped>
.base-chart {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.base-chart__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.base-chart__titles {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.base-chart__toolbar {
  display: flex;
  justify-content: flex-end;
}

.base-chart__frame {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 18px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 18px;
  background:
    radial-gradient(circle at top right, rgba(11, 91, 211, 0.08), transparent 30%),
    rgba(255, 255, 255, 0.88);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.65);
}

.base-chart__body,
.base-chart__empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.base-chart__empty {
  align-items: center;
  gap: 6px;
  color: var(--color-text-muted);
  text-align: center;
}

.base-chart__empty-label {
  color: var(--color-text-heading);
  font-size: 15px;
  font-weight: 700;
}

.base-chart__empty-text {
  margin: 0;
  font-size: 13px;
}

.base-chart__body {
  min-width: 0;
}
</style>
