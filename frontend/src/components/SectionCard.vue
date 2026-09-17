<script setup lang="ts">
defineProps<{
  eyebrow?: string;
  title: string;
  subtitle?: string;
}>();
</script>

<template>
  <section class="section-card">
    <header class="section-card__header">
      <div class="section-card__titles">
        <p v-if="eyebrow" class="section-card__eyebrow">{{ eyebrow }}</p>
        <div class="section-card__title-row">
          <h3 class="section-title">{{ title }}</h3>
          <slot name="toolbar" />
        </div>
        <p v-if="subtitle" class="section-subtitle">{{ subtitle }}</p>
      </div>

      <div v-if="$slots.actions" class="section-card__actions">
        <slot name="actions" />
      </div>
    </header>

    <div class="section-card__body">
      <slot />
    </div>
  </section>
</template>

<style scoped>
.section-card {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.section-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}

.section-card__titles {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.section-card__eyebrow {
  color: var(--color-text-muted);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.section-card__title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.section-card__actions {
  display: flex;
  justify-content: flex-end;
}

.section-card__body {
  min-width: 0;
}
</style>
