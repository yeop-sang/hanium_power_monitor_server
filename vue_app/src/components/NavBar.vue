<template>
  <nav class="navbar">
    <div class="navbar-brand">
      <router-link to="/" class="brand-link">🏠 전력 모니터링 시스템</router-link>
    </div>
    <ul class="navbar-menu">
      <li><router-link to="/">📊 대시보드</router-link></li>
      <li><router-link to="/energy-analysis">⚡ 에너지 분석</router-link></li>
      <li><router-link to="/anomaly-detection">🚨 이상탐지</router-link></li>
      <li><router-link to="/esg-report">📋 ESG 보고서</router-link></li>
      <li><router-link to="/reports">📄 보고서 목록</router-link></li>
    </ul>
  </nav>
</template>

<style scoped>
.navbar {
  background: linear-gradient(135deg, #1e293b, #334155);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-brand .brand-link {
  color: #f8fafc;
  text-decoration: none;
  font-size: 1.3rem;
  font-weight: 700;
  transition: color 0.2s ease;
}

.navbar-brand .brand-link:hover {
  color: #cbd5e1;
}

.navbar-menu {
  list-style: none;
  display: flex;
  gap: 2rem;
  margin: 0;
  padding: 0;
  align-items: center;
}

.navbar-menu li {
  position: relative;
}

.navbar-menu a {
  color: #e2e8f0;
  text-decoration: none;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 6px;
  transition: all 0.2s ease;
  display: block;
}

.navbar-menu a:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #f8fafc;
}

.navbar-menu a.router-link-active {
  background: #4f46e5;
  color: white;
}



/* 반응형 디자인 */
@media (max-width: 768px) {
  .navbar {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }
  
  .navbar-menu {
    gap: 1rem;
    flex-wrap: wrap;
    justify-content: center;
  }
  

}
</style> 