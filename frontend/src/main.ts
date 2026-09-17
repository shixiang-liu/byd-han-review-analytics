import { createApp } from "vue";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import App from "./App.vue";
import router from "./router";
import "./styles/theme.css";
import "./styles/layout.css";

function renderBootstrapError(title: string, detail: string) {
  const root = document.querySelector("#app");
  if (!root) {
    return;
  }

  root.innerHTML = `
    <section style="min-height:100vh;padding:32px;background:#0f172a;color:#e2e8f0;font-family:Inter,'Microsoft YaHei',sans-serif;">
      <h1 style="margin:0 0 16px;font-size:24px;">${title}</h1>
      <pre style="white-space:pre-wrap;word-break:break-word;padding:16px;border-radius:12px;background:rgba(15,23,42,0.82);border:1px solid rgba(148,163,184,0.16);">${detail}</pre>
    </section>
  `;
}

window.addEventListener("error", (event) => {
  if (event.error instanceof Error) {
    renderBootstrapError(
      "前端运行错误",
      `${event.error.name}: ${event.error.message}`,
    );
  }
});

window.addEventListener("unhandledrejection", (event) => {
  const detail =
    event.reason instanceof Error
      ? `${event.reason.name}: ${event.reason.message}`
      : String(event.reason);
  renderBootstrapError("前端未处理异常", detail);
});

try {
  createApp(App).use(router).use(ElementPlus).mount("#app");
} catch (error) {
  const detail =
    error instanceof Error ? `${error.name}: ${error.message}` : String(error);
  renderBootstrapError("前端启动失败", detail);
  throw error;
}
