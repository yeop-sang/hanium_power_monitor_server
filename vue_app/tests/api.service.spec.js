import { beforeEach, describe, it, expect, vi } from 'vitest';

// Mock axios at the top level with proper instance creation
const mockAxiosInstance = {
  get: vi.fn(),
  post: vi.fn()
};

vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => mockAxiosInstance)
  }
}));

describe('API Service', () => {
  let apiModule;

  beforeEach(async () => {
    vi.clearAllMocks();
    
    // Clear any existing cache
    apiModule = await import('../src/services/api.js');
    apiModule.clearCache();
  });

  describe('getPowerData', () => {
    it('fetches power data successfully', async () => {
      const mockData = [
        {
          id: 1,
          timestamp: '2024-01-01T12:00:00Z',
          temperature: 23.5,
          humidity: 65.2,
          brightness: 1200,
          electric: 150.5
        }
      ];
      
      mockAxiosInstance.get.mockResolvedValue({ data: mockData });
      
      const result = await apiModule.getPowerData({ limit: 10 });
      
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/power_data', { 
        params: { limit: 10 } 
      });
      expect(result.data).toEqual(mockData);
      expect(result.fromCache).toBe(false);
    });

    it('handles API errors gracefully', async () => {
      const mockError = {
        response: {
          status: 500,
          data: { message: 'Internal server error' }
        }
      };
      
      mockAxiosInstance.get.mockRejectedValue(mockError);
      
      await expect(apiModule.getPowerData()).rejects.toEqual({
        type: 'server_error',
        status: 500,
        message: 'Internal server error',
        data: { message: 'Internal server error' }
      });
    });

    it('handles network errors', async () => {
      const mockError = { request: {} };
      mockAxiosInstance.get.mockRejectedValue(mockError);
      
      await expect(apiModule.getPowerData()).rejects.toEqual({
        type: 'network_error',
        message: '네트워크 연결을 확인해주세요.',
        details: undefined
      });
    });

    it('validates data format', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: 'invalid data' });
      
      await expect(apiModule.getPowerData()).rejects.toEqual(
        expect.objectContaining({
          type: 'unknown_error',
          message: '알 수 없는 오류가 발생했습니다.'
        })
      );
    });
  });

  describe('getSummary', () => {
    it('fetches summary data with default time range', async () => {
      const mockSummary = {
        time_range: '24h',
        total_readings: 100,
        temperature: { avg: 23.5, min: 20.0, max: 27.0 }
      };
      
      mockAxiosInstance.get.mockResolvedValue({ data: mockSummary });
      
      const result = await apiModule.getSummary();
      
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/summary', { 
        params: { timeRange: '24h' } 
      });
      expect(result.data).toEqual(mockSummary);
    });

    it('accepts custom time range', async () => {
      const mockSummary = { time_range: '7d' };
      mockAxiosInstance.get.mockResolvedValue({ data: mockSummary });
      
      await apiModule.getSummary('7d');
      
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/summary', { 
        params: { timeRange: '7d' } 
      });
    });
  });

  describe('getLatestEnvironmentalData', () => {
    it('extracts environmental data from power data', async () => {
      const mockPowerData = [{
        temperature: 23.5,
        humidity: 65.2,
        brightness: 1200,
        timestamp: '2024-01-01T12:00:00Z'
      }];
      
      // Mock the getPowerData function response
      mockAxiosInstance.get.mockResolvedValue({ data: mockPowerData });
      
      const result = await apiModule.getLatestEnvironmentalData();
      
      expect(result.data).toEqual({
        temperature: 23.5,
        humidity: 65.2,
        brightness: 1200,
        timestamp: '2024-01-01T12:00:00Z'
      });
    });

    it('handles no data available', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: [] });
      
      await expect(apiModule.getLatestEnvironmentalData()).rejects.toEqual(
        expect.objectContaining({
          type: 'unknown_error',
          message: '알 수 없는 오류가 발생했습니다.',
          details: 'No environmental data available'
        })
      );
    });
  });

  describe('getLatestPowerData', () => {
    it('extracts power data', async () => {
      const mockPowerData = [{
        electric: 150.5,
        timestamp: '2024-01-01T12:00:00Z'
      }];
      
      mockAxiosInstance.get.mockResolvedValue({ data: mockPowerData });
      
      const result = await apiModule.getLatestPowerData();
      
      expect(result.data).toEqual({
        electric: 150.5,
        timestamp: '2024-01-01T12:00:00Z'
      });
    });
  });

  describe('cache management', () => {
    it('clears cache correctly', async () => {
      const mockData = [{ id: 1 }];
      mockAxiosInstance.get.mockResolvedValue({ data: mockData });
      
      // Fill cache
      await apiModule.getPowerData();
      
      // Clear cache
      apiModule.clearCache();
      
      // Next call should fetch from API
      const result = await apiModule.getPowerData();
      expect(result.fromCache).toBe(false);
      expect(mockAxiosInstance.get).toHaveBeenCalledTimes(2);
    });
  });

  describe('loading state', () => {
    it('tracks loading state correctly', () => {
      expect(apiModule.isLoading('power_data')).toBe(false);
      
      // Loading state is managed internally during API calls
      // This would be tested through integration tests
    });
  });
}); 