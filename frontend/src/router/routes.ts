export type AppRouteMeta = {
  label: string;
  section: string;
  description: string;
};

export type AppRouteRecord = {
  path: string;
  name: string;
  meta: AppRouteMeta;
};

export const appRoutes: readonly AppRouteRecord[] = [
  {
    path: "/",
    name: "dashboard",
    meta: {
      label: "决策支持平台",
      section: "比亚迪汉口碑分析",
      description: "基于真实用户评价的IPA分析、因果推断与改进建议。",
    },
  },
] as const;