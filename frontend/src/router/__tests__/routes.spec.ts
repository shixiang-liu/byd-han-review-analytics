import { describe, expect, it } from "vitest";
import { appRoutes } from "../routes";

describe("appRoutes", () => {
  it("defines the five primary pages in order", () => {
    expect(appRoutes.map((route) => route.name)).toEqual([
      "dashboard",
      "data-overview",
      "insight",
      "decision",
      "strategy",
    ]);
  });

  it("includes path, label, section, and description metadata for every page", () => {
    expect(appRoutes.map((route) => route.path)).toEqual([
      "/",
      "/data-overview",
      "/insight",
      "/decision",
      "/strategy",
    ]);

    expect(appRoutes.map((route) => route.meta.label)).toEqual([
      "平台总览",
      "数据资产总览",
      "用户口碑洞察",
      "决策分析中心",
      "策略建议沙盘",
    ]);

    expect(appRoutes.map((route) => route.meta.section)).toEqual([
      "运营总览",
      "数据资产",
      "口碑洞察",
      "决策分析",
      "策略沙盘",
    ]);

    expect(appRoutes.map((route) => route.meta.description)).toEqual([
      "围绕评审视角、数据洞察和策略推演展开的产品决策工作台。",
      "追踪样本规模、车型版本和城市分布。",
      "聚焦舆情趋势、情绪分布和高频问题。",
      "分析 IPA、因果影响和优先级排序结果。",
      "比较不同策略方向的收益、成本和可执行性。",
    ]);
  });
});
