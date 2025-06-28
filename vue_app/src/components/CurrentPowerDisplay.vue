<template>
  <div class="current-power">
    <h2>{{ currentPower }} W</h2>
    <small class="timestamp">갱신 {{ lastUpdated }}</small>
  </div>
</template>

<script setup>
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
</script>

<style scoped>
.current-power { text-align:center; }
.timestamp     { font-size:.8rem; color:#666; }
</style> 