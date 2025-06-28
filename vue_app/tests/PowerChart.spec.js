import { render } from '@testing-library/vue';
import { describe, it, expect, vi } from 'vitest';
vi.mock('chart.js', () => ({
  Chart: { register: () => {} },
  registerables: []
}));
vi.mock('vue-chart-3', () => ({
  LineChart: { name: 'LineChart', template: '<canvas />' }
}));
import PowerChart from '../src/components/PowerChart.vue';

describe('PowerChart', () => {
  it('renders canvas element', () => {
    const { container } = render(PowerChart);
    const canvas = container.querySelector('canvas');
    expect(canvas).toBeTruthy();
  });
}); 