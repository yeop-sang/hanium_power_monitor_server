# 스마트 전력 소비 측정 및 ESG 리포트 시스템

![Project Status](https://img.shields.io/badge/진행률-50%25-green)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Vue.js](https://img.shields.io/badge/Vue.js-3.0+-green)
![Docker](https://img.shields.io/badge/Docker-latest-blue)

> **한이음 ICT 멘토링 공모전 프로젝트**  
> 실시간 전력 소비 데이터 수집 및 AI 기반 ESG 환경 보고서 생성 시스템

## 🎯 프로젝트 개요

이 프로젝트는 Arduino/ESP32 센서를 통해 실시간으로 전력 소비량과 환경 데이터(온도, 습도, 조도)를 수집하고, 수집된 데이터를 기반으로 AI가 생성하는 ESG 환경 보고서를 제공하는 종합 시스템입니다.

### 🌟 주요 특징

- **실시간 데이터 수집**: Arduino/ESP32에서 5초마다 MQTT를 통한 데이터 전송
- **다중 센서 지원**: 전력 소비량, 온도, 습도, 조도 동시 측정
- **AI 기반 ESG 리포트**: Claude API를 활용한 환경 영향 분석 및 개선 제안
- **웹 기반 대시보드**: Vue.js로 구현된 직관적인 데이터 시각화
- **탄소 배출량 계산**: 전력 소비량 기반 탄소 발자국 자동 계산 (0.478 kgCO₂/kWh)
- **마이크로서비스 아키텍처**: Docker를 통한 확장 가능한 시스템 구조

## 🏗️ 시스템 아키텍처

```
ESP32/Arduino ──► MQTT Broker ──► Flask Backend ──► MySQL Database
                                        │
                                        ▼
Vue.js Frontend ◄────────────────── AI/LLM Module
```

### 🔧 기술 스택

#### Backend
- **Flask 2.0.1**: RESTful API 서버
- **MySQL 8.0**: 데이터 영구 저장
- **Eclipse Mosquitto**: MQTT 브로커
- **Flask-SocketIO**: 실시간 웹소켓 통신
- **Paho MQTT**: MQTT 클라이언트

#### Frontend
- **Vue.js 3.5**: 프론트엔드 프레임워크
- **Chart.js**: 데이터 시각화
- **Axios**: HTTP 클라이언트
- **Socket.IO**: 실시간 데이터 업데이트

#### AI/ML
- **Claude API (Anthropic)**: ESG 리포트 생성
- **Python**: AI 모듈 구현

#### Infrastructure
- **Docker & Docker Compose**: 컨테이너 오케스트레이션
- **Nginx**: 웹 서버 및 리버스 프록시

## 📁 프로젝트 구조

```
power_flow_server/
├── 📁 ai_llm_module/         # AI/LLM 모듈
│   └── Dockerfile
├── 📁 flask_app/             # Flask 백엔드
│   ├── app.py                # 메인 애플리케이션
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── 📁 modules/           # 핵심 모듈
│   │   ├── api.py           # REST API 엔드포인트
│   │   ├── database.py      # 데이터베이스 연결
│   │   └── mqtt_client.py   # MQTT 클라이언트
│   ├── 📁 scripts/          # 유틸리티 스크립트
│   │   └── publish_dummy_mqtt.py  # 테스트 데이터 발행
│   └── 📁 tests/            # 테스트 코드
├── 📁 vue_app/              # Vue.js 프론트엔드
│   ├── package.json
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── 📁 src/
│   │   ├── App.vue
│   │   ├── 📁 components/   # Vue 컴포넌트
│   │   │   ├── CurrentPowerDisplay.vue
│   │   │   ├── EnvironmentalData.vue
│   │   │   ├── ESGReport.vue
│   │   │   ├── NavBar.vue
│   │   │   └── PowerChart.vue
│   │   ├── 📁 services/     # API 서비스
│   │   │   ├── api.js
│   │   │   └── socket.js
│   │   └── 📁 views/        # 페이지 뷰
│   │       ├── Home.vue
│   │       └── Reports.vue
│   └── 📁 tests/           # 프론트엔드 테스트
├── 📁 mysql/               # MySQL 설정
│   └── init.sql           # 데이터베이스 초기화
├── 📁 mosquitto/          # MQTT 브로커 설정
│   └── 📁 config/
│       └── mosquitto.conf
├── docker-compose.yml     # Docker 서비스 구성
└── 📁 scripts/           # 프로젝트 스크립트
    └── prd.txt          # 프로젝트 요구사항 문서
```

## 🚀 실행 방법

### 1. 환경 설정

프로젝트 루트에 `.env` 파일을 생성하고 다음 환경 변수를 설정합니다:

```bash
# MySQL 설정
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_USER=power_user
MYSQL_PASSWORD=your_password

# AI API 키
ANTHROPIC_API_KEY=your_anthropic_api_key

# MQTT 설정 (선택사항)
MQTT_TOPIC=power/measurement
MQTT_TEST_TOPIC=power/test
```

### 2. Docker 컨테이너 실행

```bash
# 전체 시스템 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 특정 서비스만 시작
docker-compose up -d mysql mosquitto flask_app
```

### 3. 서비스 접속

- **웹 대시보드**: http://localhost (포트 80)
- **Flask API**: http://localhost:5001
- **MySQL**: localhost:3306
- **MQTT 브로커**: localhost:1883

## 🧪 테스트 데이터 발행

### publish_dummy_mqtt.py 사용법

센서 데이터 없이 시스템을 테스트할 수 있도록 더미 MQTT 데이터를 발행하는 스크립트가 제공됩니다.

```bash
# 스크립트 실행 (호스트에서)
cd flask_app/scripts
python publish_dummy_mqtt.py
```

**스크립트 기능:**
- 5초마다 10개의 테스트 데이터 발행
- 실제 센서 데이터 형식과 동일한 JSON 구조
- 랜덤 값으로 실제 환경 시뮬레이션

**생성되는 데이터 형식:**
```json
{
    "deviceCode": 1234,
    "timestamp": "2023-06-27T14:30:00Z",
    "temp": 25.3,
    "humidity": 55.2,
    "brightness": 650,
    "electric": 1150.5
}
```

### 환경 변수 설정

스크립트 실행 전 MQTT 브로커 주소를 설정할 수 있습니다:

```bash
# 호스트에서 실행할 때
export MQTT_BROKER_HOST=localhost

# Docker 컨테이너 내에서 실행할 때
export MQTT_BROKER_HOST=mosquitto
```

## 📊 데이터베이스 스키마

### power_readings 테이블
```sql
CREATE TABLE power_readings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,           -- 디바이스 측정 시간
    device_code VARCHAR(25) NOT NULL,      -- 디바이스 MAC 주소
    temperature FLOAT,                     -- 온도 (°C)
    humidity FLOAT,                        -- 습도 (%)
    brightness INT,                        -- 조도 (Lux)
    electric FLOAT,                        -- 전력 소비량 (W)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 서버 저장 시간
);
```

### esg_reports 테이블
```sql
CREATE TABLE esg_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_path VARCHAR(255) NOT NULL,       -- 리포트 파일 경로
    created_at DATETIME NOT NULL           -- 리포트 생성 시간
);
```

## 📈 현재 진행 상황 (Task-Master 기반)

### ✅ 완료된 작업 (50% 진행)

1. **✓ Raspberry Pi with Docker 설정** - Docker 환경 구축
2. **✓ Docker Compose 구성** - 전체 서비스 컨테이너 정의
3. **✓ MQTT 브로커 구성** - Mosquitto 메시지 큐 설정
4. **✓ MySQL 데이터베이스 설정** - 스키마 및 초기화 스크립트
5. **✓ Flask 백엔드 개발** - API, MQTT 클라이언트, 데이터베이스 연동

**하위 작업 진행률**: 88% (22/25 완료)

### 🚧 진행 예정 작업

6. **Vue.js 프론트엔드 개발** *(다음 우선순위)*
   - 6.6 API 통합 및 데이터 관리 (진행 예정)
   - 6.8 테스트 및 반응형 디자인 검증 (진행 예정)
   - 6.9 Socket.IO를 통한 실시간 데이터 스트리밍 (진행 예정)

7. **AI/LLM 모듈 ESG 리포트 생성** 
8. **ESG 리포트 디스플레이 통합**
9. **데이터 시각화 컴포넌트 구현**
10. **시스템 통합 및 테스트**

## 🎨 ESG 리포트 기능

### 환경 영향 분석
- **전력 소비 패턴 분석**: 시간대별/일별 사용량 트렌드
- **탄소 배출량 계산**: 전력 소비량 × 0.478 kgCO₂/kWh
- **환경 데이터 상관관계**: 온도, 습도와 전력 소비의 관계 분석
- **개선 제안**: AI 기반 맞춤형 에너지 절약 팁

### 리포트 형식
- 구조화된 테이블 형태의 데이터 표현
- 웹 대시보드 직접 표시
- 향후 PDF 내보내기 기능 계획

## 🔧 개발 도구

### Task-Master 프로젝트 관리
프로젝트는 Task-Master를 통해 체계적으로 관리되고 있습니다:

```bash
# 현재 작업 목록 확인
task-master list

# 다음 작업 확인
task-master next

# 작업 상태 업데이트
task-master set-status --id=6 --status=in-progress
```

### 테스트 도구
```bash
# Flask 백엔드 테스트
cd flask_app && python -m pytest tests/

# Vue.js 프론트엔드 테스트
cd vue_app && npm run test:unit
```

## 📝 개발 규칙

프로젝트는 다음 개발 규칙을 따릅니다:
- **데이터 무결성 우선**: 실시간성보다는 데이터 손실 방지
- **컨테이너 기반 개발**: 모든 서비스는 Docker 컨테이너로 구현
- **API 우선 설계**: RESTful API를 통한 마이크로서비스 통신
- **환경 변수 관리**: 민감한 정보는 환경 변수로 분리
- **테스트 주도 개발**: 각 모듈별 단위 테스트 구현

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 연락처

**한이음 ICT 멘토링 공모전**  
프로젝트 문의: [GitHub Issues](https://github.com/your-username/power_flow_server/issues)
이메일: 김상엽 [yeop@yeop.kr](mailto:yeop@yeop.kr)

---

> 💡 **참고**: 이 프로젝트는 교육 및 연구 목적으로 개발되었으며, 실제 상용 환경에서 사용 시 추가적인 보안 및 성능 최적화가 필요할 수 있습니다. 