<template>
  <div class="current-power">
    <h2>{{ dashboardData.currentPower }} W</h2>
    <small class="timestamp">갱신 {{ lastUpdated }}</small>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useMockData } from '../composables/useMockData.js'
import { useApiSimulation } from '../composables/useApiSimulation.js'

/* 원래 코드 (백업용 - 복구 시 사용)
import { ref, onMounted, onUnmounted } from 'vue'
import api from '../services/api.js'
import socket from '../services/socket.js'

const currentPower = ref('--')
const lastUpdated  = ref('--')

function updateFromPayload (payload) {
  currentPower.value = Number(payload.electric).toFixed(1)
  lastUpdated.value  = new Date(payload.timestamp).toLocaleString()
}

async function fetchLatest () {
  try {
    const { data } = await api.getPowerData({ limit: 1 })
    if (data.length) updateFromPayload(data[0])
  } catch (e) {
    console.error('fetchLatest failed', e)
  }
}

onMounted(() => {
  fetchLatest()                 // 최초 1회
  socket.on('reading', updateFromPayload)  // 실시간 갱신
})
onUnmounted(() => {
  socket.off('reading', updateFromPayload) // 메모리 누수 방지
})
*/

const { dashboardData, updateDashboardData } = useMockData()
const { simulateRealTimeUpdates } = useApiSimulation()

const lastUpdated = computed(() => {
  return dashboardData.lastUpdated.toLocaleTimeString('ko-KR')
})

let updateInterval = null

onMounted(() => {
  // 3초마다 실시간 업데이트
  updateInterval = simulateRealTimeUpdates(() => {
    updateDashboardData()
  }, 3000)
})

onUnmounted(() => {
  if (updateInterval) {
    updateInterval()
  }
})
</script>

<style scoped>
.current-power { text-align:center; }
.timestamp     { font-size:.8rem; color:#666; }
</style> 