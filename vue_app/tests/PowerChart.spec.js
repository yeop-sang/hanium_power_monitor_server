import { render } from '@testing-library/vue';
import { describe, it, expect, vi } from 'vitest';
vi.mock('chart.js', () => ({
  Chart: { register: () => {} },
  Title: {},
  Tooltip: {},
  Legend: {},
  LineElement: {},
  CategoryScale: {},
  LinearScale: {},
  PointElement: {},
  registerables: []
}));
vi.mock('vue-chartjs', () => ({
  Line: { name: 'Line', template: '<canvas />' }
}));
import PowerChart from '../src/components/PowerChart.vue';

describe('PowerChart', () => {
  it('renders canvas element', () => {
    const { container } = render(PowerChart);
    const canvas = container.querySelector('canvas');
    expect(canvas).toBeTruthy();
  });
}); 