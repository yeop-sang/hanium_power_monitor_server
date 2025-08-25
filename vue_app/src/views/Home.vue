<script setup>
import PowerChart from '../components/PowerChart.vue'
import EnvironmentalData from '../components/EnvironmentalData.vue'
import CurrentPowerDisplay from '../components/CurrentPowerDisplay.vue'
</script>

<template>
  <div class="dashboard">
    <div class="container">
      <header class="dashboard-header">
        <h1>📊 실시간 전력 모니터링 대시보드</h1>
        <p class="dashboard-subtitle">전력 사용량과 환경 데이터를 실시간으로 모니터링합니다</p>
      </header>

      <div class="dashboard-grid">
        <!-- 현재 전력 표시 -->
        <div class="dashboard-card dashboard-card--highlight">
          <h3>🔌 현재 전력 사용량</h3>
          <CurrentPowerDisplay />
        </div>

        <!-- 환경 데이터 -->
        <div class="dashboard-card">
          <EnvironmentalData />
        </div>

        <!-- 전력 차트 -->
        <div class="dashboard-card dashboard-card--chart">
          <h3>📈 전력 사용량 추이 (최근 50분)</h3>
          <PowerChart />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: #f8fafc;
  padding: 20px 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.dashboard-header {
  text-align: center;
  margin-bottom: 30px;
}

.dashboard-header h1 {
  font-size: 2.5rem;
  color: #1e293b;
  margin-bottom: 10px;
}

.dashboard-subtitle {
  font-size: 1.1rem;
  color: #64748b;
  margin: 0;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto;
  gap: 24px;
}

.dashboard-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.dashboard-card:hover {
  transform: translateY(-2px);
}

.dashboard-card--highlight {
  background: white;
  color: #1e293b;
  text-align: center;
  border: 2px solid #e2e8f0;
}

.dashboard-card--highlight h3 {
  color: #1e293b;
  margin: 0 0 20px 0;
  font-size: 1.3rem;
}

.dashboard-card--chart {
  grid-column: 1 / -1;
}

.dashboard-card h3 {
  font-size: 1.3rem;
  color: #1e293b;
  margin: 0 0 20px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .dashboard-card--chart {
    grid-column: 1;
  }
  
  .dashboard-header h1 {
    font-size: 2rem;
  }
  
  .container {
    padding: 0 16px;
  }
}
</style> 