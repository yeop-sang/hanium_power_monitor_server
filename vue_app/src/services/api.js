import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
});

export function getESGReports() {
  return apiClient.get('/esg_reports'); // backend TBD
}

export function generateESGReport() {
  return apiClient.post('/generate_esg_report');
}

// Fetch power readings; optional query params: { limit, timeRange, fields }
export function getPowerData(params = {}) {
  return apiClient.get('/power_data', { params });
}

export default {
  getESGReports,
  generateESGReport,
  getPowerData
}; 