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
import { ref, onMounted } from 'vue'
const temp = ref(24.5)
const humidity = ref(55)
const brightness = ref(800)
// later will fetch from API
</script>
<style scoped>
.env-grid{display:flex;gap:1rem}
.env-card{background:#ecf0f1;padding:1rem;border-radius:6px;flex:1;text-align:center}
</style> 