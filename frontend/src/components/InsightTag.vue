<script setup lang="ts">
import { computed } from "vue";

type LegacyTone = "success" | "info";
type CanonicalTone = "neutral" | "accent" | "positive" | "warning" | "critical";
type InsightTone = CanonicalTone | LegacyTone;

const props = withDefaults(
  defineProps<{
    label: string;
    tone?: InsightTone;
  }>(),
  {
    tone: "neutral",
  },
);

const resolvedTone = computed<CanonicalTone>(() => {
  if (props.tone === "success") {
    return "positive";
  }

  if (props.tone === "info") {
    return "accent";
  }

  return props.tone;
});
</script>

<template>
  <span class="insight-tag" :class="`insight-tag--${resolvedTone}`">
    {{ label }}
  </span>
</template>

<style scoped>
.insight-tag {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  min-height: 30px;
  padding: 0 12px;
  border: 1px solid transparent;
  border-radius: 999px;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.3);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.02em;
  white-space: nowrap;
}

.insight-tag--neutral {
  border-color: rgba(148, 163, 184, 0.18);
  background: rgba(148, 163, 184, 0.1);
  color: #cbd5e1;
}

.insight-tag--accent {
  border-color: rgba(59, 130, 246, 0.3);
  background: rgba(59, 130, 246, 0.15);
  color: #dbeafe;
}

.insight-tag--positive {
  border-color: rgba(16, 185, 129, 0.3);
  background: rgba(16, 185, 129, 0.16);
  color: #a7f3d0;
}

.insight-tag--warning {
  border-color: rgba(245, 158, 11, 0.3);
  background: rgba(245, 158, 11, 0.16);
  color: #fde68a;
}

.insight-tag--critical {
  border-color: rgba(220, 38, 38, 0.28);
  background: rgba(220, 38, 38, 0.14);
  color: #fecaca;
}
</style>
