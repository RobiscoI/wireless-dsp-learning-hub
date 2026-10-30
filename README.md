# 무선·신호처리 학습 허브 — MATLAB · Jetson

MATLAB으로 무선 신호처리의 원리를 확인하는 24주 트랙과, PC가 만든 IQ를 Jetson Nano 2GB에서 처리하는 Edge DSP 트랙을
한 저장소에서 나눠 진행합니다. 수업 설명과 학습 기록은 [Notion 학습 허브](https://app.notion.com/p/3e12eac098bd81569f76efed94daf130)가 기준입니다.

| 트랙 | 폴더 | 무엇을 하나 | 시작 |
|---|---|---|---|
| MATLAB 신호처리 | [`matlab/`](matlab/) | FFT·PSD·필터 → QPSK·OFDM → Beamforming·NR → Ray Tracing·ISAC (24주 · 72세션) | [matlab/README.md](matlab/README.md) |
| PC·Jetson Edge DSP | [`jetson/`](jetson/) | PC IQ 생성 → LAN TCP → Jetson C++ FFT·PSD → PC 검증, 이후 FIR·MUSIC·스트리밍 (교재 00~10장) | [jetson/README.md](jetson/README.md) |
| 학습 사이트 | [`dist/`](dist/) | 24주 로드맵·72세션 정적 사이트 | [아래](#학습-사이트-dist) |

두 트랙은 서로 기다리지 않습니다. MATLAB만 있을 때는 `matlab/`로 시작하고, Jetson이 준비되면 `jetson/`의 00장부터 진행합니다.

## 폴더 구조

```
wireless-dsp-learning-hub/
├── matlab/                MATLAB 신호처리 트랙
│   ├── README.md          시작 순서 · MATLAB 릴리스 호환 · 저장소 규칙
│   ├── setup_path.m       MATLAB 세션마다 한 번 — 구 릴리스(R2018a 등)용 대체 함수 연결
│   ├── compat/            exportgraphics · tiledlayout/nexttile · yline · jsonencode(PrettyPrint)
│   ├── kit/               (git 제외) Notion 「MATLAB 실행 파일과 검증 예시」 ZIP 압축 해제 위치
│   └── sessions/          내가 수정·작성한 세션 코드 (W01-S1 …)
├── jetson/                PC·Jetson Edge DSP 트랙 — 명령은 이 폴더에서 실행
│   ├── README.md
│   ├── docs/edge-dsp/     교재 00~10장 원고 · 검증 기록 · 그림
│   ├── labs/edge_dsp/     cpp/ (Jetson 서버) · python/ (클라이언트·심화) · matlab/ · tests/
│   ├── build/             (git 제외) g++ 산출물
│   └── output/            (git 제외) 실행 결과
├── dist/  .openai/        학습 사이트와 배포 설정
├── .github/               Pull request · Issue 템플릿
└── AGENTS.md              AI 에이전트 작업 지침
```

## 공개 저장소 규칙

이 저장소는 공개입니다.

- 올리지 않는 것: Notion 원본 PDF와 MATLAB 워크북 ZIP(`matlab/kit/`), 실행 결과(`results*/`, `output/`, `build/`),
  대용량 측정 IQ, 개인 학습 기록, 토큰·계정·장비 주소.
- 올리는 것: 소스 코드, 교재 원고, 작은 검증 요약.
- 커밋 전에 `git status`로 확인하고 파일을 지정해서 `git add` 합니다 (교재 06장).

## 학습 사이트 (`dist/`)

MATLAB과 Agentic AI 기반 DSP, Beamforming, NR 지상망, Ray Tracing, ISAC의 24주 로드맵과 72개 실습 세션을 제공하는 한국어 정적 사이트입니다.

### 실행

`dist/`를 정적 HTTP 서버로 제공합니다. Python이 있다면 `python -m http.server 8000 --directory dist` 실행 후 `http://localhost:8000`에서 확인합니다. 별도의 빌드나 npm 의존성이 없습니다.

### 구성

- `dist/index.html`: 학습 사이트
- `dist/style.css`: 반응형 디자인
- `dist/app.js`: 주차 선택 및 세션 표시
- `dist/roadmap.json`: 24주·72세션 학습 자료
- `.openai/hosting.json`: Sites 배포 설정

### 내용 관리

Notion 학습 허브의 로드맵을 고정 사본으로 옮겼습니다. 자동 발행이나 Notion 동기화는 구현하지 않았습니다. 제목·일정·목표·이론·실습은 `dist/roadmap.json`에서 수정합니다. 개인 학습 기록, 토큰, 실습 출력물은 공개 저장소에 넣지 마세요. 원본 첨부 PDF와 MATLAB 패키지는 재배포하지 않으며 Notion에서 접근합니다.

학습 자료의 MATLAB R2025b Update 1 환경 설명은 원본 기준이며 이 사이트 제작 과정에서 MATLAB 코드를 실행 검증하지 않았습니다. 추가 Toolbox 과정과 교육용 모델을 표준 NR 구현으로 표현하지 마세요. 구 릴리스에서 실행한 결과는 [matlab/README.md](matlab/README.md)에 있습니다.

## Jetson 데이터 흐름 실습 사이트

[Jetson Flow Lab — 데이터 흐름 실습실](https://jetson-flow-lab.fbwogkr98.chatgpt.site)

추가 보드 없이 Jetson Nano 2GB의 LAN·USB와 PC·서버를 활용하는 입문 실습입니다. 데이터 크기·전송 경로·CPU/GPU 처리 방식을 바꾸면서 메모리, 버퍼, 복사와 전송 흐름을 살펴볼 수 있습니다.

- 연결 구성 → 데이터 입력 → 처리 → 결과 확인 순서의 실습 안내와 예제 코드
- 가상 IQ 생성·FFT 실행, MATLAB 무선 신호처리와 LLM_Study 확장 안내
- **접근:** 사이트 소유자만 접근 가능한 비공개 사이트입니다. 이 공개 저장소에 링크를 기록해도 사이트 접근 권한은 변경되지 않습니다. 공개 전환은 소유자의 별도 승인 후에만 진행합니다.

메모리 계산·FFT·TCP 및 파일 처리 예제는 실행 검증했습니다. 브라우저 클릭 검증과 실제 Jetson 하드웨어 성능 측정은 수행하지 못했습니다. 사이트의 메모리·전송 수치는 학습용 추정값입니다. 사이트(JFL1 · TCP 9000)와 `jetson/` 교재(IQ01 · TCP 5000)의 코드는 섞지 않습니다.
