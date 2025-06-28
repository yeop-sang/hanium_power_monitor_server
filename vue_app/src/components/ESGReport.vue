<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api.js';

const reports = ref([]);
const loading = ref(false);
const error = ref(null);

async function fetchReports() {
  try {
    const { data } = await api.getESGReports();
    reports.value = data;
  } catch (e) {
    error.value = 'Failed to load reports';
  }
}

async function handleGenerate() {
  loading.value = true;
  try {
    await api.generateESGReport();
    await fetchReports();
  } catch (e) {
    error.value = 'Failed to generate report';
  } finally {
    loading.value = false;
  }
}

onMounted(fetchReports);
</script>

<template>
  <div class="card">
    <h3>ESG Report</h3>
    <button @click="handleGenerate" :disabled="loading" class="btn">
      {{ loading ? 'Generating...' : 'Generate New Report' }}
    </button>
    <p v-if="error" style="color:red">{{ error }}</p>
    <div v-if="reports.length">
      <h4>Generated Reports:</h4>
      <table class="styled-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>URL</th>
            <th>Created At</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in reports" :key="r.id">
            <td>{{ r.id }}</td>
            <td><a :href="r.url" target="_blank">{{ r.url }}</a></td>
            <td>{{ new Date(r.created_at).toLocaleString() }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-if="!reports.length">No reports yet.</p>
  </div>
</template>

<style scoped>
.card {
  padding: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.btn {
  margin: 0.5rem 0;
}

.styled-table {
  width: 100%;
  border-collapse: collapse;
}

.styled-table th,
.styled-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.styled-table th {
  background-color: #f8f9fa;
}

.styled-table tbody tr:hover {
  background-color: #f8f9fa;
}
</style> 