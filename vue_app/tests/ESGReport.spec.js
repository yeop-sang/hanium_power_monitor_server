// tests/ESGReport.spec.js
import { render, screen } from '@testing-library/vue'
import userEvent from '@testing-library/user-event'
import ESGReport from '../src/components/ESGReport.vue'
import { vi, describe, it, expect } from 'vitest'

// 1) 모듈을 먼저 mock
vi.mock('../src/services/api.js', () => {
  const mockApi = {
    getESGReports: vi.fn().mockResolvedValue({ data: [] }),
    generateESGReport: vi.fn().mockResolvedValue({})
  }
  // default·named export 모두 동일 객체로 반환
  return { default: mockApi, ...mockApi }
})

// 2) mock 정의 후 import 해야 spy 가 유지됨
import api from '../src/services/api.js'

describe('ESGReport', () => {
  it('calls generateESGReport on button click', async () => {
    render(ESGReport)
    const btn = screen.getByRole('button', { name: /generate report/i })
    await userEvent.click(btn)
    expect(api.generateESGReport).toHaveBeenCalled()
  })
})