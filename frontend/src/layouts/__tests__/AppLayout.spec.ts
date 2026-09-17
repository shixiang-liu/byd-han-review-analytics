import { RouterLinkStub, mount } from "@vue/test-utils";
import { createMemoryHistory, createRouter } from "vue-router";
import { describe, expect, it } from "vitest";
import AppLayout from "../AppLayout.vue";

const menuItems = [
  { path: "/", label: "总览驾驶舱" },
  { path: "/decision", label: "决策分析中心" },
];

describe("AppLayout", () => {
  it("renders the BYD Han shell, route context, and filter labels", async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: "/decision",
          component: { template: "<div />" },
          meta: {
            section: "决策分析",
            label: "决策分析中心",
            description: "围绕 IPA、因果影响和策略优先级展开评审。",
          },
        },
      ],
    });

    await router.push("/decision");
    await router.isReady();

    const wrapper = mount(AppLayout, {
      props: { menuItems },
      slots: { default: "<div>body</div>" },
      global: {
        plugins: [router],
        stubs: {
          RouterLink: RouterLinkStub,
        },
      },
    });

    expect(wrapper.text()).toContain("BYD 汉产品决策分析平台");
    expect(wrapper.text()).toContain("决策分析");
    expect(wrapper.text()).toContain("决策分析中心");
    expect(wrapper.text()).toContain("围绕 IPA、因果影响和策略优先级展开评审。");
    expect(wrapper.text()).toContain("时间周期");
    expect(wrapper.text()).toContain("车型版本");
    expect(wrapper.text()).toContain("城市层级");
    expect(wrapper.text()).toContain("价格带");
    expect(wrapper.findAllComponents(RouterLinkStub)).toHaveLength(
      menuItems.length,
    );
    expect(wrapper.findComponent(RouterLinkStub).props("to")).toBe("/");
  });
});
