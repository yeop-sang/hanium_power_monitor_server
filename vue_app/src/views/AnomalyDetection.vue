<template>
  <div class="anomaly-detection">
    <div class="container">
      <header class="page-header">
        <h1>🚨 실시간 이상탐지 시스템</h1>
        <p class="page-subtitle">전류 및 온도 이상 상황을 실시간으로 모니터링하고 즉시 알림을 제공합니다</p>
      </header>

      <!-- 시스템 상태 개요 -->
      <div class="status-overview">
        <div class="status-card" :class="{ 'status-card--alert': currentAlerts.length > 0 }">
          <div class="status-icon">
            {{ currentAlerts.length > 0 ? '🔴' : '🟢' }}
          </div>
          <div class="status-info">
            <h3>시스템 상태</h3>
            <p class="status-text">
              {{ currentAlerts.length > 0 ? '이상 상황 감지됨' : '정상 운영 중' }}
            </p>
            <p class="status-count">활성 알림: {{ currentAlerts.length }}개</p>
          </div>
        </div>

        <div class="monitoring-stats">
          <div class="stat-item">
            <span class="stat-label">모니터링 기간</span>
            <span class="stat-value">{{ monitoringTime }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">총 알림 수</span>
            <span class="stat-value">{{ totalAlerts }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">마지막 체크</span>
            <span class="stat-value">{{ lastCheckTime }}</span>
          </div>
        </div>
      </div>

      <!-- 실시간 상태 모니터 -->
      <div class="monitoring-section">
        <div class="monitor-grid">
          <!-- 전류 상태 -->
          <div class="monitor-panel">
            <div class="monitor-header">
              <h3>⚡ 전류 모니터링</h3>
              <div class="status-indicator" :class="currentStatus.current.class">
                {{ currentStatus.current.label }}
              </div>
            </div>
            <div class="monitor-content">
              <div class="current-reading">
                <span class="reading-value">{{ currentStatus.current.value.toFixed(2) }}</span>
                <span class="reading-unit">A</span>
              </div>
              <div class="reading-status">
                <div class="progress-bar">
                  <div 
                    class="progress-fill" 
                    :style="{ width: currentStatus.current.percentage + '%' }"
                    :class="currentStatus.current.class"
                  ></div>
                </div>
                <span class="threshold-info">임계값: 15.0A</span>
              </div>
            </div>
          </div>

          <!-- 온도 상태 -->
          <div class="monitor-panel">
            <div class="monitor-header">
              <h3>🌡️ 온도 모니터링</h3>
              <div class="status-indicator" :class="currentStatus.temperature.class">
                {{ currentStatus.temperature.label }}
              </div>
            </div>
            <div class="monitor-content">
              <div class="temperature-reading">
                <span class="reading-value">{{ currentStatus.temperature.value.toFixed(2) }}</span>
                <span class="reading-unit">°C</span>
              </div>
              <div class="reading-status">
                <div class="progress-bar">
                  <div 
                    class="progress-fill" 
                    :style="{ width: currentStatus.temperature.percentage + '%' }"
                    :class="currentStatus.temperature.class"
                  ></div>
                </div>
                <span class="threshold-info">임계값: 45.0°C</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 제어 패널
        <div class="control-panel">
          <h3>🔧 시스템 제어</h3>
          <div class="control-buttons">
            <button 
              class="btn btn--danger" 
              @click="triggerAnomaly('current')"
              :disabled="isLoading"
            >
              ⚡ 전류 이상 테스트
            </button>
            <button 
              class="btn btn--warning" 
              @click="triggerAnomaly('temperature')"
              :disabled="isLoading"
            >
              🌡️ 온도 이상 테스트
            </button>
            <button 
              class="btn btn--secondary" 
              @click="clearAllAlerts"
              :disabled="currentAlerts.length === 0"
            >
              🔄 모든 알림 지우기
            </button>
          </div>
        </div> -->
      </div>

      <!-- 알림 패널 -->
      <div class="alerts-section">
        <div class="alerts-header">
          <h3>📢 실시간 알림</h3>
          <div class="alerts-controls">
            <label class="toggle-switch">
              <input type="checkbox" v-model="autoAlertsEnabled">
              <span class="toggle-slider"></span>
              자동 알림
            </label>
          </div>
        </div>

        <div class="alerts-container">
          <div v-if="currentAlerts.length === 0" class="no-alerts">
            <div class="no-alerts-icon">✅</div>
            <p>현재 이상 상황이 감지되지 않았습니다</p>
            <small>시스템이 정상적으로 운영되고 있습니다</small>
          </div>

          <div 
            v-for="alert in currentAlerts" 
            :key="alert.id"
            class="alert-item"
            :class="`alert-item--${alert.type}`"
          >
            <div class="alert-icon">{{ alert.icon }}</div>
            <div class="alert-content">
              <div class="alert-header">
                <span class="alert-title">{{ alert.message }}</span>
                <span class="alert-time">{{ alert.timestamp }}</span>
              </div>
              <div class="alert-details">
                <span class="alert-severity">심각도: {{ alert.severity }}</span>
                <button class="alert-dismiss" @click="dismissAlert(alert.id)">
                  ✕
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 이상 발생 통계 -->
      <div class="statistics-section">
        <h3>📊 이상 발생 통계 (최근 24시간)</h3>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-number">{{ statistics.currentAnomalies }}</div>
            <div class="stat-label">전류 이상</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ statistics.temperatureAnomalies }}</div>
            <div class="stat-label">온도 이상</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ statistics.totalResolved }}</div>
            <div class="stat-label">해결된 문제</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ statistics.avgResponseTime }}</div>
            <div class="stat-label">평균 대응시간</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed, watch } from 'vue';

import { useMockData } from '../composables/useMockData.js';
import { useApiSimulation } from '../composables/useApiSimulation.js';

// Composables
const { generateRandomAnomaly } = useMockData();
const { isLoading, simulateApiCall } = useApiSimulation();

// Reactive data
const currentAlerts = ref([]);
const autoAlertsEnabled = ref(true);
const monitoringStartTime = ref(new Date());
const totalAlerts = ref(0);
const lastCheckTime = ref(new Date().toLocaleTimeString('ko-KR'));

// 실시간 상태 데이터
const currentStatus = reactive({
  current: {
    value: 12.3,
    percentage: 82,
    class: 'status--normal',
    label: '정상'
  },
  temperature: {
    value: 38.5,
    percentage: 85,
    class: 'status--normal',
    label: '정상'
  }
});

// 통계 데이터
const statistics = reactive({
  currentAnomalies: 3,
  temperatureAnomalies: 2,
  totalResolved: 18,
  avgResponseTime: '2.3분'
});

// Auto alert interval
let autoAlertInterval = null;
let statusUpdateInterval = null;

// Computed properties
const monitoringTime = computed(() => {
  const now = new Date();
  const diff = Math.floor((now - monitoringStartTime.value) / 1000 / 60);
  return `${diff}분`;
});

// Methods
const triggerAnomaly = async (type) => {
  await simulateApiCall(async () => {
    const anomaly = generateRandomAnomaly();
    anomaly.type = type; // 강제로 타입 설정
    
    currentAlerts.value.unshift(anomaly);
    totalAlerts.value++;
    
    // 상태 업데이트
    updateStatus(type, true);
    
    // 브라우저 알림
    if (Notification.permission === 'granted') {
      new Notification('이상 상황 감지!', {
        body: anomaly.message,
        icon: '/favicon.ico'
      });
    }
    
    // 시스템 알림음 (옵션)
    playAlertSound();
  });
};

const dismissAlert = (alertId) => {
  const index = currentAlerts.value.findIndex(alert => alert.id === alertId);
  if (index > -1) {
    currentAlerts.value.splice(index, 1);
  }
  
  // 알림이 없으면 상태를 정상으로 복구
  if (currentAlerts.value.length === 0) {
    resetStatus();
  }
};

const clearAllAlerts = () => {
  currentAlerts.value = [];
  resetStatus();
};

const updateStatus = (type, isAnomaly) => {
  if (type === 'current') {
    currentStatus.current.value = isAnomaly ? 16.8 : 12.3;
    currentStatus.current.percentage = isAnomaly ? 112 : 82;
    currentStatus.current.class = isAnomaly ? 'status--danger' : 'status--normal';
    currentStatus.current.label = isAnomaly ? '위험' : '정상';
  } else if (type === 'temperature') {
    currentStatus.temperature.value = isAnomaly ? 48.2 : 38.5;
    currentStatus.temperature.percentage = isAnomaly ? 107 : 85;
    currentStatus.temperature.class = isAnomaly ? 'status--warning' : 'status--normal';
    currentStatus.temperature.label = isAnomaly ? '경고' : '정상';
  }
};

const resetStatus = () => {
  currentStatus.current.value = 12.3;
  currentStatus.current.percentage = 82;
  currentStatus.current.class = 'status--normal';
  currentStatus.current.label = '정상';
  
  currentStatus.temperature.value = 38.5;
  currentStatus.temperature.percentage = 85;
  currentStatus.temperature.class = 'status--normal';
  currentStatus.temperature.label = '정상';
};

const playAlertSound = () => {
  // 간단한 알림음 (실제 프로젝트에서는 오디오 파일 사용)
  const context = new (window.AudioContext || window.webkitAudioContext)();
  const oscillator = context.createOscillator();
  const gainNode = context.createGain();
  
  oscillator.connect(gainNode);
  gainNode.connect(context.destination);
  
  oscillator.frequency.value = 800;
  oscillator.type = 'sine';
  gainNode.gain.setValueAtTime(0.3, context.currentTime);
  gainNode.gain.exponentialRampToValueAtTime(0.01, context.currentTime + 0.5);
  
  oscillator.start(context.currentTime);
  oscillator.stop(context.currentTime + 0.5);
};

const startAutoAlerts = () => {
  if (autoAlertInterval) return;
  
  autoAlertInterval = setInterval(() => {
    if (autoAlertsEnabled.value) { // 100% 확률로 변경
      const types = ['current', 'temperature'];
      const randomType = types[Math.floor(Math.random() * types.length)];
      triggerAnomaly(randomType);
    }
  }, 15000); // 15초마다 체크
};

const stopAutoAlerts = () => {
  if (autoAlertInterval) {
    clearInterval(autoAlertInterval);
    autoAlertInterval = null;
  }
};

const startStatusUpdates = () => {
  statusUpdateInterval = setInterval(() => {
    lastCheckTime.value = new Date().toLocaleTimeString('ko-KR');
    
    // 상태가 정상일 때만 값을 약간 변동
    if (currentAlerts.value.length === 0) {
      currentStatus.current.value = parseFloat((12.3 + (Math.random() - 0.5) * 2).toFixed(2));
      currentStatus.temperature.value = parseFloat((38.5 + (Math.random() - 0.5) * 3).toFixed(2));
    }
  }, 2000);
};

// Request notification permission
const requestNotificationPermission = async () => {
  if ('Notification' in window && Notification.permission === 'default') {
    await Notification.requestPermission();
  }
};

// Lifecycle
onMounted(() => {
  requestNotificationPermission();
  startAutoAlerts();
  startStatusUpdates();
});

onUnmounted(() => {
  stopAutoAlerts();
  if (statusUpdateInterval) {
    clearInterval(statusUpdateInterval);
  }
});

// Watch auto alerts setting
watch(autoAlertsEnabled, (enabled) => {
  if (enabled) {
    startAutoAlerts();
  } else {
    stopAutoAlerts();
  }
});
</script>

<style scoped>
.anomaly-detection {
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

.status-overview {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 20px;
  margin-bottom: 30px;
}

.status-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 20px;
  border: 2px solid #10b981;
  transition: all 0.3s ease;
}

.status-card--alert {
  border-color: #ef4444;
  background: linear-gradient(135deg, #fef2f2, white);
}

.status-icon {
  font-size: 3rem;
  animation: pulse 2s infinite;
}

.status-info h3 {
  font-size: 1.5rem;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.status-text {
  font-size: 1.1rem;
  color: #374151;
  margin: 0 0 4px 0;
}

.status-count {
  font-size: 0.9rem;
  color: #64748b;
  margin: 0;
}

.monitoring-stats {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #e2e8f0;
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  color: #64748b;
  font-size: 0.9rem;
}

.stat-value {
  color: #1e293b;
  font-weight: 600;
}

.monitoring-section {
  margin-bottom: 30px;
}

.monitor-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.monitor-panel {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.monitor-header h3 {
  font-size: 1.3rem;
  color: #1e293b;
  margin: 0;
}

.status-indicator {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}

.status--normal {
  background: #d1fae5;
  color: #065f46;
}

.status--warning {
  background: #fef3c7;
  color: #92400e;
}

.status--danger {
  background: #fee2e2;
  color: #991b1b;
}

.monitor-content {
  text-align: center;
}

.current-reading,
.temperature-reading {
  margin-bottom: 20px;
}

.reading-value {
  font-size: 3rem;
  font-weight: 700;
  color: #1e293b;
}

.reading-unit {
  font-size: 1.5rem;
  color: #64748b;
  margin-left: 8px;
}

.reading-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  transition: all 0.3s ease;
}

.progress-fill.status--normal {
  background: #10b981;
}

.progress-fill.status--warning {
  background: #f59e0b;
}

.progress-fill.status--danger {
  background: #ef4444;
}

.threshold-info {
  font-size: 0.8rem;
  color: #64748b;
}

.control-panel {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.control-panel h3 {
  font-size: 1.3rem;
  color: #1e293b;
  margin: 0 0 20px 0;
}

.control-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn {
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.9rem;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn--danger {
  background: #ef4444;
  color: white;
}

.btn--danger:hover:not(:disabled) {
  background: #dc2626;
}

.btn--warning {
  background: #f59e0b;
  color: white;
}

.btn--warning:hover:not(:disabled) {
  background: #d97706;
}

.btn--secondary {
  background: #f1f5f9;
  color: #475569;
}

.btn--secondary:hover:not(:disabled) {
  background: #e2e8f0;
}

.alerts-section {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.alerts-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.alerts-header h3 {
  font-size: 1.3rem;
  color: #1e293b;
  margin: 0;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 24px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: #4f46e5;
}

input:checked + .toggle-slider:before {
  transform: translateX(26px);
}

.alerts-container {
  max-height: 400px;
  overflow-y: auto;
}

.no-alerts {
  text-align: center;
  padding: 40px 20px;
  color: #64748b;
}

.no-alerts-icon {
  font-size: 3rem;
  margin-bottom: 16px;
}

.alert-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  border-radius: 12px;
  margin-bottom: 12px;
  border-left: 4px solid;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.alert-item--current {
  background: #fef2f2;
  border-color: #ef4444;
}

.alert-item--temperature {
  background: #fffbeb;
  border-color: #f59e0b;
}

.alert-icon {
  font-size: 1.5rem;
  margin-top: 2px;
}

.alert-content {
  flex: 1;
}

.alert-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.alert-title {
  font-weight: 600;
  color: #1e293b;
  line-height: 1.4;
}

.alert-time {
  font-size: 0.8rem;
  color: #64748b;
  white-space: nowrap;
  margin-left: 12px;
}

.alert-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.alert-severity {
  font-size: 0.8rem;
  color: #64748b;
}

.alert-dismiss {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.alert-dismiss:hover {
  background: rgba(0, 0, 0, 0.1);
  color: #1e293b;
}

.statistics-section {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.statistics-section h3 {
  font-size: 1.3rem;
  color: #1e293b;
  margin: 0 0 20px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.stat-card {
  text-align: center;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 0.9rem;
  color: #64748b;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .status-overview {
    grid-template-columns: 1fr;
  }
  
  .monitor-grid {
    grid-template-columns: 1fr;
  }
  
  .control-buttons {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .alert-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .alert-time {
    margin-left: 0;
  }
}
</style>
