import { render, screen } from '@testing-library/vue';
import userEvent from '@testing-library/user-event';
import NavBar from '../src/components/NavBar.vue';
import { createRouter, createWebHistory } from 'vue-router';
import Home from '../src/views/Home.vue';
import Reports from '../src/views/Reports.vue';
import { describe, it, expect } from 'vitest';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Home },
    { path: '/reports', component: Reports }
  ]
});

describe('NavBar', () => {
  it('renders navigation links', async () => {
    render(NavBar, { global: { plugins: [router] } });
    expect(screen.getByRole('link', { name: /dashboard/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /reports/i })).toBeInTheDocument();
  });

  it('navigates to reports page on click', async () => {
    render(NavBar, { global: { plugins: [router] } });
    const reportsLink = screen.getByRole('link', { name: /reports/i });
    await userEvent.click(reportsLink);
    expect(router.currentRoute.value.path).toBe('/reports');
  });
}); 