import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import BaseChart from "../BaseChart.vue";

describe("BaseChart", () => {
  it("renders a framed body and empty state", () => {
    const wrapper = mount(BaseChart, {
      props: {
        title: "Trend",
        description: "Monthly movement",
        empty: true,
        emptyText: "No chart data yet",
      },
    });

    expect(wrapper.text()).toContain("Trend");
    expect(wrapper.text()).toContain("Monthly movement");
    expect(wrapper.text()).toContain("No chart data yet");
    expect(wrapper.find(".base-chart__empty").exists()).toBe(true);
  });
});
