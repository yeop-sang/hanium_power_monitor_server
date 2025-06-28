<script setup>
import NavBar from './components/NavBar.vue';
</script>

<template>
  <NavBar />
  <main class="p-4">
    <router-view />
  </main>
</template>

<style scoped>
main {
  max-width: 1280px;
  margin: 0 auto;
}
</style>
