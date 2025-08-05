import { io } from 'socket.io-client';
import { ref, computed } from 'vue';

// 연결 상태 관리
const connectionStatus = ref('disconnected'); // 'connected', 'connecting', 'disconnected', 'error'
const lastError = ref(null);
const reconnectAttempts = ref(0);
const lastDataReceived = ref(null);

// 서버 상태 정보
const serverStatus = ref({
  mqtt_connected: false,
  db_available: false,
  server_time: null,
  client_id: null
});

// Socket 인스턴스 생성
const socket = io('/', {
  path: '/socket.io',
  transports: ['websocket', 'polling'],
  timeout: 10000,
  reconnection: true,
  reconnectionAttempts: 5,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 5000,
  maxReconnectionAttempts: 5
});

// 연결 이벤트 핸들러
socket.on('connect', () => {
  console.log('Socket connected:', socket.id);
  connectionStatus.value = 'connected';
  lastError.value = null;
  reconnectAttempts.value = 0;
});

socket.on('disconnect', (reason) => {
  console.log('Socket disconnected:', reason);
  connectionStatus.value = 'disconnected';
  
  if (reason === 'io server disconnect') {
    // 서버에서 연결을 끊은 경우, 수동으로 재연결 시도
    socket.connect();
  }
});

socket.on('connect_error', (error) => {
  console.error('Socket connection error:', error);
  connectionStatus.value = 'error';
  lastError.value = {
    message: error.message,
    timestamp: new Date().toISOString(),
    type: 'connection_error'
  };
});

socket.on('reconnect', (attemptNumber) => {
  console.log('Socket reconnected after', attemptNumber, 'attempts');
  connectionStatus.value = 'connected';
  reconnectAttempts.value = attemptNumber;
});

socket.on('reconnect_attempt', (attemptNumber) => {
  console.log('Socket reconnection attempt:', attemptNumber);
  connectionStatus.value = 'connecting';
  reconnectAttempts.value = attemptNumber;
});

socket.on('reconnect_error', (error) => {
  console.error('Socket reconnection error:', error);
  lastError.value = {
    message: error.message,
    timestamp: new Date().toISOString(),
    type: 'reconnection_error'
  };
});

socket.on('reconnect_failed', () => {
  console.error('Socket reconnection failed');
  connectionStatus.value = 'error';
  lastError.value = {
    message: '재연결에 실패했습니다. 네트워크 연결을 확인해주세요.',
    timestamp: new Date().toISOString(),
    type: 'reconnection_failed'
  };
});

// 데이터 수신 이벤트 (모든 데이터 수신을 추적)
socket.on('reading', (data) => {
  lastDataReceived.value = {
    data,
    timestamp: new Date().toISOString()
  };
  console.log('Real-time data received:', data);
});

// 에러 핸들링
socket.on('error', (error) => {
  console.error('Socket error:', error);
  lastError.value = {
    message: error.message || 'Socket 에러가 발생했습니다.',
    timestamp: new Date().toISOString(),
    type: 'socket_error'
  };
});

// 서버 이벤트 리스너들 추가
socket.on('connection_status', (data) => {
  console.log('Connection status received:', data);
  serverStatus.value = {
    mqtt_connected: data.mqtt_connected,
    db_available: data.db_available,
    server_time: data.server_time,
    client_id: data.client_id
  };
  connectionStatus.value = 'connected';
});

socket.on('latest_data', (data) => {
  console.log('Latest data received from server:', data);
  lastDataReceived.value = {
    data,
    timestamp: new Date().toISOString(),
    source: 'server_request'
  };
});

socket.on('pong', (data) => {
  console.log('Pong received:', data);
});

socket.on('room_joined', (data) => {
  console.log('Joined room:', data.room);
});

socket.on('room_left', (data) => {
  console.log('Left room:', data.room);
});

socket.on('error', (error) => {
  console.error('Server error received:', error);
  lastError.value = {
    message: error.message || 'Server error occurred',
    timestamp: new Date().toISOString(),
    type: error.type || 'server_error',
    details: error
  };
});

// 연결 상태 computed properties
const isConnected = computed(() => connectionStatus.value === 'connected');
const isConnecting = computed(() => connectionStatus.value === 'connecting');
const hasError = computed(() => connectionStatus.value === 'error');

// 수동 연결/해제 함수들
function connect() {
  if (socket.disconnected) {
    connectionStatus.value = 'connecting';
    socket.connect();
  }
}

function disconnect() {
  if (socket.connected) {
    socket.disconnect();
  }
}

// 연결 상태 확인 함수
function checkConnection() {
  return {
    connected: socket.connected,
    id: socket.id,
    status: connectionStatus.value,
    error: lastError.value,
    reconnectAttempts: reconnectAttempts.value,
    lastDataReceived: lastDataReceived.value
  };
}

// 수동 재연결 함수
function forceReconnect() {
  console.log('Forcing socket reconnection...');
  disconnect();
  setTimeout(() => {
    connect();
  }, 1000);
}

// 이벤트 리스너 관리 함수들
function onReading(callback) {
  socket.on('reading', callback);
  return () => socket.off('reading', callback);
}

function onConnectionChange(callback) {
  const unsubscribers = [
    () => socket.off('connect', callback),
    () => socket.off('disconnect', callback),
    () => socket.off('connect_error', callback),
    () => socket.off('reconnect', callback)
  ];
  
  socket.on('connect', () => callback('connected'));
  socket.on('disconnect', () => callback('disconnected'));
  socket.on('connect_error', () => callback('error'));
  socket.on('reconnect', () => callback('connected'));
  
  return () => unsubscribers.forEach(unsub => unsub());
}

// 특정 이벤트에 대한 안전한 리스너 등록
function safeOn(event, callback) {
  const wrappedCallback = (data) => {
    try {
      callback(data);
    } catch (error) {
      console.error(`Error in ${event} callback:`, error);
      lastError.value = {
        message: `${event} 이벤트 처리 중 에러가 발생했습니다.`,
        timestamp: new Date().toISOString(),
        type: 'callback_error',
        details: error.message
      };
    }
  };
  
  socket.on(event, wrappedCallback);
  return () => socket.off(event, wrappedCallback);
}

// 데이터 검증 함수
function validateReadingData(data) {
  const requiredFields = ['timestamp', 'temperature', 'humidity', 'brightness', 'electric'];
  const missingFields = requiredFields.filter(field => !(field in data));
  
  if (missingFields.length > 0) {
    console.warn('Missing fields in reading data:', missingFields);
    return false;
  }
  
  // 숫자 데이터 검증
  const numericFields = ['temperature', 'humidity', 'brightness', 'electric'];
  for (const field of numericFields) {
    if (typeof data[field] !== 'number' && !isNaN(Number(data[field]))) {
      data[field] = Number(data[field]);
    }
  }
  
  return true;
}

// 서버로부터 최신 데이터 요청
function requestLatestData() {
  if (socket.connected) {
    console.log('Requesting latest data from server...');
    socket.emit('get_latest_data');
  }
}

// 핑 테스트 함수
function sendPing() {
  if (socket.connected) {
    socket.emit('ping');
  }
}

// 룸 관리 함수들
function joinRoom(roomName) {
  if (socket.connected) {
    socket.emit('join_room', { room: roomName });
  }
}

function leaveRoom(roomName) {
  if (socket.connected) {
    socket.emit('leave_room', { room: roomName });
  }
}

// 서버 상태 확인 함수
function getServerStatus() {
  return {
    ...serverStatus.value,
    socket_connected: socket.connected,
    socket_id: socket.id
  };
}

// 연결 품질 테스트 함수
function testConnectionQuality() {
  return new Promise((resolve) => {
    const startTime = Date.now();
    
    const onPong = (data) => {
      const endTime = Date.now();
      const latency = endTime - startTime;
      
      socket.off('pong', onPong);
      resolve({
        latency,
        server_time: data.timestamp,
        client_id: data.client_id,
        quality: latency < 100 ? 'excellent' : latency < 300 ? 'good' : latency < 1000 ? 'fair' : 'poor'
      });
    };
    
    socket.on('pong', onPong);
    sendPing();
    
    // 타임아웃 처리
    setTimeout(() => {
      socket.off('pong', onPong);
      resolve({
        latency: -1,
        error: 'timeout',
        quality: 'timeout'
      });
    }, 5000);
  });
}

// Export 기본 socket과 유틸리티 함수들
export default socket;

export {
  connectionStatus,
  isConnected,
  isConnecting,
  hasError,
  lastError,
  reconnectAttempts,
  lastDataReceived,
  connect,
  disconnect,
  checkConnection,
  forceReconnect,
  onReading,
  onConnectionChange,
  safeOn,
  validateReadingData,
  requestLatestData,
  sendPing,
  joinRoom,
  leaveRoom,
  getServerStatus,
  testConnectionQuality
}; 