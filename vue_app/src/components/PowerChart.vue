<script setup>
// vue-chartjs에서 필요한 차트 유형 임포트 (예: Line)
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement
} from 'chart.js';
import { ref, onMounted, computed } from 'vue';

// chart.js의 필요한 구성 요소 등록
ChartJS.register(Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale, PointElement);

const labels = ref([]);
const values = ref([]);
const chartKey = ref(0); // Optional: Keep this if you suspect rendering issues

onMounted(() => {
  labels.value = ['00:00', '01:00', '02:00', '03:00'];
  values.value = [120, 150, 100, 180];
  chartKey.value++; // Increment key to force re-render after data is set
});

const chartData = computed(() => ({
  labels: labels.value,
  datasets: [
    {
      label: 'Power (W)',
      data: values.value,
      borderColor: '#42b883',
      fill: false
    }
  ]
}));

const chartOptions = { responsive: true, maintainAspectRatio: false };
</script>

<template>
  <div style="height:300px">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>