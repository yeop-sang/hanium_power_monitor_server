import axios from 'axios';

// API 클라이언트 설정
const apiClient = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
});

// 데이터 캐시
const cache = new Map();
const CACHE_TTL = 30000; // 30초

// 로딩 상태 관리
const loadingStates = new Map();

// 에러 핸들링 유틸리티
function handleApiError(error, context = 'API') {
  console.error(`${context} Error:`, error);
  
  if (error.response) {
    // 서버 응답 에러 (4xx, 5xx)
    const { status, data } = error.response;
    return {
      type: 'server_error',
      status,
      message: data.message || `서버 에러 (${status})`,
      data: data
    };
  } else if (error.request) {
    // 네트워크 에러
    return {
      type: 'network_error',
      message: '네트워크 연결을 확인해주세요.',
      details: error.message
    };
  } else {
    // 기타 에러
    return {
      type: 'unknown_error',
      message: '알 수 없는 오류가 발생했습니다.',
      details: error.message
    };
  }
}

// 캐시 유틸리티
function getCacheKey(endpoint, params = {}) {
  return `${endpoint}_${JSON.stringify(params)}`;
}

function getFromCache(key) {
  const cached = cache.get(key);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data;
  }
  cache.delete(key);
  return null;
}

function setToCache(key, data) {
  cache.set(key, {
    data,
    timestamp: Date.now()
  });
}

// 로딩 상태 관리
function setLoading(key, state) {
  loadingStates.set(key, state);
}

function getLoading(key) {
  return loadingStates.get(key) || false;
}

// API 함수들
export async function getPowerData(params = {}) {
  const cacheKey = getCacheKey('power_data', params);
  const cached = getFromCache(cacheKey);
  
  if (cached) {
    return { data: cached, fromCache: true };
  }

  setLoading('power_data', true);
  
  try {
    const response = await apiClient.get('/power_data', { params });
    const data = response.data;
    
    // 데이터 유효성 검증
    if (Array.isArray(data)) {
      setToCache(cacheKey, data);
      return { data, fromCache: false };
    } else {
      throw new Error('Invalid data format received');
    }
  } catch (error) {
    throw handleApiError(error, 'Power Data API');
  } finally {
    setLoading('power_data', false);
  }
}

export async function getSummary(timeRange = '24h') {
  const cacheKey = getCacheKey('summary', { timeRange });
  const cached = getFromCache(cacheKey);
  
  if (cached) {
    return { data: cached, fromCache: true };
  }

  setLoading('summary', true);
  
  try {
    const response = await apiClient.get('/summary', { 
      params: { timeRange } 
    });
    const data = response.data;
    setToCache(cacheKey, data);
    return { data, fromCache: false };
  } catch (error) {
    throw handleApiError(error, 'Summary API');
  } finally {
    setLoading('summary', false);
  }
}

export async function getESGReports() {
  const cacheKey = getCacheKey('esg_reports');
  const cached = getFromCache(cacheKey);
  
  if (cached) {
    return { data: cached, fromCache: true };
  }

  setLoading('esg_reports', true);
  
  try {
    const response = await apiClient.get('/esg_reports');
    const data = response.data;
    setToCache(cacheKey, data);
    return { data, fromCache: false };
  } catch (error) {
    throw handleApiError(error, 'ESG Reports API');
  } finally {
    setLoading('esg_reports', false);
  }
}

export async function generateESGReport() {
  setLoading('generate_esg', true);
  
  try {
    const response = await apiClient.post('/generate_esg_report');
    
    // ESG 보고서 생성 후 캐시 무효화
    cache.clear();
    
    return { data: response.data };
  } catch (error) {
    throw handleApiError(error, 'Generate ESG Report API');
  } finally {
    setLoading('generate_esg', false);
  }
}

// 환경 데이터 전용 함수 (최적화된 캐싱)
export async function getLatestEnvironmentalData() {
  const cacheKey = 'latest_env_data';
  const cached = getFromCache(cacheKey);
  
  if (cached) {
    return { data: cached, fromCache: true };
  }
  
  try {
    const response = await getPowerData({ limit: 1 });
    if (response.data && response.data.length > 0) {
      const envData = {
        temperature: response.data[0].temperature,
        humidity: response.data[0].humidity,
        brightness: response.data[0].brightness,
        timestamp: response.data[0].timestamp
      };
      setToCache(cacheKey, envData);
      return { data: envData, fromCache: false };
    }
    throw new Error('No environmental data available');
  } catch (error) {
    throw handleApiError(error, 'Environmental Data API');
  }
}

// 현재 전력 데이터 전용 함수
export async function getLatestPowerData() {
  const cacheKey = 'latest_power_data';
  const cached = getFromCache(cacheKey);
  
  if (cached) {
    return { data: cached, fromCache: true };
  }
  
  try {
    const response = await getPowerData({ limit: 1 });
    if (response.data && response.data.length > 0) {
      const powerData = {
        electric: response.data[0].electric,
        timestamp: response.data[0].timestamp
      };
      setToCache(cacheKey, powerData);
      return { data: powerData, fromCache: false };
    }
    throw new Error('No power data available');
  } catch (error) {
    throw handleApiError(error, 'Latest Power Data API');
  }
}

// 트렌드 데이터 함수
export async function getTrendData(timeRange = '24h') {
  const cacheKey = getCacheKey('trend', { timeRange });
  const cached = getFromCache(cacheKey);
  
  if (cached) {
    return { data: cached, fromCache: true };
  }

  setLoading('trend', true);
  
  try {
    const response = await apiClient.get('/trend', { 
      params: { timeRange } 
    });
    const data = response.data;
    setToCache(cacheKey, data);
    return { data, fromCache: false };
  } catch (error) {
    throw handleApiError(error, 'Trend API');
  } finally {
    setLoading('trend', false);
  }
}

// 캐시 관리 함수들
export function clearCache() {
  cache.clear();
}

export function clearCacheByPattern(pattern) {
  for (const key of cache.keys()) {
    if (key.includes(pattern)) {
      cache.delete(key);
    }
  }
}

// 로딩 상태 확인 함수들
export function isLoading(key) {
  return getLoading(key);
}

export function getAllLoadingStates() {
  return Object.fromEntries(loadingStates);
}

// 기본 export
export default {
  getPowerData,
  getSummary,
  getESGReports,
  generateESGReport,
  getLatestEnvironmentalData,
  getLatestPowerData,
  getTrendData,
  clearCache,
  clearCacheByPattern,
  isLoading,
  getAllLoadingStates
}; 