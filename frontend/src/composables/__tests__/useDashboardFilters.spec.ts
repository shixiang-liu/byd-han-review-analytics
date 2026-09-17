import { describe, expect, it } from "vitest";
import { useDashboardFilters } from "../useDashboardFilters";

describe("useDashboardFilters", () => {
  it("shares the same filter state across consumers and resets both views", () => {
    const first = useDashboardFilters();
    const second = useDashboardFilters();

    expect(first.timePeriod.value).toBe("近 12 个月");
    expect(second.timePeriod.value).toBe("近 12 个月");

    first.timePeriod.value = "近 6 个月";
    first.modelVersion.value = "汉 EV";
    first.cityTier.value = "一线";
    first.priceBand.value = "30-40 万";

    expect(second.timePeriod.value).toBe("近 6 个月");
    expect(second.modelVersion.value).toBe("汉 EV");
    expect(second.cityTier.value).toBe("一线");
    expect(second.priceBand.value).toBe("30-40 万");

    second.resetFilters();

    expect(first.timePeriod.value).toBe("近 12 个月");
    expect(first.modelVersion.value).toBe("汉 DM-i");
    expect(first.cityTier.value).toBe("新一线");
    expect(first.priceBand.value).toBe("20-30 万");
  });
});
