import { createMemoryHistory, createRouter } from "vue-router";
import { flushPromises, mount } from "@vue/test-utils";
import { afterEach, describe, expect, it, vi } from "vitest";
import dashboardSummary from "../../../public/data/dashboard-summary.json";
import decisionAnalysis from "../../../public/data/decision-analysis.json";
import strategySandbox from "../../../public/data/strategy-sandbox.json";
import HighlightPanel from "../../components/HighlightPanel.vue";
import MetricCard from "../../components/MetricCard.vue";
import PageHero from "../../components/PageHero.vue";
import SectionCard from "../../components/SectionCard.vue";
import DashboardPage from "../DashboardPage.vue";
import { appRoutes } from "../../router/routes";

const echartsMock = vi.hoisted(() => {
  const LinearGradient = vi.fn(function LinearGradient(...args: unknown[]) {
    return { args };
  });

  const init = vi.fn(() => ({
    setOption: vi.fn(),
    resize: vi.fn(),
    dispose: vi.fn(),
  }));

  return {
    init,
    LinearGradient,
  };
});

vi.mock("echarts", () => ({
  default: {
    init: echartsMock.init,
    graphic: {
      LinearGradient: echartsMock.LinearGradient,
    },
  },
}));

const payloads = {
  "/data/dashboard-summary.json": dashboardSummary,
  "/data/decision-analysis.json": decisionAnalysis,
  "/data/strategy-sandbox.json": strategySandbox,
};

function createTestRouter() {
  const routeComponents: Record<string, { template: string }> = {
    "/": { template: "<div />" },
    "/data-overview": { template: "<div />" },
    "/insight": { template: "<div />" },
    "/decision": { template: "<div />" },
    "/strategy": { template: "<div />" },
  };

  return createRouter({
    history: createMemoryHistory(),
    routes: appRoutes.map((route) => ({
      path: route.path,
      name: route.name,
      meta: route.meta,
      component: routeComponents[route.path],
    })),
  });
}

async function mountDashboardPage() {
  const router = createTestRouter();
  await router.push("/");
  await router.isReady();

  const wrapper = mount(DashboardPage, {
    global: {
      plugins: [router],
    },
  });

  await flushPromises();
  return wrapper;
}

function mockFetch(overrides: Partial<Record<string, boolean>> = {}) {
  vi.stubGlobal(
    "fetch",
    vi.fn((url: string) =>
      Promise.resolve({
        ok: overrides[url] ?? true,
        status: overrides[url] === false ? 500 : 200,
        statusText: overrides[url] === false ? "Server Error" : "OK",
        json: () => Promise.resolve(payloads[url as keyof typeof payloads]),
      }),
    ),
  );
}

function getMetricCard(wrapper: ReturnType<typeof mount>, title: string) {
  return wrapper
    .findAllComponents(MetricCard)
    .find((card) => card.props("title") === title);
}

describe("DashboardPage", () => {
  afterEach(() => {
    vi.clearAllMocks();
    vi.unstubAllGlobals();
  });

  it("renders the real dashboard route contract and the primary overview payload", async () => {
    mockFetch();

    const wrapper = await mountDashboardPage();

    expect(appRoutes[0]).toMatchObject({
      path: "/",
      meta: {
        label: "平台总览",
        section: "运营总览",
        description: "围绕评审视角、数据洞察和策略推演展开的产品决策工作台。",
      },
    });
    expect(wrapper.vm.$router.currentRoute.value.meta).toEqual(appRoutes[0].meta);
    expect(wrapper.findComponent(PageHero).props()).toMatchObject({
      section: "运营总览",
      title: "平台总览",
    });
    expect(wrapper.findAllComponents(HighlightPanel)).toHaveLength(2);
    expect(wrapper.findAllComponents(SectionCard).length).toBeGreaterThanOrEqual(3);

    const totalSampleCard = getMetricCard(wrapper, "总样本量");
    const decisionCard = getMetricCard(wrapper, "决策抓手");

    expect(totalSampleCard?.props("value")).toBe(dashboardSummary.sampleCount);
    expect(totalSampleCard?.props("subtitle")).toContain(dashboardSummary.projectName);
    expect(decisionCard?.props("value")).toBe(strategySandbox.priorityActions.length);
    expect(decisionCard?.props("subtitle")).toContain("Q1 1 / Q2 3");

    const topPriorityAction = strategySandbox.priorityActions.find(
      (item) => item.aspect === "interior",
    );
    expect(topPriorityAction).toBeTruthy();
    expect(wrapper.text()).toContain(dashboardSummary.priorityItems.join("、"));
    expect(wrapper.text()).toContain(dashboardSummary.strengthItems.join("、"));
    expect(wrapper.text()).toContain(`Priority ${topPriorityAction?.priorityRank}: ${topPriorityAction?.aspectCn}`);
    expect(wrapper.get('[data-testid="donut-chart"]').exists()).toBe(true);
    expect(wrapper.get('[data-testid="line-chart"]').exists()).toBe(true);
  });

  it("keeps the overview visible when a secondary payload fails", async () => {
    mockFetch({
      "/data/decision-analysis.json": false,
    });

    const wrapper = await mountDashboardPage();

    expect(appRoutes[0].meta.label).toBe("平台总览");
    expect(wrapper.findComponent(PageHero).props("title")).toBe("平台总览");
    expect(wrapper.text()).toContain("8,424");
    expect(wrapper.text()).toContain("Q1 -- / Q2 --");
    expect(wrapper.text()).toContain("决策分析数据暂未加载");
    expect(wrapper.findAllComponents(HighlightPanel)).toHaveLength(2);
    expect(wrapper.findAllComponents(MetricCard)).toHaveLength(4);
  });

  it("renders an error state when the dashboard payload request fails", async () => {
    mockFetch({
      "/data/dashboard-summary.json": false,
    });

    const wrapper = await mountDashboardPage();

    expect(wrapper.text()).toContain("Failed to load dashboard-summary.json");
    expect(wrapper.text()).toContain("500 Server Error");
  });
});
