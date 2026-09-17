<script setup lang="ts">
import InsightTag from "./InsightTag.vue";

const props = withDefaults(
  defineProps<{
    eyebrow?: string;
    title: string;
    summary: string;
    highlights?: string[];
    tone?: "neutral" | "accent" | "positive" | "warning" | "critical";
  }>(),
  {
    eyebrow: "",
    highlights: () => [],
    tone: "neutral",
  },
);

const toneLabel: Record<NonNullable<typeof props.tone>, string> = {
  neutral: "Insight",
  accent: "Opportunity",
  positive: "Validated",
  warning: "Watchlist",
  critical: "Priority",
};
</script>

<template>
  <section class="highlight-panel" :class="`highlight-panel--${tone}`">
    <header class="highlight-panel__header">
      <div class="highlight-panel__titles">
        <p v-if="eyebrow" class="highlight-panel__eyebrow">{{ eyebrow }}</p>
        <h3 class="highlight-panel__title">{{ title }}</h3>
      </div>
      <InsightTag :label="toneLabel[tone]" :tone="tone" />
    </header>

    <p class="highlight-panel__summary">{{ summary }}</p>

    <ul v-if="highlights.length" class="highlight-panel__list">
      <li
        v-for="(item, index) in highlights"
        :key="`${item}-${index}`"
        class="highlight-panel__item"
      >
        {{ item }}
      </li>
    </ul>
  </section>
</template>

<style scoped>
.highlight-panel {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 24px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  border-radius: 20px;
  background:
    radial-gradient(circle at top right, rgba(11, 91, 211, 0.14), transparent 32%),
    rgba(255, 255, 255, 0.94);
  box-shadow: var(--shadow-sm);
}

.highlight-panel--accent {
  border-color: rgba(59, 130, 246, 0.2);
}

.highlight-panel--positive {
  border-color: rgba(16, 185, 129, 0.2);
}

.highlight-panel--warning {
  border-color: rgba(245, 158, 11, 0.22);
}

.highlight-panel--critical {
  border-color: rgba(220, 38, 38, 0.24);
  background:
    radial-gradient(circle at top right, rgba(220, 38, 38, 0.12), transparent 32%),
    rgba(255, 255, 255, 0.94);
}

.highlight-panel__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.highlight-panel__titles {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.highlight-panel__eyebrow {
  color: var(--color-text-muted);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.highlight-panel__title {
  color: var(--color-text-heading);
  font-size: 24px;
  line-height: 1.15;
  font-weight: 800;
}

.highlight-panel__summary {
  max-width: 820px;
  margin: 0;
  color: var(--color-text-muted);
  font-size: 14px;
  line-height: 1.7;
}

.highlight-panel__list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.highlight-panel__item {
  padding: 12px 14px;
  border: 1px solid rgba(148, 163, 184, 0.14);
  border-radius: 14px;
  background: rgba(248, 250, 252, 0.8);
  color: var(--color-text-heading);
  font-size: 13px;
  font-weight: 600;
}
</style>
