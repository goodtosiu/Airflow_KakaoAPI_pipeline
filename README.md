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
이 데이터 파이프라인은 강화학습 모델 학습을 위한 데이터 셋을 마련하기 위해 구축했습니다.
서울시설공단에서 운영하는 장애인 콜택시 서비스의 사용자 대기시간을 감소시키기 위해 콜택시 차량의 차고지 배차 최적화를 위한 강화학습 모델을 도입하였고
모델의 보상으로 활용하기 위한 서울시의 각 동과 차고지 간의 요일 별, 시간대 별 소요 시간을 수집해야 했습니다.
이때 Kakao Mobility API를 활용해 원천 데이터를 수집하고, 정제하여 데이터 셋을 구축했습니다.
Airflow를 활용해 다수의 API 요청을 자동화하고, ThreadPoolExecutor을 활용해 여러개의 API key를 활용해 병렬처리 하였습니다.
또한 요청 수를 줄이기 위해 일부 시점만을 수집하고 PCHIP 보간법을 활용해 데이터를 증강하였습니다.
Docker compose 환경에서 파이프라인을 구축하였고, PostgreSQL을 사용해 DB를 저장했습니다.

## 📎 기타
- 데이터의 중복과 누락을 방지하기 위한 파이프라인 설계
- API 호출 실패 감지 및 리트라이 로직 포함
