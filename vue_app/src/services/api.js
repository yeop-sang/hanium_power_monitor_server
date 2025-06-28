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

export default {
  getESGReports,
  generateESGReport
}; 