import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import FilterToolbar from "../FilterToolbar.vue";

describe("FilterToolbar", () => {
  it("renders the shared filter labels", () => {
    const wrapper = mount(FilterToolbar);

    expect(wrapper.text()).toContain("时间周期");
    expect(wrapper.text()).toContain("车型版本");
    expect(wrapper.text()).toContain("城市层级");
    expect(wrapper.text()).toContain("价格带");
  });
});
