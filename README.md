# 무선·신호처리 24주 학습 허브

MATLAB과 Agentic AI 기반 DSP, Beamforming, NR 지상망, Ray Tracing, ISAC의 24주 로드맵과 72개 실습 세션을 제공하는 한국어 정적 사이트입니다.

## 실행

`dist/`를 정적 HTTP 서버로 제공합니다. Python이 있다면 `python -m http.server 8000 --directory dist` 실행 후 `http://localhost:8000`에서 확인합니다. 별도의 빌드나 npm 의존성이 없습니다.

## 구조

- `dist/index.html`: 학습 사이트
- `dist/style.css`: 반응형 디자인
- `dist/app.js`: 주차 선택 및 세션 표시
- `dist/roadmap.json`: 24주·72세션 학습 자료
- `.openai/hosting.json`: Sites 배포 설정

## 내용 관리

Notion 학습 허브의 로드맵을 고정 사본으로 옮겼습니다. 자동 발행이나 Notion 동기화는 구현하지 않았습니다. 제목·일정·목표·이론·실습은 `dist/roadmap.json`에서 수정합니다. 개인 학습 기록, 토큰, 실습 출력물은 공개 저장소에 넣지 마세요. 원본 첨부 PDF와 MATLAB 패키지는 재배포하지 않으며 Notion에서 접근합니다.

학습 자료의 MATLAB R2025b Update 1 환경 설명은 원본 기준이며 이 사이트 제작 과정에서 MATLAB 코드를 실행 검증하지 않았습니다. 추가 Toolbox 과정과 교육용 모델을 표준 NR 구현으로 표현하지 마세요.

## Jetson 데이터 흐름 실습 사이트

[Jetson Flow Lab — 데이터 흐름 실습실](https://jetson-flow-lab.fbwogkr98.chatgpt.site)

추가 보드 없이 Jetson Nano 2GB의 LAN·USB와 PC·서버를 활용하는 입문 실습입니다. 데이터 크기·전송 경로·CPU/GPU 처리 방식을 바꾸면서 메모리, 버퍼, 복사와 전송 흐름을 살펴볼 수 있습니다.

- 연결 구성 → 데이터 입력 → 처리 → 결과 확인 순서의 실습 안내와 예제 코드
- 가상 IQ 생성·FFT 실행, MATLAB 무선 신호처리와 LLM_Study 확장 안내
- **접근:** 사이트 소유자만 접근 가능한 비공개 사이트입니다. 이 공개 저장소에 링크를 기록해도 사이트 접근 권한은 변경되지 않습니다. 공개 전환은 소유자의 별도 승인 후에만 진행합니다.

메모리 계산·FFT·TCP 및 파일 처리 예제는 실행 검증했습니다. 브라우저 클릭 검증과 실제 Jetson 하드웨어 성능 측정은 수행하지 못했습니다. 사이트의 메모리·전송 수치는 학습용 추정값입니다.
