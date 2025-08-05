import { render, screen, waitFor } from '@testing-library/vue';
import { beforeEach, describe, it, expect, vi } from 'vitest';

// Mock API service - must be at top level
vi.mock('../src/services/api.js', () => ({
  getLatestEnvironmentalData: vi.fn(),
  isLoading: vi.fn()
}));

// Mock Socket service - must be at top level  
vi.mock('../src/services/socket.js', () => ({
  isConnected: { value: true },
  isConnecting: { value: false },
  hasError: { value: false },
  safeOn: vi.fn(),
  validateReadingData: vi.fn()
}));

describe('EnvironmentalData', () => {
  let mockGetLatestEnvironmentalData;
  let mockIsLoading;
  let mockSafeOn;
  let mockValidateReadingData;
  let mockIsConnected;
  let mockIsConnecting;
  let mockSocketHasError;

  beforeEach(async () => {
    vi.clearAllMocks();
    
    // Get the mocked functions
    const apiModule = await import('../src/services/api.js');
    const socketModule = await import('../src/services/socket.js');
    
    mockGetLatestEnvironmentalData = apiModule.getLatestEnvironmentalData;
    mockIsLoading = apiModule.isLoading;
    mockSafeOn = socketModule.safeOn;
    mockValidateReadingData = socketModule.validateReadingData;
    mockIsConnected = socketModule.isConnected;
    mockIsConnecting = socketModule.isConnecting;
    mockSocketHasError = socketModule.hasError;
    
    // Set default mock behavior
    mockIsLoading.mockReturnValue(false);
    mockGetLatestEnvironmentalData.mockResolvedValue({
      data: {
        temperature: 23.5,
        humidity: 65.2,
        brightness: 1200,
        timestamp: '2024-01-01T12:00:00Z'
      }
    });
    mockValidateReadingData.mockReturnValue(true);
    mockSafeOn.mockReturnValue(() => {});
    
    // Reset socket state to defaults
    mockIsConnected.value = true;
    mockIsConnecting.value = false;
    mockSocketHasError.value = false;
  });

  it('renders environmental data with correct units', async () => {
    const EnvironmentalData = await import('../src/components/EnvironmentalData.vue');
    render(EnvironmentalData.default);
    
    expect(screen.getByText('Environmental Data')).toBeInTheDocument();
    expect(screen.getByText('Temperature')).toBeInTheDocument();
    expect(screen.getByText('Humidity')).toBeInTheDocument();
    expect(screen.getByText('Brightness')).toBeInTheDocument();
  });

  it('shows connection status indicator', async () => {
    const EnvironmentalData = await import('../src/components/EnvironmentalData.vue');
    render(EnvironmentalData.default);
    
    expect(screen.getByText('실시간 연결됨')).toBeInTheDocument();
  });

  it('displays connecting status when connecting', async () => {
    mockIsConnected.value = false;
    mockIsConnecting.value = true;
    mockSocketHasError.value = false;
    
    const EnvironmentalData = await import('../src/components/EnvironmentalData.vue');
    render(EnvironmentalData.default);
    
    expect(screen.getByText('연결 중...')).toBeInTheDocument();
  });

  it('displays error status when connection has error', async () => {
    mockIsConnected.value = false;
    mockIsConnecting.value = false;
    mockSocketHasError.value = true;
    
    const EnvironmentalData = await import('../src/components/EnvironmentalData.vue');
    render(EnvironmentalData.default);
    
    expect(screen.getByText('연결 오류')).toBeInTheDocument();
  });

  it('displays loading state', async () => {
    mockIsLoading.mockReturnValue(true);
    
    const EnvironmentalData = await import('../src/components/EnvironmentalData.vue');
    render(EnvironmentalData.default);
    
    expect(screen.getAllByText('로딩 중...')).toHaveLength(3);
  });

  it('handles API errors gracefully', async () => {
    const mockError = {
      message: 'Network error occurred',
      type: 'network_error'
    };
    mockGetLatestEnvironmentalData.mockRejectedValue(mockError);
    
    const EnvironmentalData = await import('../src/components/EnvironmentalData.vue');
    render(EnvironmentalData.default);
    
    await waitFor(() => {
      expect(screen.getByText('Network error occurred')).toBeInTheDocument();
    });
  });

  it('displays default values when no data available', async () => {
    mockGetLatestEnvironmentalData.mockResolvedValue({ data: null });
    
    const EnvironmentalData = await import('../src/components/EnvironmentalData.vue');
    render(EnvironmentalData.default);
    
    // Should show default values with units
    expect(screen.getByText('-- °C')).toBeInTheDocument();
    expect(screen.getByText('-- %')).toBeInTheDocument();
    expect(screen.getByText('-- lx')).toBeInTheDocument();
  });

  it('registers socket event listener on mount', async () => {
    const EnvironmentalData = await import('../src/components/EnvironmentalData.vue');
    render(EnvironmentalData.default);
    
    expect(mockSafeOn).toHaveBeenCalledWith('reading', expect.any(Function));
  });

  it('validates socket data before using it', async () => {
    const EnvironmentalData = await import('../src/components/EnvironmentalData.vue');
    render(EnvironmentalData.default);
    
    // Get the socket callback function
    const socketCallback = mockSafeOn.mock.calls[0][1];
    
    // Mock valid data
    const validData = {
      temperature: 25.0,
      humidity: 70.0,
      brightness: 1500,
      timestamp: '2024-01-01T13:00:00Z'
    };
    
    mockValidateReadingData.mockReturnValue(true);
    
    // Simulate socket data
    socketCallback(validData);
    
    expect(mockValidateReadingData).toHaveBeenCalledWith(validData);
  });

  it('handles invalid socket data gracefully', async () => {
    const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
    
    const EnvironmentalData = await import('../src/components/EnvironmentalData.vue');
    render(EnvironmentalData.default);
    
    const socketCallback = mockSafeOn.mock.calls[0][1];
    const invalidData = { invalid: 'data' };
    
    mockValidateReadingData.mockReturnValue(false);
    
    socketCallback(invalidData);
    
    expect(consoleSpy).toHaveBeenCalledWith('Invalid socket data received:', invalidData);
    
    consoleSpy.mockRestore();
  });

  it('updates last updated timestamp', async () => {
    const EnvironmentalData = await import('../src/components/EnvironmentalData.vue');
    render(EnvironmentalData.default);
    
    await waitFor(() => {
      expect(screen.getByText(/마지막 업데이트:/)).toBeInTheDocument();
    });
  });

  it('is responsive on mobile devices', async () => {
    const EnvironmentalData = await import('../src/components/EnvironmentalData.vue');
    const { container } = render(EnvironmentalData.default);
    
    // Check if responsive CSS classes exist
    expect(container.querySelector('.env-grid')).toBeInTheDocument();
    expect(container.querySelector('.env-header')).toBeInTheDocument();
  });
}); 