// tests/ESGReport.spec.js
import { render, screen } from '@testing-library/vue'
import { describe, it, expect, vi } from 'vitest'
import userEvent from '@testing-library/user-event'

// Mock API service with default export
const mockApi = {
  getESGReports: vi.fn(),
  generateESGReport: vi.fn()
};

vi.mock('../src/services/api.js', () => ({
  default: mockApi,
  ...mockApi
}));

describe('ESGReport', () => {
  it('calls generateESGReport on button click', async () => {
    mockApi.generateESGReport.mockResolvedValue({ data: { id: 1, url: '/report.csv' } });
    mockApi.getESGReports.mockResolvedValue({ data: [] });
    
    const ESGReport = await import('../src/components/ESGReport.vue');
    render(ESGReport.default);
    
    // Use the actual button text from the component
    const btn = screen.getByRole('button', { name: /generate new report/i });
    await userEvent.click(btn);
    
    expect(mockApi.generateESGReport).toHaveBeenCalled();
  });
})