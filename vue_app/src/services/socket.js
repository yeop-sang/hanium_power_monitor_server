import { io } from 'socket.io-client';

// Connect to same origin; nginx will proxy WebSocket automatically
const socket = io('/', {
  path: '/socket.io',
  transports: ['websocket', 'polling'],
});

export default socket; 