# Kakao Mobility API 자동화 파이프라인

도시 교통 데이터를 수집·가공·저장하기 위한 Airflow 기반 데이터 파이프라인입니다.  
Kakao Mobility의 미래 길찾기 API를 활용하여, 서울시 모든 동-차고지 조합에 대한 시간대별 소요시간 데이터를 수집하고 PostgreSQL에 저장합니다.

## 🔧 기술 스택
- Airflow (Docker Compose)
- Python + ThreadPoolExecutor
- PostgreSQL
- Kakao Mobility API
- scipy.interpolate (PCHIP 보간)

## 🧩 DAG 구성
1. `load_task`: 현재 수집 대상 origin-destination ID를 로드
2. `fetch_task`: API 병렬 요청 (총 240개 조합, 10개 키 사용)
3. `clean_task`: 8개 시점 → 48시점 보간 (PCHIP)
4. `save_task`: PostgreSQL 저장 + 수집 상태 파일 갱신

## 📂 DB 스키마
- `travel_time(origin_id, destination_id, origin_name, destination_name, departure_time, duration)`
- `origin(id, district, name, longitude, latitude)`
- `destination(id, name, longitude, latitude, num_of_vehicles)`

## 💡 목적
이 데이터 파이프라인은 강화학습 기반의 택시 배차 최적화 모델 학습용 데이터셋 구축을 목적으로 설계되었습니다.
서울시설공단이 운영하는 장애인 콜택시 서비스의 사용자 대기시간을 단축하고자,
차고지 배차 전략을 개선할 수 있는 강화학습 모델을 개발하는 프로젝트에 참여하였습니다.

모델의 보상 함수로 활용할 수 있는 이동 소요시간 데이터를 확보하기 위해
서울시 각 행정동과 차고지 간의 요일별·시간대별 이동시간 데이터를 수집하는 파이프라인을 구축했습니다.

이를 위해 다음과 같은 기술과 전략을 적용했습니다:
	•	Kakao Mobility API를 활용한 실시간 예상 소요시간 데이터 수집
	•	Airflow 기반 DAG 구성으로 대규모 API 요청 자동화
	•	ThreadPoolExecutor + 다중 API Key를 활용한 병렬 처리 최적화
	•	PCHIP 보간법을 활용한 일부 시점 데이터 보강 (하나의 경로에 대해 총 240개 시점 확보)
	•	Docker Compose 기반 환경 구성 및 PostgreSQL DB 연동으로 관리와 이식성 강화

이 파이프라인은 향후 강화학습 모델 학습뿐 아니라,
실제 서울시 교통 서비스의 효율적인 운영 및 시뮬레이션 분석에 필요한 기반 데이터로 활용될 수 있습니다.

## 📎 기타
- 데이터의 중복과 누락을 방지하기 위한 파이프라인 설계
- API 호출 실패 감지 및 리트라이 로직 포함
