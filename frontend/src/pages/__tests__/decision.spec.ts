import { flushPromises, mount } from "@vue/test-utils";
import { createMemoryHistory, createRouter } from "vue-router";
import { describe, expect, it, vi } from "vitest";
import decisionAnalysis from "../../../public/data/decision-analysis.json";
import DecisionPage from "../DecisionPage.vue";

vi.stubGlobal(
  "fetch",
  vi.fn(() =>
    Promise.resolve({
      ok: true,
      json: () => Promise.resolve(decisionAnalysis),
    }),
  ),
);

describe("DecisionPage", () => {
  it("renders the redesigned decision evidence chain from the exported payload", async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: "/",
          component: { template: "<div />" },
          meta: { section: "运营总览", label: "平台总览", description: "" },
        },
        {
          path: "/decision",
          component: { template: "<div />" },
          meta: {
            section: "决策分析",
            label: "决策分析中心",
            description: "分析 IPA、因果影响和优先级排序结果。",
          },
        },
      ],
    });

    await router.push("/decision");
    await router.isReady();

    const wrapper = mount(DecisionPage, {
      global: {
        plugins: [router],
      },
    });
    await flushPromises();

    const focusAspect =
      decisionAnalysis.ipaMatrix.find((item) => item.quadrant === "Q2") ??
      decisionAnalysis.ipaMatrix[0];
    const causalEffect = decisionAnalysis.causalEffects[0];
    const evidenceRow =
      decisionAnalysis.penaltyReward[0] ??
      decisionAnalysis.innovationPriority[0];

    // Plan Task 5 assertions: new section titles
    expect(wrapper.text()).toContain("核心结论");
    expect(wrapper.text()).toContain("IPA 重点改进");
    expect(wrapper.text()).toContain("因果效应强度");
    expect(wrapper.text()).toContain("证据链");

    // Data rendering
    expect(wrapper.text()).toContain(focusAspect.quadrantName);
    expect(wrapper.text()).toContain(causalEffect.theta.toFixed(3));
    expect(wrapper.text()).toContain(
      `${causalEffect.ciLower.toFixed(3)} ~ ${causalEffect.ciUpper.toFixed(3)}`,
    );
    expect(wrapper.text()).toContain(evidenceRow.aspect);
  });
});
