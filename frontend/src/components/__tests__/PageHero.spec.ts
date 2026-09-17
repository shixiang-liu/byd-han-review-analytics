import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import PageHero from "../PageHero.vue";

describe("PageHero", () => {
  it("renders the section, title, and description", () => {
    const wrapper = mount(PageHero, {
      props: {
        section: "决策分析",
        title: "决策分析中心",
        description: "围绕 IPA、因果影响和策略优先级展开评审。",
      },
    });

    expect(wrapper.text()).toContain("决策分析");
    expect(wrapper.text()).toContain("决策分析中心");
    expect(wrapper.text()).toContain("围绕 IPA、因果影响和策略优先级展开评审。");
  });
});
