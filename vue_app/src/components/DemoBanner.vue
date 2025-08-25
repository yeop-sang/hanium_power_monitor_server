<template>
  <div class="demo-banner" :class="{ 'demo-banner--minimized': isMinimized }">
    <div class="demo-banner__content">
      <div class="demo-banner__icon">
        🚧
      </div>
      <div class="demo-banner__text">
        <strong>데모 모드로 실행 중</strong>
        <span v-if="!isMinimized"> - 실제 센서 데이터 대신 시뮬레이션 데이터를 사용합니다</span>
      </div>
      <button 
        class="demo-banner__toggle"
        @click="toggleMinimize"
        :title="isMinimized ? '배너 확장' : '배너 최소화'"
      >
        {{ isMinimized ? '▼' : '▲' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const isMinimized = ref(false);

const toggleMinimize = () => {
  isMinimized.value = !isMinimized.value;
};
</script>

<style scoped>
.demo-banner {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 12px 20px;
  position: sticky;
  top: 0;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.demo-banner--minimized {
  padding: 6px 20px;
}

.demo-banner__content {
  display: flex;
  align-items: center;
  justify-content: center;
  max-width: 1200px;
  margin: 0 auto;
  gap: 12px;
}

.demo-banner__icon {
  font-size: 20px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.demo-banner__text {
  flex: 1;
  text-align: center;
  font-size: 14px;
  line-height: 1.4;
}

.demo-banner__text strong {
  font-weight: 600;
  margin-right: 8px;
}

.demo-banner__toggle {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: background 0.2s ease;
}

.demo-banner__toggle:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .demo-banner {
    padding: 10px 16px;
  }
  
  .demo-banner--minimized {
    padding: 5px 16px;
  }
  
  .demo-banner__content {
    gap: 8px;
  }
  
  .demo-banner__text {
    font-size: 13px;
  }
  
  .demo-banner__icon {
    font-size: 18px;
  }
}
</style>
