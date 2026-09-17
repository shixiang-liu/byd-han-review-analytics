import { flushPromises, mount } from "@vue/test-utils";
import { createMemoryHistory, createRouter } from "vue-router";
import { afterEach, describe, expect, it, vi } from "vitest";
import sentimentInsight from "../../../public/data/sentiment-insight.json";
import PageHero from "../../components/PageHero.vue";
import InsightPage from "../InsightPage.vue";

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
  await router.push("/insight");
  await router.isReady();

  const wrapper = mount(InsightPage, {
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

describe("InsightPage", () => {
  it("renders the sentiment intelligence page from the exported payload", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(sentimentInsight),
        }),
      ),
    );

    const wrapper = await mountPage();

    const strongestAspect = [...sentimentInsight.aspectSentiment].sort(
      (left, right) => right.performance - left.performance,
    )[0];
    const weakestAspect = [...sentimentInsight.aspectSentiment].sort(
      (left, right) => left.performance - right.performance,
    )[0];
    const latestTrend = sentimentInsight.monthlyTrend.at(-1);
    const latestTrendStrongest = Object.entries(latestTrend ?? {})
      .filter(([key, value]) => key !== "month" && typeof value === "number")
      .sort((left, right) => (right[1] as number) - (left[1] as number))[0];

    expect(wrapper.findComponent(PageHero).props()).toMatchObject({
      section: "情感智能",
      title: "情感计算看板",
      description: expect.stringContaining("情感信号"),
    });
    expect(wrapper.text()).toContain("98.7%");
    expect(wrapper.text()).toContain("72.2%");
    expect(wrapper.text()).toContain(String(sentimentInsight.aspectSentiment.length));
    expect(wrapper.text()).toContain("维度情感表现");
    expect(wrapper.text()).toContain("负向主题聚类");
    expect(wrapper.text()).toContain("月度趋势洞察");
    expect(wrapper.text()).toContain(strongestAspect.aspectCn);
    expect(wrapper.text()).toContain(weakestAspect.aspectCn);
    expect(wrapper.text()).toContain(latestTrend?.month ?? "");
    expect(wrapper.text()).toContain(latestTrendStrongest?.[0] ?? "");
  });
});
