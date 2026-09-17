import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import InsightTag from "../InsightTag.vue";

describe("InsightTag", () => {
  it("renders the positive tone variant", () => {
    const wrapper = mount(InsightTag, {
      props: {
        label: "Validated",
        tone: "positive",
      },
    });

    expect(wrapper.text()).toBe("Validated");
    expect(wrapper.classes()).toContain("insight-tag--positive");
  });

  it("normalizes legacy success tone to the positive class", () => {
    const wrapper = mount(InsightTag, {
      props: {
        label: "Validated",
        tone: "success",
      },
    });

    expect(wrapper.text()).toBe("Validated");
    expect(wrapper.classes()).toContain("insight-tag--positive");
    expect(wrapper.classes()).not.toContain("insight-tag--success");
  });
});
