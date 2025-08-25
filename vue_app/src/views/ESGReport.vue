<template>
  <div class="esg-report">
    <div class="container">
      <header class="page-header">
        <h1>📋 ESG 환경 보고서</h1>
        <p class="page-subtitle">월별 환경 성과를 분석하고 ESG 등급을 확인하세요</p>
      </header>

      <!-- 보고 기간 선택 -->
      <div class="period-selector">
        <div class="selector-header">
          <h3>📅 보고 기간 선택</h3>
          <div class="loading-indicator" v-if="isLoading">
            <div class="spinner"></div>
            <span>보고서 생성 중...</span>
          </div>
        </div>
        <div class="month-tabs">
          <button 
            v-for="month in esgReportData.months" 
            :key="month"
            class="month-tab"
            :class="{ 'month-tab--active': selectedMonth === month }"
            @click="selectMonth(month)"
          >
            {{ month }}
          </button>
        </div>
      </div>

      <!-- 기본 정보 대시보드 -->
      <div class="dashboard-section">
        <div class="info-cards">
          <div class="info-card info-card--energy">
            <div class="card-icon">⚡</div>
            <div class="card-content">
              <div class="card-value">{{ currentData.energyUsage.toFixed(1) }}</div>
              <div class="card-unit">kWh</div>
              <div class="card-label">에너지 사용량</div>
            </div>
          </div>

          <div class="info-card info-card--carbon">
            <div class="card-icon">🌱</div>
            <div class="card-content">
              <div class="card-value">{{ currentData.carbonEmission.toFixed(1) }}</div>
              <div class="card-unit">kgCO₂</div>
              <div class="card-label">탄소 배출량</div>
            </div>
          </div>

          <div class="info-card info-card--savings">
            <div class="card-icon">💰</div>
            <div class="card-content">
              <div class="card-value">{{ currentData.savings.toLocaleString() }}</div>
              <div class="card-unit">원</div>
              <div class="card-label">절감된 전기요금</div>
            </div>
          </div>

          <div class="info-card info-card--anomalies">
            <div class="card-icon">🚨</div>
            <div class="card-content">
              <div class="card-value">{{ currentData.anomaliesDetected }}</div>
              <div class="card-unit">건</div>
              <div class="card-label">이상 감지</div>
            </div>
          </div>
        </div>
      </div>

      <!-- ESG 평가 등급 게이지 -->
      <div class="grade-section">
        <div class="grade-container">
          <h3>🎯 ESG 환경 평가 등급</h3>
          <div class="gauge-wrapper">
            <div class="gauge-chart" ref="gaugeChart">
              <canvas ref="gaugeCanvas" width="300" height="200"></canvas>
              <div class="gauge-center">
                <div class="current-grade">{{ currentData.grade }}</div>
                <div class="current-score">{{ animatedScore }}점</div>
              </div>
            </div>
            <div class="grade-legend">
              <div class="legend-item" v-for="grade in gradeScale" :key="grade.name">
                <div class="legend-color" :style="{ background: grade.color }"></div>
                <span class="legend-label">{{ grade.name }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="grade-improvement">
          <h4>📈 등급 변화</h4>
          <div class="improvement-stats">
            <div class="stat-item" v-if="previousMonthData">
              <span class="stat-label">이전 등급:</span>
              <span class="stat-value">{{ previousMonthData.grade }} ({{ previousMonthData.score }}점)</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">현재 등급:</span>
              <span class="stat-value">{{ currentData.grade }} ({{ currentData.score }}점)</span>
            </div>
            <div class="stat-item" v-if="previousMonthData">
              <span class="stat-label">개선도:</span>
              <span class="stat-value improvement" v-if="currentData.score > previousMonthData.score">
                +{{ currentData.score - previousMonthData.score }}점 ⬆️
              </span>
              <span class="stat-value decline" v-else-if="currentData.score < previousMonthData.score">
                {{ currentData.score - previousMonthData.score }}점 ⬇️
              </span>
              <span class="stat-value stable" v-else>
                변화 없음 ➡️
              </span>
            </div>
            <div class="stat-item" v-else>
              <span class="stat-label">상태:</span>
              <span class="stat-value">첫 번째 월 데이터</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 전달 대비 탄소 배출 비교 -->
      <div class="comparison-section">
        <h3>📊 전월 대비 탄소 배출 비교</h3>
        <div class="comparison-content">
          <div class="chart-container">
            <canvas ref="comparisonChart" width="400" height="200"></canvas>
          </div>
          <div class="comparison-stats">
            <div class="reduction-highlight">
              <div class="reduction-value">{{ esgReportData.comparison.reduction }}%</div>
              <div class="reduction-label">탄소 배출 감축률</div>
              <div class="reduction-trend">📉 전월 대비 개선</div>
            </div>
            <div class="comparison-details">
              <div class="detail-item">
                <span class="detail-label">5월 배출량:</span>
                <span class="detail-value">{{ esgReportData.comparison.current[0] }} kgCO₂</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">6월 배출량:</span>
                <span class="detail-value">{{ esgReportData.comparison.current[1] }} kgCO₂</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 종합 의견 섹션 -->
      <div class="opinion-section">
        <h3>📝 종합 의견</h3>
        <div class="opinion-content">
          <div class="opinion-text">
            {{ esgReportData.opinion }}
          </div>
          <div class="opinion-signature">
            <div class="signature-line">
              <span class="signature-label">분석 일시:</span>
              <span class="signature-value">{{ new Date().toLocaleDateString('ko-KR') }}</span>
            </div>
            <div class="signature-line">
              <span class="signature-label">분석 시스템:</span>
              <span class="signature-value">AI 기반 ESG 분석 엔진 v2.1</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 보고서 다운로드 -->
      <div class="download-section">
        <div class="download-content">
          <div class="download-info">
            <h3>📥 보고서 다운로드</h3>
            <p>완성된 ESG 보고서를 PDF 형태로 다운로드하여 보관하거나 공유하세요.</p>
          </div>
          <div class="download-actions">
            <button 
              class="btn btn--primary btn--large"
              @click="downloadReport"
              :disabled="isDownloading"
            >
              <div v-if="isDownloading" class="btn-loading">
                <div class="spinner"></div>
                <span>PDF 생성 중...</span>
              </div>
              <div v-else class="btn-content">
                <span class="btn-icon">📄</span>
                <span>PDF 다운로드</span>
              </div>
            </button>
            <button class="btn btn--secondary" @click="shareReport">
              <span class="btn-icon">📤</span>
              <span>보고서 공유</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch, nextTick } from 'vue';
import { Chart, registerables } from 'chart.js';

import { useMockData } from '../composables/useMockData.js';
import { useApiSimulation } from '../composables/useApiSimulation.js';

Chart.register(...registerables);

// Composables
const { esgReportData } = useMockData();
const { isLoading, simulateApiCall, simulatePdfDownload } = useApiSimulation();

// Reactive data
const selectedMonth = ref(esgReportData.currentMonth);
const isDownloading = ref(false);
const animatedScore = ref(0);
const gaugeCanvas = ref(null);
const comparisonChart = ref(null);
let gaugeInstance = null;
let comparisonInstance = null;

// ESG 등급 스케일
const gradeScale = [
  { name: 'A+', color: '#059669', min: 90, max: 100 },
  { name: 'A0', color: '#10b981', min: 80, max: 89 },
  { name: 'A-', color: '#34d399', min: 75, max: 79 },
  { name: 'B+', color: '#fbbf24', min: 70, max: 74 },
  { name: 'B0', color: '#f59e0b', min: 65, max: 69 },
  { name: 'B-', color: '#d97706', min: 60, max: 64 },
  { name: 'C+', color: '#fb923c', min: 55, max: 59 },
  { name: 'C0', color: '#f97316', min: 50, max: 54 },
  { name: 'C-', color: '#ea580c', min: 45, max: 49 },
  { name: 'D+', color: '#ef4444', min: 40, max: 44 },
  { name: 'D0', color: '#dc2626', min: 35, max: 39 },
  { name: 'D-', color: '#b91c1c', min: 30, max: 34 },
  { name: 'F', color: '#991b1b', min: 0, max: 29 }
];

// Computed properties
const currentData = computed(() => {
  return esgReportData.monthlyData[selectedMonth.value] || esgReportData.basicInfo;
});

const previousMonthData = computed(() => {
  const currentIndex = esgReportData.months.indexOf(selectedMonth.value);
  if (currentIndex <= 0) return null;
  
  const previousMonth = esgReportData.months[currentIndex - 1];
  return esgReportData.monthlyData[previousMonth];
});

// Methods
const selectMonth = async (month) => {
  selectedMonth.value = month;
  
  await simulateApiCall(async () => {
    // 월별 데이터 변경 시뮬레이션
    await nextTick();
    updateCharts();
    animateScore();
  });
};

const animateScore = () => {
  const targetScore = currentData.value.score || esgReportData.gradeInfo.score;
  const duration = 1500;
  const startTime = Date.now();
  const startScore = animatedScore.value;

  const animate = () => {
    const elapsed = Date.now() - startTime;
    const progress = Math.min(elapsed / duration, 1);
    
    // Easing function (ease-out)
    const easeOut = 1 - Math.pow(1 - progress, 3);
    
    animatedScore.value = Math.round(startScore + (targetScore - startScore) * easeOut);
    
    if (progress < 1) {
      requestAnimationFrame(animate);
    }
  };
  
  animate();
};

const createGaugeChart = () => {
  if (!gaugeCanvas.value) return;

  const ctx = gaugeCanvas.value.getContext('2d');
  const score = currentData.value.score || esgReportData.gradeInfo.score;
  
  // 기존 차트 제거
  if (gaugeInstance) {
    gaugeInstance.destroy();
  }

  // 게이지 차트 데이터 생성
  const data = gradeScale.map(grade => {
    if (score >= grade.min && score <= grade.max) {
      return { value: grade.max - grade.min + 1, backgroundColor: grade.color };
    }
    return { value: grade.max - grade.min + 1, backgroundColor: '#e5e7eb' };
  });

  gaugeInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      datasets: [{
        data: data.map(d => d.value),
        backgroundColor: data.map(d => d.backgroundColor),
        borderWidth: 0,
        cutout: '70%',
        rotation: -90,
        circumference: 180
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          enabled: false
        }
      }
    }
  });
};

const createComparisonChart = () => {
  if (!comparisonChart.value) return;

  const ctx = comparisonChart.value.getContext('2d');
  
  // 기존 차트 제거
  if (comparisonInstance) {
    comparisonInstance.destroy();
  }

  comparisonInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: esgReportData.comparison.labels,
      datasets: [{
        label: '탄소 배출량 (kgCO₂)',
        data: esgReportData.comparison.current,
        backgroundColor: ['#fbbf24', '#10b981'],
        borderColor: ['#f59e0b', '#059669'],
        borderWidth: 2,
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              return `${context.parsed.y} kgCO₂`;
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: '탄소 배출량 (kgCO₂)'
          }
        }
      }
    }
  });
};

const updateCharts = async () => {
  await nextTick();
  createGaugeChart();
  createComparisonChart();
};

const downloadReport = async () => {
  isDownloading.value = true;
  
  try {
    // 동적으로 라이브러리 import
    const html2canvas = (await import('html2canvas')).default;
    const jsPDF = (await import('jspdf')).jsPDF;
    
    // 다운로드 버튼 숨기기 (PDF에 포함되지 않도록)
    const downloadSection = document.querySelector('.download-section');
    const originalDisplay = downloadSection.style.display;
    downloadSection.style.display = 'none';
    
    // 페이지 전체를 캡처
    const element = document.querySelector('.esg-report');
    
    // 고해상도 캔버스 생성
    const canvas = await html2canvas(element, {
      scale: 2, // 해상도 향상
      useCORS: true,
      allowTaint: true,
      backgroundColor: '#ffffff',
      width: element.scrollWidth,
      height: element.scrollHeight,
      scrollX: 0,
      scrollY: 0
    });
    
    // 다운로드 섹션 다시 표시
    downloadSection.style.display = originalDisplay;
    
    // PDF 생성
    const imgData = canvas.toDataURL('image/png');
    const pdf = new jsPDF('p', 'mm', 'a4');
    
    // A4 크기 계산
    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = pdf.internal.pageSize.getHeight();
    
    // 이미지 크기 조정
    const imgWidth = pdfWidth;
    const imgHeight = (canvas.height * pdfWidth) / canvas.width;
    
    let heightLeft = imgHeight;
    let position = 0;
    
    // 첫 페이지 추가
    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
    heightLeft -= pdfHeight;
    
    // 여러 페이지가 필요한 경우 페이지 추가
    while (heightLeft >= 0) {
      position = heightLeft - imgHeight;
      pdf.addPage();
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= pdfHeight;
    }
    
    // PDF 다운로드
    const fileName = `ESG_환경보고서_${selectedMonth.value}_${new Date().getFullYear()}.pdf`;
    pdf.save(fileName);
    
    // 성공 메시지
    alert(`✅ PDF 다운로드가 완료되었습니다!\n파일명: ${fileName}`);
    
  } catch (error) {
    console.error('PDF 생성 오류:', error);
    alert(`❌ PDF 생성 중 오류가 발생했습니다: ${error.message}`);
  } finally {
    isDownloading.value = false;
  }
};

const shareReport = async () => {
  await simulateApiCall(async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: `ESG 보고서 - ${selectedMonth.value}`,
          text: `${selectedMonth.value} ESG 환경 성과 보고서를 확인하세요.`,
          url: window.location.href
        });
      } catch (err) {
        console.log('공유가 취소되었습니다.');
      }
    } else {
      // 대체 공유 방법
      const url = window.location.href;
      await navigator.clipboard.writeText(url);
      alert('보고서 링크가 클립보드에 복사되었습니다!');
    }
  });
};

// Lifecycle
onMounted(async () => {
  await nextTick();
  updateCharts();
  animateScore();
});

// Watch for month changes
watch(selectedMonth, () => {
  updateCharts();
  animateScore();
});
</script>

<style scoped>
.esg-report {
  min-height: 100vh;
  background: #f8fafc;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 2.5rem;
  color: #1e293b;
  margin-bottom: 10px;
}

.page-subtitle {
  font-size: 1.1rem;
  color: #64748b;
  margin: 0;
}

.period-selector {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.selector-header h3 {
  font-size: 1.3rem;
  color: #1e293b;
  margin: 0;
}

.loading-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #64748b;
  font-size: 0.9rem;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #e2e8f0;
  border-top: 2px solid #4f46e5;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.month-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.month-tab {
  padding: 10px 20px;
  border: 2px solid #e2e8f0;
  background: white;
  color: #64748b;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.month-tab--active {
  border-color: #4f46e5;
  background: #4f46e5;
  color: white;
}

.month-tab:hover:not(.month-tab--active) {
  border-color: #cbd5e1;
  background: #f8fafc;
}

.dashboard-section {
  margin-bottom: 30px;
}

.info-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.info-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: transform 0.2s ease;
}

.info-card:hover {
  transform: translateY(-2px);
}

.info-card--energy {
  border-left: 4px solid #3b82f6;
}

.info-card--carbon {
  border-left: 4px solid #10b981;
}

.info-card--savings {
  border-left: 4px solid #f59e0b;
}

.info-card--anomalies {
  border-left: 4px solid #ef4444;
}

.card-icon {
  font-size: 2.5rem;
}

.card-content {
  flex: 1;
}

.card-value {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  line-height: 1;
}

.card-unit {
  font-size: 0.9rem;
  color: #64748b;
  margin-left: 4px;
}

.card-label {
  font-size: 0.9rem;
  color: #64748b;
  margin-top: 4px;
}

.grade-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 30px;
  margin-bottom: 30px;
}

.grade-container {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.grade-container h3 {
  font-size: 1.3rem;
  color: #1e293b;
  margin: 0 0 20px 0;
}

.gauge-wrapper {
  text-align: center;
}

.gauge-chart {
  position: relative;
  display: inline-block;
  margin-bottom: 20px;
}

.gauge-center {
  position: absolute;
  top: 60%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.current-grade {
  font-size: 2.5rem;
  font-weight: 800;
  color: #1e293b;
  line-height: 1;
}

.current-score {
  font-size: 1.2rem;
  color: #64748b;
  margin-top: 4px;
}

.grade-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.8rem;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.legend-label {
  color: #64748b;
  font-weight: 500;
}

.grade-improvement {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.grade-improvement h4 {
  font-size: 1.2rem;
  color: #1e293b;
  margin: 0 0 16px 0;
}

.improvement-stats {
  space-y: 12px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #e2e8f0;
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  color: #64748b;
  font-size: 0.9rem;
}

.stat-value {
  color: #1e293b;
  font-weight: 600;
  font-size: 0.9rem;
}

.stat-value.improvement {
  color: #10b981;
}

.stat-value.decline {
  color: #ef4444;
}

.stat-value.stable {
  color: #64748b;
}

.comparison-section {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.comparison-section h3 {
  font-size: 1.3rem;
  color: #1e293b;
  margin: 0 0 20px 0;
}

.comparison-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 30px;
  align-items: center;
}

.chart-container {
  height: 200px;
  position: relative;
}

.comparison-stats {
  text-align: center;
}

.reduction-highlight {
  background: linear-gradient(135deg, #d1fae5, #a7f3d0);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
}

.reduction-value {
  font-size: 3rem;
  font-weight: 800;
  color: #059669;
  line-height: 1;
}

.reduction-label {
  font-size: 1rem;
  color: #065f46;
  font-weight: 600;
  margin: 8px 0;
}

.reduction-trend {
  font-size: 0.9rem;
  color: #047857;
}

.comparison-details {
  space-y: 8px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
}

.detail-label {
  color: #64748b;
}

.detail-value {
  color: #1e293b;
  font-weight: 600;
}

.opinion-section {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.opinion-section h3 {
  font-size: 1.3rem;
  color: #1e293b;
  margin: 0 0 20px 0;
}

.opinion-text {
  font-size: 1rem;
  line-height: 1.6;
  color: #374151;
  margin-bottom: 20px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
  border-left: 4px solid #4f46e5;
}

.opinion-signature {
  display: flex;
  justify-content: space-between;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

.signature-line {
  font-size: 0.85rem;
}

.signature-label {
  color: #64748b;
  margin-right: 8px;
}

.signature-value {
  color: #1e293b;
  font-weight: 500;
}

.download-section {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.download-content {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 30px;
  align-items: center;
}

.download-info h3 {
  font-size: 1.3rem;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.download-info p {
  color: #64748b;
  margin: 0;
  line-height: 1.5;
}

.download-actions {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn--primary {
  background: #4f46e5;
  color: white;
}

.btn--primary:hover:not(:disabled) {
  background: #3730a3;
}

.btn--secondary {
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #e2e8f0;
}

.btn--secondary:hover {
  background: #e2e8f0;
}

.btn--large {
  padding: 16px 32px;
  font-size: 1rem;
}

.btn-loading {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-icon {
  font-size: 1.1em;
}

/* PDF 출력용 스타일 */
@media print {
  .download-section {
    display: none !important;
  }
  
  .esg-report {
    background: white !important;
  }
  
  .container {
    max-width: none !important;
    padding: 0 !important;
  }
  
  .info-cards,
  .grade-section,
  .comparison-content,
  .download-content {
    break-inside: avoid;
  }
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .info-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .grade-section {
    grid-template-columns: 1fr;
  }
  
  .comparison-content {
    grid-template-columns: 1fr;
  }
  
  .download-content {
    grid-template-columns: 1fr;
    text-align: center;
  }
  
  .download-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
  
  .month-tabs {
    justify-content: center;
  }
  
  .opinion-signature {
    flex-direction: column;
    gap: 8px;
  }
}
</style>
