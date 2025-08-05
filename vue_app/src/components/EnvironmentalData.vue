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
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { getLatestEnvironmentalData, isLoading } from '../services/api.js'
import { 
  isConnected, 
  isConnecting, 
  hasError as socketHasError, 
  safeOn, 
  validateReadingData 
} from '../services/socket.js'

const temp = ref('--')
const humidity = ref('--')
const brightness = ref('--')
const electric = ref('--')
const lastUpdated = ref('--')
const error = ref(null)
const fetchInterval = ref(null)

// 로딩 상태 (API 및 Socket 상태 기반)
const loading = computed(() => isLoading('latest_env_data'))

// 연결 상태 관리
const connectionStatus = computed(() => {
  if (socketHasError.value) return 'error'
  if (isConnected.value) return 'connected'
  if (isConnecting.value) return 'connecting'
  return 'disconnected'
})

const connectionStatusText = computed(() => {
  switch (connectionStatus.value) {
    case 'connected': return '실시간 연결됨'
    case 'connecting': return '연결 중...'
    case 'error': return '연결 오류'
    case 'disconnected': return '연결 끊김'
    default: return '알 수 없음'
  }
})

// 데이터 가져오기 함수
async function fetchLatest() {
  try {
    error.value = null
    const response = await getLatestEnvironmentalData()
    
    if (response.data) {
      updateData(response.data)
    }
  } catch (e) {
    console.error('Failed to fetch environmental data:', e)
    error.value = e
  }
}

// 데이터 업데이트 함수
function updateData(data) {
  temp.value = typeof data.temperature === 'number' ? data.temperature.toFixed(1) : '--'
  humidity.value = typeof data.humidity === 'number' ? data.humidity.toFixed(1) : '--'  
  brightness.value = typeof data.brightness === 'number' ? data.brightness.toString() : '--'
  electric.value = typeof data.electric === 'number' ? data.electric.toFixed(1) : '--'
  lastUpdated.value = data.timestamp ? new Date(data.timestamp).toLocaleString() : new Date().toLocaleString()
}

// Socket 데이터 처리 함수
function handleSocketData(payload) {
  if (validateReadingData(payload)) {
    updateData(payload)
    error.value = null // 성공적으로 데이터를 받으면 에러 클리어
  } else {
    console.warn('Invalid socket data received:', payload)
  }
}

// 재시도 함수
function retry() {
  error.value = null
  fetchLatest()
}

// 초기화 및 정리
let unsubscribeSocket = null

onMounted(() => {
  fetchLatest()
  
  // 30초마다 백업 데이터 가져오기 (Socket이 실패할 경우)
  fetchInterval.value = setInterval(() => {
    if (!isConnected.value || error.value) {
      fetchLatest()
    }
  }, 30000)
  
  // Socket 이벤트 리스너 등록 (안전한 방식)
  unsubscribeSocket = safeOn('reading', handleSocketData)
})

onUnmounted(() => {
  if (fetchInterval.value) {
    clearInterval(fetchInterval.value)
  }
  if (unsubscribeSocket) {
    unsubscribeSocket()
  }
})
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