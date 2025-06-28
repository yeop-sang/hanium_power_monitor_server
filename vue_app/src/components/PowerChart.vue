<script setup>
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
import { ref, onMounted, onUnmounted, computed } from 'vue';
import api from '../services/api.js';
import socket from '../services/socket.js';

ChartJS.register(Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale, PointElement);

const labels = ref([]);
const values = ref([]);
const loading = ref(true);
const interval = ref(null);
const dataPoints = ref([]);
const chartKey = ref(0);

async function fetchData() {
  try {
    const { data } = await api.getPowerData({ limit: 50 });
    // 데이터가 최신순으로 오므로 역순 정렬해 시간순 정렬
    const sorted = data.slice().reverse();
    labels.value = sorted.map(r => new Date(r.timestamp).toLocaleTimeString());
    values.value = sorted.map(r => r.electric);
  } catch (e) {
    console.error('Failed to fetch power data', e);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  fetchData();
  interval.value = setInterval(fetchData, 60000);
  socket.on('reading', appendPoint);
});

onUnmounted(() => {
  clearInterval(interval.value);
  socket.off('reading', appendPoint);
});

function appendPoint(payload) {
  const ts = new Date(payload.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  labels.value.push(ts);
  dataPoints.value.push(payload.electric);
  // Keep last 50
  if (labels.value.length > 50) {
    labels.value.shift();
    dataPoints.value.shift();
  }
  chartKey.value++;
}

const chartData = computed(() => ({
  labels: labels.value,
  datasets: [
    {
      label: 'Power (W)',
      data: values.value,
      borderColor: '#42b983',
      backgroundColor: 'rgba(66, 184, 131, 0.2)',
      fill: true,
      tension: 0.3
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