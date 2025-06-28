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
  <section>
    <h2>ESG Reports</h2>
    <button @click="handleGenerate" :disabled="loading">Generate Report</button>
    <p v-if="error" style="color:red">{{ error }}</p>
    <ul>
      <li v-for="r in reports" :key="r.id">
        <a :href="r.url" target="_blank">Report {{ r.id }} - {{ new Date(r.created_at).toLocaleString() }}</a>
      </li>
      <li v-if="!reports.length">No reports yet.</li>
    </ul>
  </section>
</template>

<style scoped>
button {
  margin: 0.5rem 0;
}
</style> 