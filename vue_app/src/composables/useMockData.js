import { ref, reactive } from 'vue';

// Data generators for energy monitoring system
export function useMockData() {
  // 전력 사용량 목업 데이터 (기기별)
  const energyMockData = reactive({
    daily: {
      pie: [
        { name: '냉장고', value: 45, color: '#4F46E5' },
        { name: '에어컨', value: 78, color: '#06B6D4' },
        { name: '조명', value: 12, color: '#10B981' },
        { name: '세탁기', value: 23, color: '#F59E0B' },
        { name: '컴퓨터', value: 34, color: '#EF4444' },
        { name: '기타', value: 18, color: '#8B5CF6' }
      ]
    },
    weekly: {
      bar: [
        { day: '월', value: 156, color: '#4F46E5' },
        { day: '화', value: 189, color: '#4F46E5' },
        { day: '수', value: 145, color: '#4F46E5' },
        { day: '목', value: 203, color: '#4F46E5' },
        { day: '금', value: 167, color: '#4F46E5' },
        { day: '토', value: 134, color: '#4F46E5' },
        { day: '일', value: 178, color: '#4F46E5' }
      ]
    },
    monthly: {
      bar: [
        { month: '3월', value: 4567, color: '#06B6D4' },
        { month: '4월', value: 4234, color: '#06B6D4' },
        { month: '5월', value: 3987, color: '#06B6D4' },
        { month: '6월', value: 4123, color: '#06B6D4' },
        { month: '7월', value: 4456, color: '#06B6D4' },
        { month: '8월', value: 4789, color: '#06B6D4' }
      ]
    }
  });

  // AI 패턴 추천 목업 데이터
  const aiRecommendations = ref([
    {
      id: 1,
      type: '절약 팁',
      message: '에어컨 설정온도를 1도 높이면 월 전기요금을 약 7% 절약할 수 있습니다.',
      priority: 'high',
      savings: '약 15,000원/월'
    },
    {
      id: 2,
      type: '사용 패턴',
      message: '오후 2-4시에 전력 사용량이 최고조에 달합니다. 이 시간대 사용량 조절을 권장합니다.',
      priority: 'medium',
      savings: '약 8,000원/월'
    },
    {
      id: 3,
      type: '기기 최적화',
      message: '냉장고의 24시간 평균 소비량이 표준보다 12% 높습니다. 문 개폐 횟수를 줄여보세요.',
      priority: 'low',
      savings: '약 3,500원/월'
    }
  ]);

  // 이상탐지 목업 데이터
  const anomalyTypes = [
    {
      type: 'current',
      messages: [
        '전류 과부하 감지 - 에어컨 #2',
        '전류 이상 급증 - 세탁기',
        '전류 불안정 - 냉장고',
        '전류 임계치 초과 - 전자레인지'
      ],
      color: '#EF4444',
      icon: '⚡'
    },
    {
      type: 'temperature',
      messages: [
        '온도 임계치 초과 - 침실',
        '온도 급상승 감지 - 보일러실',
        '온도 센서 이상 - 거실',
        '고온 경고 - 주방'
      ],
      color: '#F59E0B',
      icon: '🌡️'
    }
  ];

  // ESG 보고서 목업 데이터
  const esgReportData = reactive({
    months: ['3월', '4월', '5월', '6월', '7월', '8월'],
    currentMonth: '8월',
    basicInfo: {
      energyUsage: 118.4, // kWh
      carbonEmission: 51.2, // kgCO₂
      savings: 9500, // 원
      anomaliesDetected: 1
    },
    gradeInfo: {
      currentGrade: 'A+',
      score: 92,
      previousGrade: 'A0',
      previousScore: 87
    },
    comparison: {
      labels: ['7월', '8월'],
      current: [55.8, 51.2], // 7월 → 8월로 일관성 있는 감소
      reduction: 8.2 // 실제 계산된 감축률: (55.8-51.2)/55.8 * 100 = 8.2%
    },
    monthlyData: {
      '3월': { energyUsage: 148.5, carbonEmission: 75.2, savings: 5500, anomaliesDetected: 12, grade: 'C+', score: 58 },
      '4월': { energyUsage: 141.3, carbonEmission: 69.8, savings: 6200, anomaliesDetected: 9, grade: 'B-', score: 64 },
      '5월': { energyUsage: 133.7, carbonEmission: 63.4, savings: 7100, anomaliesDetected: 6, grade: 'B+', score: 72 },
      '6월': { energyUsage: 127.2, carbonEmission: 59.1, savings: 8000, anomaliesDetected: 4, grade: 'A-', score: 79 },
      '7월': { energyUsage: 122.8, carbonEmission: 55.8, savings: 8800, anomaliesDetected: 2, grade: 'A0', score: 87 },
      '8월': { energyUsage: 118.4, carbonEmission: 51.2, savings: 9500, anomaliesDetected: 1, grade: 'A+', score: 92 }
    },
    opinion: '8월은 전력 사용량이 7월 대비 3.6% 감소하고 탄소 배출량도 8.2% 줄어들어 A+ 등급을 달성했습니다. 스마트 전력 관리 시스템 도입과 고효율 가전제품 교체가 큰 효과를 보였습니다. 이상 감지 건수도 1건으로 대폭 감소하여 안정적인 전력 운영을 보여주고 있습니다.'
  });

  // 실시간 데이터 업데이트 시뮬레이션
  const updateEnergyData = () => {
    // 일간 데이터 약간 변경
    energyMockData.daily.pie.forEach(item => {
      const variation = (Math.random() - 0.5) * 10; // ±5 변동
      item.value = Math.max(5, Math.round(item.value + variation));
    });
  };

  // 랜덤 이상 알림 생성
  const generateRandomAnomaly = () => {
    const randomType = anomalyTypes[Math.floor(Math.random() * anomalyTypes.length)];
    const randomMessage = randomType.messages[Math.floor(Math.random() * randomType.messages.length)];
    
    return {
      id: Date.now(),
      type: randomType.type,
      message: randomMessage,
      color: randomType.color,
      icon: randomType.icon,
      timestamp: new Date().toLocaleTimeString('ko-KR'),
      severity: Math.random() > 0.5 ? 'high' : 'medium'
    };
  };

  // 대시보드 실시간 데이터
  const dashboardData = reactive({
    currentPower: 1245.7,
    temperature: 23.5,
    humidity: 58.2,
    brightness: 450,
    lastUpdated: new Date(),
    isConnected: true,
    powerHistory: [],
    basePower: 1300, // 기준 전력값
    outlierCount: 0   // outlier 카운터
  });

  // 실시간 대시보드 데이터 업데이트
  const updateDashboardData = () => {
    // 전력 사용량 - 안정적이지만 가끔 outlier
    const isOutlier = Math.random() < 0.1; // 10% 확률로 outlier
    
    if (isOutlier) {
      // Outlier: 기준값에서 크게 벗어남 (±300-500W)
      const outlierDirection = Math.random() > 0.5 ? 1 : -1;
      const outlierAmount = 300 + Math.random() * 200; // 300-500W
      dashboardData.currentPower = parseFloat((dashboardData.basePower + (outlierDirection * outlierAmount)).toFixed(1));
      dashboardData.outlierCount++;
    } else {
      // 일반적인 변동: 기준값 ±50W 내에서 작은 변동
      const smallVariation = (Math.random() - 0.5) * 100; // ±50W
      dashboardData.currentPower = parseFloat((dashboardData.basePower + smallVariation).toFixed(1));
    }
    
    // 온도 (20-30°C 범위에서 변동)
    dashboardData.temperature = parseFloat((20 + Math.random() * 10).toFixed(1));
    
    // 습도 (40-80% 범위에서 변동)
    dashboardData.humidity = parseFloat((40 + Math.random() * 40).toFixed(1));
    
    // 조도 (200-800 lx 범위에서 변동)
    dashboardData.brightness = Math.round(200 + Math.random() * 600);
    
    // 업데이트 시간
    dashboardData.lastUpdated = new Date();
    
    // 전력 히스토리에 추가 (최대 50개 유지)
    dashboardData.powerHistory.push({
      timestamp: new Date(),
      value: dashboardData.currentPower,
      isOutlier: isOutlier
    });
    
    if (dashboardData.powerHistory.length > 50) {
      dashboardData.powerHistory.shift();
    }
  };

  // 초기 전력 히스토리 생성 (지난 50분 데이터)
  const generateInitialPowerHistory = () => {
    const history = [];
    const now = new Date();
    
    for (let i = 49; i >= 0; i--) {
      const timestamp = new Date(now.getTime() - i * 60000); // 1분씩 과거
      
      // 초기 데이터도 안정적이지만 가끔 outlier
      const isOutlier = Math.random() < 0.08; // 8% 확률로 outlier
      let value;
      
      if (isOutlier) {
        // Outlier: 기준값에서 크게 벗어남
        const outlierDirection = Math.random() > 0.5 ? 1 : -1;
        const outlierAmount = 300 + Math.random() * 200;
        value = parseFloat((dashboardData.basePower + (outlierDirection * outlierAmount)).toFixed(1));
      } else {
        // 일반적인 변동: 기준값 ±50W 내에서 작은 변동
        const smallVariation = (Math.random() - 0.5) * 100;
        value = parseFloat((dashboardData.basePower + smallVariation).toFixed(1));
      }
      
      history.push({ timestamp, value, isOutlier });
    }
    
    dashboardData.powerHistory = history;
  };

  return {
    energyMockData,
    aiRecommendations,
    anomalyTypes,
    esgReportData,
    dashboardData,
    updateEnergyData,
    generateRandomAnomaly,
    updateDashboardData,
    generateInitialPowerHistory
  };
}
