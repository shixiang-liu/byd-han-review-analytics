<script setup lang="ts">
defineProps<{
  section: string;
  title: string;
  description?: string;
}>();
</script>

<template>
  <section class="page-hero">
    <p class="page-eyebrow">{{ section }}</p>
    <h2 class="page-title">{{ title }}</h2>
    <p v-if="description" class="page-description">{{ description }}</p>
  </section>
</template>
