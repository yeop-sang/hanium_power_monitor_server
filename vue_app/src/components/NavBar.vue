<template>
  <nav class="navbar">
    <ul>
      <li><router-link to="/">Dashboard</router-link></li>
      <li><router-link to="/reports">Reports</router-link></li>
    </ul>
  </nav>
</template>

<style scoped>
.navbar {
  background-color: #34495e;
  padding: 1rem;
}

.navbar ul {
  list-style: none;
  display: flex;
  gap: 1rem;
  margin: 0;
  padding: 0;
}

.navbar a {
  color: #ecf0f1;
  text-decoration: none;
  font-weight: 600;
}

.navbar a.router-link-active {
  text-decoration: underline;
}
</style> 