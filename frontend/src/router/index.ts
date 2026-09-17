import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";
import DashboardPage from "../pages/DashboardPage.vue";
import { appRoutes } from "./routes";

const routes: RouteRecordRaw[] = [
  {
    path: appRoutes[0].path,
    name: appRoutes[0].name,
    meta: appRoutes[0].meta,
    component: DashboardPage,
  },
  {
    path: "/:pathMatch(.*)*",
    redirect: "/",
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  },
});

export default router;