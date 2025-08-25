<template>
  <div class="env-container">
    <div class="env-header">
      <h3>Environmental Data</h3>
      <div class="status-indicator">
        <span :class="['status-dot', connectionStatus]"></span>
        {{ connectionStatusText }}
      </div>
    </div>
    
    <div v-if="error" class="error-message">
      {{ error.message }}
      <button @click="retry" class="retry-btn">재시도</button>
    </div>
    
    <div v-else class="env-grid">
      <div class="env-card">
        <h4>Temperature</h4>
        <p class="value">{{ temp }} °C</p>
        <div v-if="loading" class="loading">로딩 중...</div>
      </div>
      <div class="env-card">
        <h4>Humidity</h4>
        <p class="value">{{ humidity }} %</p>
        <div v-if="loading" class="loading">로딩 중...</div>
      </div>
      <div class="env-card">
        <h4>Brightness</h4>
        <p class="value">{{ brightness }} lx</p>
        <div v-if="loading" class="loading">로딩 중...</div>
      </div>
      <div class="env-card">
        <h4>Electric Power</h4>
        <p class="value">{{ electric }} W</p>
        <div v-if="loading" class="loading">로딩 중...</div>
      </div>
    </div>
    
    <div class="last-updated">
      마지막 업데이트: {{ lastUpdated }}
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useMockData } from '../composables/useMockData.js'
import { useApiSimulation } from '../composables/useApiSimulation.js'

const { dashboardData, updateDashboardData } = useMockData()
const { simulateRealTimeUpdates } = useApiSimulation()

// 계산된 속성들
const temp = computed(() => dashboardData.temperature.toFixed(1))
const humidity = computed(() => dashboardData.humidity.toFixed(1))
const brightness = computed(() => dashboardData.brightness.toString())
const electric = computed(() => dashboardData.currentPower.toFixed(1))
const lastUpdated = computed(() => dashboardData.lastUpdated.toLocaleString('ko-KR'))

const connectionStatus = computed(() => {
  return dashboardData.isConnected ? 'connected' : 'disconnected'
})

const connectionStatusText = computed(() => {
  return dashboardData.isConnected ? '실시간 연결됨' : '연결 끊김'
})

const loading = computed(() => false) // 목업 데이터이므로 항상 false
const error = computed(() => null) // 목업 데이터이므로 에러 없음

let updateInterval = null

onMounted(() => {
  // 5초마다 실시간 업데이트
  updateInterval = simulateRealTimeUpdates(() => {
    updateDashboardData()
  }, 5000)
})

onUnmounted(() => {
  if (updateInterval) {
    updateInterval()
  }
})

// 재시도 함수 (목업에서는 실제로는 아무것도 하지 않음)
function retry() {
  // 목업 데이터에서는 항상 성공
}
</script>

<style scoped>
.env-container {
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.env-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.env-header h3 {
  margin: 0;
  color: #333;
}

.status-indicator {
  display: flex;
  align-items: center;
  font-size: 0.8rem;
  color: #666;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 0.5rem;
}

.status-dot.connected {
  background-color: #28a745;
}

.status-dot.connecting {
  background-color: #ffc107;
  animation: pulse 1.5s infinite;
}

.status-dot.error {
  background-color: #dc3545;
}

.status-dot.disconnected {
  background-color: #6c757d;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.retry-btn {
  background: #dc3545;
  color: white;
  border: none;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
}

.retry-btn:hover {
  background: #c82333;
}

.env-grid {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.env-card {
  background: white;
  padding: 1rem;
  border-radius: 6px;
  flex: 1;
  text-align: center;
  border: 1px solid #dee2e6;
  position: relative;
}

.env-card h4 {
  margin: 0 0 0.5rem 0;
  color: #495057;
  font-size: 0.9rem;
  font-weight: 600;
}

.value {
  font-size: 1.4rem;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255,255,255,0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  color: #666;
}

.last-updated {
  text-align: center;
  font-size: 0.75rem;
  color: #6c757d;
  margin-top: 0.5rem;
}

@media (max-width: 768px) {
  .env-grid {
    flex-direction: column;
  }
  
  .env-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style> 