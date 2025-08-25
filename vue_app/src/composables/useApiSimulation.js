import { ref } from 'vue';

// API 호출 관리를 위한 composable
export function useApiSimulation() {
  const isLoading = ref(false);
  const error = ref(null);

  // API 호출 딜레이 시뮬레이션 (500ms ~ 2초)
  const simulateApiDelay = (minMs = 500, maxMs = 2000) => {
    const delay = Math.floor(Math.random() * (maxMs - minMs + 1)) + minMs;
    return new Promise(resolve => setTimeout(resolve, delay));
  };

  // 성공/실패 시뮬레이션 (95% 성공률)
  const simulateApiCall = async (successCallback, errorRate = 0.05) => {
    isLoading.value = true;
    error.value = null;

    try {
      await simulateApiDelay();
      
      // 에러 시뮬레이션
      if (Math.random() < errorRate) {
        throw new Error('네트워크 연결이 불안정합니다. 다시 시도해주세요.');
      }

      const result = await successCallback();
      return result;
    } catch (err) {
      error.value = err.message;
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  // 실시간 데이터 업데이트 시뮬레이션
  const simulateRealTimeUpdates = (callback, intervalMs = 3000) => {
    const interval = setInterval(() => {
      callback();
    }, intervalMs);

    return () => clearInterval(interval);
  };

  // PDF 다운로드 시뮬레이션
  const simulatePdfDownload = async (filename = 'ESG_Report.pdf') => {
    return simulateApiCall(async () => {
      // 실제 다운로드 대신 성공 메시지만 반환
      return {
        success: true,
        message: `${filename} 다운로드가 완료되었습니다.`,
        filename
      };
    });
  };

  // 차트 데이터 로딩 시뮬레이션
  const simulateChartDataLoad = async (dataGenerator) => {
    return simulateApiCall(async () => {
      return dataGenerator();
    });
  };

  // 알림 발송 시뮬레이션
  const simulateNotificationSend = async (notification) => {
    return simulateApiCall(async () => {
      return {
        success: true,
        message: '알림이 성공적으로 전송되었습니다.',
        notification
      };
    });
  };

  // 로딩 상태 수동 제어
  const setLoading = (loading) => {
    isLoading.value = loading;
  };

  const setError = (errorMessage) => {
    error.value = errorMessage;
  };

  const clearError = () => {
    error.value = null;
  };

  return {
    isLoading,
    error,
    simulateApiDelay,
    simulateApiCall,
    simulateRealTimeUpdates,
    simulatePdfDownload,
    simulateChartDataLoad,
    simulateNotificationSend,
    setLoading,
    setError,
    clearError
  };
}
