<template>
  <div class="env-grid">
    <div class="env-card">
      <h3>Temperature</h3>
      <p>{{ temp }} °C</p>
    </div>
    <div class="env-card">
      <h3>Humidity</h3>
      <p>{{ humidity }} %</p>
    </div>
    <div class="env-card">
      <h3>Brightness</h3>
      <p>{{ brightness }} lx</p>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import api from '../services/api.js'
import socket from '../services/socket.js'

const temp = ref('--')
const humidity = ref('--')
const brightness = ref('--')

async function fetchLatest() {
  try {
    const { data } = await api.getPowerData({ limit: 1 })
    if (data.length) {
      const [d] = data
      temp.value = d.temperature?.toFixed(1)
      humidity.value = d.humidity?.toFixed(1)
      brightness.value = d.brightness
    }
  } catch (e) {
    console.error('Failed to fetch env data', e)
  }
}

function handleSocket(payload) {
  temp.value = payload.temperature?.toFixed(1)
  humidity.value = payload.humidity?.toFixed(1)
  brightness.value = payload.brightness
}

onMounted(() => {
  fetchLatest()
  setInterval(fetchLatest, 30000) // 30초마다 갱신
  socket.on('reading', handleSocket)
})

onUnmounted(() => {
  socket.off('reading', handleSocket)
})
</script>
<style scoped>
.env-grid{display:flex;gap:1rem}
.env-card{background:#ecf0f1;padding:1rem;border-radius:6px;flex:1;text-align:center}
</style> 