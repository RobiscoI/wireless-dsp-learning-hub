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
