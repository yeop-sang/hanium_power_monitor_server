<script setup>
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  Chart,
  Title,
  Tooltip,
  Legend,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement
} from 'chart.js';
import { computed, onMounted, onUnmounted } from 'vue';
import { useMockData } from '../composables/useMockData.js';
import { useApiSimulation } from '../composables/useApiSimulation.js';

ChartJS.register(Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale, PointElement);

const { dashboardData, generateInitialPowerHistory, updateDashboardData } = useMockData();
const { simulateRealTimeUpdates } = useApiSimulation();

let updateInterval = null;

onMounted(() => {
  // 초기 히스토리 데이터 생성
  generateInitialPowerHistory();
  
  // 30초마다 새 데이터 포인트 추가
  updateInterval = simulateRealTimeUpdates(() => {
    updateDashboardData();
  }, 30000);
});

onUnmounted(() => {
  if (updateInterval) {
    updateInterval();
  }
});

const chartData = computed(() => ({
  labels: dashboardData.powerHistory.map(item => 
    item.timestamp.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
  ),
  datasets: [
    {
      label: 'Power (W)',
      data: dashboardData.powerHistory.map(item => item.value),
      borderColor: '#42b983',
      backgroundColor: 'rgba(66, 184, 131, 0.2)',
      fill: true,
      tension: 0.3,
      pointBackgroundColor: dashboardData.powerHistory.map(item => 
        item.isOutlier ? '#ff4757' : '#42b983'
      ),
      pointBorderColor: dashboardData.powerHistory.map(item => 
        item.isOutlier ? '#ff3742' : '#2d8659'
      ),
      pointRadius: dashboardData.powerHistory.map(item => 
        item.isOutlier ? 6 : 3
      ),
      pointHoverRadius: dashboardData.powerHistory.map(item => 
        item.isOutlier ? 8 : 5
      )
    }
  ]
}));

const chartOptions = { 
  responsive: true, 
  maintainAspectRatio: false,
  scales: {
    y: {
      beginAtZero: false,
      title: {
        display: true,
        text: 'Power (W)'
      }
    },
    x: {
      title: {
        display: true,
        text: 'Time'
      }
    }
  },
  plugins: {
    tooltip: {
      callbacks: {
        afterLabel: function(context) {
          const dataIndex = context.dataIndex;
          const isOutlier = dashboardData.powerHistory[dataIndex]?.isOutlier;
          return isOutlier ? '⚠️ Outlier 감지됨' : '';
        }
      }
    },
    legend: {
      labels: {
        generateLabels: function(chart) {
          const original = Chart.defaults.plugins.legend.labels.generateLabels;
          const labels = original.call(this, chart);
          
          // outlier 범례 추가
          labels.push({
            text: '⚠️ Outlier',
            fillStyle: '#ff4757',
            strokeStyle: '#ff3742',
            pointStyle: 'circle'
          });
          
          return labels;
        }
      }
    }
  }
};
</script>

<template>
  <div style="height:300px">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>