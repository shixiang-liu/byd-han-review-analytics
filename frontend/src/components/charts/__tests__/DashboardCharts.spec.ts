import { mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";
import CausalEffectChart from "../CausalEffectChart.vue";
import KeywordBarChart from "../KeywordBarChart.vue";
import type { CausalEffectData, KeywordAnalysisData } from "@/types/data";

const echartsInstances: Array<{
  setOption: ReturnType<typeof vi.fn>;
  resize: ReturnType<typeof vi.fn>;
  dispose: ReturnType<typeof vi.fn>;
}> = [];

vi.mock("echarts", () => ({
  init: vi.fn(() => {
    const instance = {
      setOption: vi.fn(),
      resize: vi.fn(),
      dispose: vi.fn(),
    };
    echartsInstances.push(instance);
    return instance;
  }),
}));

const causalData: CausalEffectData = {
  effects: [
    {
      aspect: "interior",
      aspectCn: "内饰",
      theta: 0.1403,
      se: 0.0006,
      ciLower: 0.1391,
      ciUpper: 0.1415,
      pValue: 0,
      nUsed: 5838,
    },
  ],
  totalCount: 1,
};

const keywordData: KeywordAnalysisData = {
  keywords: [
    {
      aspect: "interior",
      aspectCn: "内饰",
      rank: 1,
      keyword: "异味",
      keywordRaw: "内饰 异味",
      tfidfScore: 0.047,
      scoreType: "contrastive_tfidf_ngram",
      keywordType: "negative_theme_phrase",
    },
    {
      aspect: "range",
      aspectCn: "续航",
      rank: 1,
      keyword: "掉电",
      keywordRaw: "高速 掉电",
      tfidfScore: 0.03,
      scoreType: "contrastive_tfidf_ngram",
      keywordType: "negative_theme_phrase",
    },
  ],
  byAspect: {
    interior: [],
    range: [],
  },
  totalCount: 2,
};

beforeEach(() => {
  echartsInstances.length = 0;
  vi.stubGlobal(
    "ResizeObserver",
    class {
      observe() {}
      disconnect() {}
    },
  );
});

describe("dashboard charts", () => {
  it("reads DML custom-series values by dimension so the plot can render", () => {
    mount(CausalEffectChart, {
      props: {
        data: causalData,
      },
    });

    const option = echartsInstances[0].setOption.mock.calls[0][0];
    const renderItem = option.series[0].renderItem as (
      params: { dataIndex: number },
      api: { value: (dimension?: number) => unknown; coord: (value: number[]) => number[] },
    ) => unknown;

    const value = [0.1391, 0.1415, 0.1403, 0.1397, 0.1409];

    const shape = renderItem(
      { dataIndex: 0 },
      {
        value: (dimension?: number) => {
          if (dimension === undefined) {
            throw new Error("dimension is required");
          }
          return value[dimension];
        },
        coord: ([x, y]) => [x * 1000, y * 20],
      },
    ) as { children: Array<{ shape: Record<string, number> }> };

    expect(shape.children).toHaveLength(4);
    expect(shape.children[0].shape).toMatchObject({
      x1: 139.1,
      x2: 141.5,
    });
    expect(shape.children[3].shape).toMatchObject({
      cx: 140.3,
      cy: 0,
    });
  });

  it("keeps the keyword and DML chart grids compact inside dashboard cards", () => {
    mount(KeywordBarChart, {
      props: {
        data: keywordData,
        topN: 2,
      },
    });

    mount(CausalEffectChart, {
      props: {
        data: causalData,
      },
    });

    const keywordOption = echartsInstances[0].setOption.mock.calls[0][0];
    const causalOption = echartsInstances[1].setOption.mock.calls[0][0];

    expect(keywordOption.grid).toMatchObject({
      left: 56,
      right: 20,
      top: 12,
      bottom: 8,
    });
    expect(causalOption.grid).toMatchObject({
      left: 56,
      right: 20,
      top: 12,
      bottom: 8,
    });
  });
});
