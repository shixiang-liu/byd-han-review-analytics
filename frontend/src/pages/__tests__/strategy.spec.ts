import { flushPromises, mount } from "@vue/test-utils";
import { createMemoryHistory, createRouter } from "vue-router";
import { afterEach, describe, expect, it, vi } from "vitest";
import strategySandbox from "../../../public/data/strategy-sandbox.json";
import StrategyPage from "../StrategyPage.vue";

describe("StrategyPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders the redesigned action board from the exported sandbox payload", async () => {
    const fetchMock = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(strategySandbox),
      }),
    );

    vi.stubGlobal("fetch", fetchMock);

    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: "/",
          component: { template: "<div />" },
          meta: { section: "运营总览", label: "平台总览", description: "" },
        },
        {
          path: "/strategy",
          component: { template: "<div />" },
          meta: {
            section: "策略沙盘",
            label: "策略建议沙盘",
            description: "比较不同策略方向的收益、成本和可执行性。",
          },
        },
      ],
    });

    await router.push("/strategy");
    await router.isReady();

    const wrapper = mount(StrategyPage, {
      global: {
        plugins: [router],
      },
    });

    await flushPromises();

    expect(fetchMock).toHaveBeenCalledWith("/data/strategy-sandbox.json");

    // Plan Task 5 assertions: new section titles
    expect(wrapper.text()).toContain("行动总览");
    expect(wrapper.text()).toContain("优先策略");
    expect(wrapper.text()).toContain("细分对比");

    // Data rendering
    expect(wrapper.text()).toContain(strategySandbox.priorityActions[0].action);
    expect(wrapper.text()).toContain(
      strategySandbox.priorityActions[0].keywords[0],
    );
    expect(wrapper.text()).toContain(
      strategySandbox.segmentComparisons.powertrain[0].segment,
    );
  });
});
