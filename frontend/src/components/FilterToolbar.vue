<script setup lang="ts">
import { useDashboardFilters } from "../composables/useDashboardFilters";

const {
  timePeriod,
  modelVersion,
  cityTier,
  priceBand,
  timePeriodOptions,
  modelVersionOptions,
  cityTierOptions,
  priceBandOptions,
  resetFilters,
} = useDashboardFilters();
</script>

<template>
  <section class="filter-toolbar" aria-label="dashboard filters">
    <div class="filter-field">
      <label class="filter-label" for="filter-time-period">时间周期</label>
      <select id="filter-time-period" v-model="timePeriod" class="filter-select">
        <option v-for="option in timePeriodOptions" :key="option" :value="option">
          {{ option }}
        </option>
      </select>
    </div>

    <div class="filter-field">
      <label class="filter-label" for="filter-model-version">车型版本</label>
      <select id="filter-model-version" v-model="modelVersion" class="filter-select">
        <option
          v-for="option in modelVersionOptions"
          :key="option"
          :value="option"
        >
          {{ option }}
        </option>
      </select>
    </div>

    <div class="filter-field">
      <label class="filter-label" for="filter-city-tier">城市层级</label>
      <select id="filter-city-tier" v-model="cityTier" class="filter-select">
        <option v-for="option in cityTierOptions" :key="option" :value="option">
          {{ option }}
        </option>
      </select>
    </div>

    <div class="filter-field">
      <label class="filter-label" for="filter-price-band">价格带</label>
      <select id="filter-price-band" v-model="priceBand" class="filter-select">
        <option v-for="option in priceBandOptions" :key="option" :value="option">
          {{ option }}
        </option>
      </select>
    </div>

    <div class="filter-actions">
      <button type="button" class="filter-reset" @click="resetFilters">
        重置筛选
      </button>
    </div>
  </section>
</template>
