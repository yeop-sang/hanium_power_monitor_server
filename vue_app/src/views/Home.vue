<script setup>
import PowerChart from '../components/PowerChart.vue'
import EnvironmentalData from '../components/EnvironmentalData.vue'
import CurrentPowerDisplay from '../components/CurrentPowerDisplay.vue'
</script>

<template>
  <section>
    <h1>Dashboard</h1>
    <CurrentPowerDisplay />
    <div class="card">
      <EnvironmentalData />
    </div>
    <div class="card">
      <PowerChart />
    </div>
  </section>
</template> 