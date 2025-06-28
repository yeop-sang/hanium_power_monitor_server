<script setup>
import PowerChart from '../components/PowerChart.vue'
import EnvironmentalData from '../components/EnvironmentalData.vue'
import CurrentPowerDisplay from '../components/CurrentPowerDisplay.vue'
</script>

<template>
  <section>
    <h1>Dashboard</h1>
    <CurrentPowerDisplay />
    <EnvironmentalData />
    <PowerChart />
  </section>
</template> 