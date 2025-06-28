import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import Reports from '../views/Reports.vue';

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/reports', name: 'Reports', component: Reports }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router; 