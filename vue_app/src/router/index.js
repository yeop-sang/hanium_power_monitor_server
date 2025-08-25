import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import Reports from '../views/Reports.vue';
import EnergyAnalysis from '../views/EnergyAnalysis.vue';
import AnomalyDetection from '../views/AnomalyDetection.vue';
import ESGReport from '../views/ESGReport.vue';

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/reports', name: 'Reports', component: Reports },
  { path: '/energy-analysis', name: 'EnergyAnalysis', component: EnergyAnalysis },
  { path: '/anomaly-detection', name: 'AnomalyDetection', component: AnomalyDetection },
  { path: '/esg-report', name: 'ESGReport', component: ESGReport }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router; 