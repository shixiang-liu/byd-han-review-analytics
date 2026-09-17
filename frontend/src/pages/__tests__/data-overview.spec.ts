import { flushPromises, mount } from "@vue/test-utils";
import { createMemoryHistory, createRouter } from "vue-router";
import { afterEach, describe, expect, it, vi } from "vitest";
import dataOverview from "../../../public/data/data-overview.json";
import PageHero from "../../components/PageHero.vue";
import DataOverviewPage from "../DataOverviewPage.vue";

function createTestRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: "/", component: { template: "<div />" } },
      { path: "/data-overview", component: { template: "<div />" } },
      { path: "/insight", component: { template: "<div />" } },
      { path: "/decision", component: { template: "<div />" } },
      { path: "/strategy", component: { template: "<div />" } },
    ],
  });
}

async function mountPage() {
  const router = createTestRouter();
  await router.push("/data-overview");
  await router.isReady();

  const wrapper = mount(DataOverviewPage, {
    global: {
      plugins: [router],
    },
  });

  await flushPromises();
  return wrapper;
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("DataOverviewPage", () => {
  it("renders the data foundation page from the exported payload", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(dataOverview),
        }),
      ),
    );

    const wrapper = await mountPage();

    const latestMonth =
      dataOverview.reviewTimeline[dataOverview.reviewTimeline.length - 1].month;
    const peakMonth = dataOverview.reviewTimeline.reduce((current, item) =>
      item.count > current.count ? item : current,
    );
    const weakestCoverage = dataOverview.scoreCoverage.reduce((current, item) =>
      item.share < current.share ? item : current,
    );

    expect(wrapper.findComponent(PageHero).props()).toMatchObject({
      section: "数据基础",
      title: "基础数据看板",
      description: expect.stringContaining("数据资产可信度"),
    });
    expect(wrapper.text()).toContain("8,424");
    expect(wrapper.text()).toContain(latestMonth);
    expect(wrapper.text()).toContain(peakMonth.month);
    expect(wrapper.text()).toContain(String(peakMonth.count));
    expect(wrapper.text()).toContain("车型样本分布");
    expect(wrapper.text()).toContain("城市样本分布");
    expect(wrapper.text()).toContain("价格带分布");
    expect(wrapper.text()).toContain("评分字段覆盖");
    expect(wrapper.text()).toContain(weakestCoverage.aspectCn);
  });

  it("renders the loading failure state when the payload request fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({
          ok: false,
          status: 500,
          statusText: "Server Error",
          json: () => Promise.resolve({}),
        }),
      ),
    );

    const wrapper = await mountPage();

    expect(wrapper.text()).toContain("Failed to load data-overview.json: 500 Server Error");
  });
});
