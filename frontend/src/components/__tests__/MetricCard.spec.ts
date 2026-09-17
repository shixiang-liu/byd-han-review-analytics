import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import MetricCard from "../MetricCard.vue";

describe("MetricCard", () => {
  it("renders eyebrow, formatted value, trend, and tone", () => {
    const wrapper = mount(MetricCard, {
      props: {
        eyebrow: "Portfolio",
        title: "Active leads",
        value: 12345,
        subtitle: "Across all tracked regions",
        trend: "+12.4% vs last month",
        tone: "positive",
      },
    });

    expect(wrapper.text()).toContain("Portfolio");
    expect(wrapper.text()).toContain("Active leads");
    expect(wrapper.text()).toContain("12,345");
    expect(wrapper.text()).toContain("Across all tracked regions");
    expect(wrapper.text()).toContain("+12.4% vs last month");
    expect(wrapper.classes()).toContain("metric-card--positive");
  });
});
