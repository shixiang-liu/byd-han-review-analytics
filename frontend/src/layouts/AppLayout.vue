<script setup lang="ts">
type MenuItem = {
  path: string;
  label: string;
};

const props = defineProps<{
  menuItems: MenuItem[];
}>();
</script>

<template>
  <div class="app-shell">
    <!-- 简洁顶部导航 -->
    <header class="top-bar">
      <div class="brand">
        <span class="brand-mark">汉</span>
        <span class="brand-name">比亚迪汉口碑分析决策支持系统</span>
      </div>
      <div class="meta">
        <span class="meta-item">基于真实用户评价数据</span>
        <span class="meta-divider">|</span>
        <span class="meta-item">IPA分析 · 因果推断 · 改进建议</span>
      </div>
    </header>

    <!-- 主内容 -->
    <main class="main-content">
      <slot />
    </main>

    <!-- 底部 -->
    <footer class="footer">
      <p>数据来源：汽车之家真实用户口碑 | 分析方法：IPA重要性-表现分析 + DML因果推断</p>
    </footer>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #0b5bd3, #6ea8ff);
  color: #fff;
  font-size: 18px;
  font-weight: 700;
  border-radius: 8px;
}

.brand-name {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #64748b;
}

.meta-divider {
  color: #cbd5e1;
}

.main-content {
  flex: 1;
  padding: 0;
}

.footer {
  padding: 12px 24px;
  background: #fff;
  border-top: 1px solid #e2e8f0;
  text-align: center;
}

.footer p {
  font-size: 12px;
  color: #64748b;
  margin: 0;
}
</style>
