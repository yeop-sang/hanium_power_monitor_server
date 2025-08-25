<template>
  <div class="energy-analysis">
    <div class="container">
      <header class="page-header">
        <h1>📊 에너지 분석 및 AI 추천</h1>
        <p class="page-subtitle">전력 기기별 소비 패턴을 분석하고 AI 기반 절약 방법을 추천합니다</p>
      </header>

      <!-- 기간 선택 탭 -->
      <div class="period-tabs">
        <button 
          v-for="period in periods" 
          :key="period.key"
          class="period-tab"
          :class="{ 'period-tab--active': activePeriod === period.key }"
          @click="changePeriod(period.key)"
        >
          {{ period.label }}
        </button>
      </div>

      <!-- 차트 영역 -->
      <div class="charts-section">
        <div class="chart-container">
          <div class="chart-header">
            <h2>{{ currentPeriodData.title }}</h2>
            <div class="chart-loading" v-if="isLoading">
              <div class="spinner"></div>
              <span>데이터 로딩 중...</span>
            </div>
          </div>
          
          <div class="chart-wrapper">
            <canvas ref="chartCanvas" width="400" height="400"></canvas>
          </div>
          
          <div class="chart-summary">
            <div class="summary-item">
              <span class="summary-label">총 소비량:</span>
              <span class="summary-value">{{ totalConsumption }} kWh</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">최대 소비 기기:</span>
              <span class="summary-value">{{ maxConsumptionDevice }}</span>
            </div>
          </div>
        </div>

        <!-- AI 패턴 추론 패널 -->
        <div class="ai-panel">
          <div class="ai-panel__header">
            <h3>🤖 AI 패턴 분석 및 추천</h3>
            <div class="ai-status">
              <div class="ai-status__indicator"></div>
              <span>AI 분석 중...</span>
            </div>
          </div>
          
          <div class="recommendations">
            <div 
              v-for="recommendation in currentRecommendations" 
              :key="recommendation.id"
              class="recommendation-card"
              :class="`recommendation-card--${recommendation.priority}`"
            >
              <div class="recommendation-header">
                <span class="recommendation-type">{{ recommendation.type }}</span>
                <span class="recommendation-savings">{{ recommendation.savings }}</span>
              </div>
              <p class="recommendation-message">{{ recommendation.message }}</p>
            </div>
          </div>

          <div class="ai-actions">
            <button class="btn btn--primary" @click="refreshRecommendations">
              🔄 새로운 추천 받기
            </button>
            <button class="btn btn--secondary" @click="exportRecommendations">
              📥 추천사항 내보내기
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from 'vue';
import { Chart, registerables } from 'chart.js';

import { useMockData } from '../composables/useMockData.js';
import { useApiSimulation } from '../composables/useApiSimulation.js';

Chart.register(...registerables);

// Composables
const { energyMockData, aiRecommendations, updateEnergyData } = useMockData();
const { isLoading, simulateApiCall, simulateRealTimeUpdates } = useApiSimulation();

// Reactive data
const chartCanvas = ref(null);
const activePeriod = ref('daily');
let chartInstance = null;
let updateInterval = null;

const periods = [
  { key: 'daily', label: '일간', type: 'pie' },
  { key: 'weekly', label: '주간', type: 'bar' },
  { key: 'monthly', label: '월간', type: 'bar' }
];

// Computed properties
const currentPeriodData = computed(() => {
  const period = periods.find(p => p.key === activePeriod.value);
  const data = energyMockData[activePeriod.value];
  
  return {
    title: `${period.label} 전력 소비 분석`,
    type: period.type,
    data: period.type === 'pie' ? data.pie : data.bar
  };
});

const totalConsumption = computed(() => {
  const data = currentPeriodData.value.data;
  return data.reduce((sum, item) => sum + item.value, 0);
});

const maxConsumptionDevice = computed(() => {
  const data = currentPeriodData.value.data;
  const maxItem = data.reduce((max, item) => item.value > max.value ? item : max, data[0]);
  return maxItem.name || maxItem.day || maxItem.month;
});

const currentRecommendations = computed(() => {
  return aiRecommendations.value.slice(0, 3);
});

// Methods
const createChart = async () => {
  if (!chartCanvas.value) return;

  const ctx = chartCanvas.value.getContext('2d');
  const periodData = currentPeriodData.value;

  // 기존 차트 제거
  if (chartInstance) {
    chartInstance.destroy();
  }

  // 차트 설정
  const chartConfig = {
    type: periodData.type,
    data: {
      labels: periodData.data.map(item => item.name || item.day || item.month),
      datasets: [{
        label: '전력 소비량 (kWh)',
        data: periodData.data.map(item => item.value),
        backgroundColor: periodData.data.map(item => item.color),
        borderColor: periodData.data.map(item => item.color),
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: periodData.type === 'pie',
          position: 'right'
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              const value = context.parsed.y || context.parsed;
              return `${context.label}: ${value} kWh`;
            }
          }
        }
      },
      scales: periodData.type === 'bar' ? {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: '전력 소비량 (kWh)'
          }
        }
      } : {}
    }
  };

  // 애니메이션과 함께 차트 생성
  await simulateApiCall(async () => {
    chartInstance = new Chart(ctx, chartConfig);
  });
};

const changePeriod = async (period) => {
  activePeriod.value = period;
  await nextTick();
  await createChart();
};

const refreshRecommendations = async () => {
  await simulateApiCall(async () => {
    // AI 추천 새로고침 시뮬레이션
    const shuffled = [...aiRecommendations.value].sort(() => Math.random() - 0.5);
    aiRecommendations.value = shuffled;
  });
};

const exportRecommendations = async () => {
  await simulateApiCall(async () => {
    alert('추천사항이 성공적으로 내보내졌습니다!');
  });
};

// Lifecycle
onMounted(async () => {
  await nextTick();
  await createChart();
  
  // 실시간 데이터 업데이트 시뮬레이션 (5초마다)
  updateInterval = simulateRealTimeUpdates(() => {
    updateEnergyData();
    if (chartInstance && activePeriod.value === 'daily') {
      const newData = energyMockData.daily.pie.map(item => item.value);
      chartInstance.data.datasets[0].data = newData;
      chartInstance.update('none');
    }
  }, 5000);
});

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.destroy();
  }
  if (updateInterval) {
    updateInterval();
  }
});

// Watch for period changes
watch(activePeriod, () => {
  createChart();
});
</script>

<style scoped>
.energy-analysis {
  min-height: 100vh;
  background: #f8fafc;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 2.5rem;
  color: #1e293b;
  margin-bottom: 10px;
}

.page-subtitle {
  font-size: 1.1rem;
  color: #64748b;
  margin: 0;
}

.period-tabs {
  display: flex;
  justify-content: center;
  gap: 4px;
  margin-bottom: 30px;
  background: white;
  padding: 6px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  width: fit-content;
  margin-left: auto;
  margin-right: auto;
}

.period-tab {
  padding: 12px 24px;
  border: none;
  background: transparent;
  color: #64748b;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.period-tab--active {
  background: #4f46e5;
  color: white;
  box-shadow: 0 2px 4px rgba(79, 70, 229, 0.3);
}

.period-tab:hover:not(.period-tab--active) {
  background: #f1f5f9;
  color: #1e293b;
}

.charts-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 30px;
  align-items: start;
}

.chart-container {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-header h2 {
  font-size: 1.5rem;
  color: #1e293b;
  margin: 0;
}

.chart-loading {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #64748b;
  font-size: 0.9rem;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #e2e8f0;
  border-top: 2px solid #4f46e5;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.chart-wrapper {
  height: 400px;
  position: relative;
}

.chart-summary {
  display: flex;
  justify-content: space-around;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.summary-item {
  text-align: center;
}

.summary-label {
  display: block;
  font-size: 0.9rem;
  color: #64748b;
  margin-bottom: 4px;
}

.summary-value {
  display: block;
  font-size: 1.2rem;
  font-weight: 600;
  color: #1e293b;
}

.ai-panel {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  height: fit-content;
}

.ai-panel__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.ai-panel__header h3 {
  font-size: 1.3rem;
  color: #1e293b;
  margin: 0;
}

.ai-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  color: #10b981;
}

.ai-status__indicator {
  width: 8px;
  height: 8px;
  background: #10b981;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.recommendations {
  space-y: 16px;
}

.recommendation-card {
  padding: 16px;
  border-radius: 12px;
  border-left: 4px solid;
  margin-bottom: 16px;
  transition: transform 0.2s ease;
}

.recommendation-card:hover {
  transform: translateY(-2px);
}

.recommendation-card--high {
  background: #fef2f2;
  border-color: #ef4444;
}

.recommendation-card--medium {
  background: #fffbeb;
  border-color: #f59e0b;
}

.recommendation-card--low {
  background: #f0fdf4;
  border-color: #10b981;
}

.recommendation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.recommendation-type {
  font-size: 0.85rem;
  font-weight: 600;
  color: #374151;
}

.recommendation-savings {
  font-size: 0.85rem;
  font-weight: 600;
  color: #10b981;
}

.recommendation-message {
  font-size: 0.9rem;
  color: #4b5563;
  line-height: 1.5;
  margin: 0;
}

.ai-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.btn {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.9rem;
}

.btn--primary {
  background: #4f46e5;
  color: white;
}

.btn--primary:hover {
  background: #3730a3;
}

.btn--secondary {
  background: #f1f5f9;
  color: #475569;
}

.btn--secondary:hover {
  background: #e2e8f0;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .charts-section {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .period-tabs {
    width: 100%;
    justify-content: stretch;
  }
  
  .period-tab {
    flex: 1;
    padding: 10px 16px;
  }
  
  .ai-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>
