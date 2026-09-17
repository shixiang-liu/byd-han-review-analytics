import { ref } from "vue";

const defaultFilters = {
  timePeriod: "近 12 个月",
  modelVersion: "汉 DM-i",
  cityTier: "新一线",
  priceBand: "20-30 万",
} as const;

const timePeriodOptions = ["近 3 个月", "近 6 个月", "近 12 个月", "近 24 个月"];
const modelVersionOptions = ["汉 DM-i", "汉 EV", "汉 DM-p", "汉 L"];
const cityTierOptions = ["一线", "新一线", "二线", "三线及以下"];
const priceBandOptions = ["15-20 万", "20-30 万", "30-40 万", "40 万以上"];

const timePeriod = ref(defaultFilters.timePeriod);
const modelVersion = ref(defaultFilters.modelVersion);
const cityTier = ref(defaultFilters.cityTier);
const priceBand = ref(defaultFilters.priceBand);

const resetFilters = () => {
  timePeriod.value = defaultFilters.timePeriod;
  modelVersion.value = defaultFilters.modelVersion;
  cityTier.value = defaultFilters.cityTier;
  priceBand.value = defaultFilters.priceBand;
};

export function useDashboardFilters() {
  return {
    timePeriod,
    modelVersion,
    cityTier,
    priceBand,
    timePeriodOptions,
    modelVersionOptions,
    cityTierOptions,
    priceBandOptions,
    resetFilters,
  };
}
