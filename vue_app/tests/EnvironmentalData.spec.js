import { render, screen } from '@testing-library/vue';
import EnvironmentalData from '../src/components/EnvironmentalData.vue';
import { describe, it, expect } from 'vitest';

describe('EnvironmentalData', () => {
  it('shows default dummy data with units', () => {
    render(EnvironmentalData);
    expect(screen.getByText(/temperature/i)).toBeInTheDocument();
    expect(screen.getByText(/humidity/i)).toBeInTheDocument();
    expect(screen.getByText(/brightness/i)).toBeInTheDocument();
    expect(screen.getByText(/°C/)).toBeInTheDocument();
    expect(screen.getByText(/%/)).toBeInTheDocument();
    expect(screen.getByText(/lx/)).toBeInTheDocument();
  });
}); 