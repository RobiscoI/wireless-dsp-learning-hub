# MATLAB 신호처리 트랙 — 24주 · 72세션

FFT·PSD·필터 → QPSK·OFDM → Beamforming·NR → Ray Tracing·ISAC 순서로 진행합니다. NTN은 22주차 참고입니다.
수업 설명과 학습 기록은 Notion의 [학습 세션](https://app.notion.com/p/3e12eac098bd81dfbcd2db4579c90d17)과
[24주 로드맵](https://app.notion.com/p/3e12eac098bd81f2bfb0f5a62068a05e)이 기준이고, 이 폴더에는 실행 코드를 둡니다.

```
matlab/
├── README.md          이 문서
├── setup_path.m       MATLAB 세션마다 한 번 — 구 릴리스용 대체 함수 연결
├── compat/            exportgraphics · tiledlayout/nexttile · yline · jsonencode(PrettyPrint) 대체 함수
├── kit/               (git 제외) Notion 실습 ZIP 압축 해제 위치 — 원본, 수정하지 않음
└── sessions/          내가 수정·작성한 세션 코드 (W01-S1 …) — sessions/README.md
```

## 1. 처음 한 번: 실습 키트 받기

1. Notion 허브 → 다운로드 → **MATLAB 실행 파일과 검증 예시** (`MATLAB_Wireless_24Week_Workbook_Kit.zip`)를 받습니다.
2. 이 폴더의 `kit/`에 압축을 풉니다. `matlab/kit/practice/W01-S1/`이 생기면 맞습니다.
3. `kit/`은 git에서 제외됩니다. 원본 PDF·패키지는 이 공개 저장소에 올리지 않습니다.

```
kit/
├── README_FIRST_KO.txt        키트 안내
├── pdf/                       100쪽 개정 워크북
├── practice/W01-S1 … W24-S1   세션별 실행 코드 (W01~W03 상세 수업, 각 주차 미니 실습)
├── lessons/                   상세 수업 9개 원고와 개념 그림
├── matlab/                    기준선 데모 (DSP · beamforming · 교육 OFDM · 합성 경로 · 이상 ISAC)
├── curriculum/                72세션 계획 · 주차 카드
└── example_results/           R2025b 실행 결과 예시 — 본인 결과와 구분
```

## 2. 매 MATLAB 세션: 경로 준비

```matlab
addpath('C:\Users\<사용자>\Desktop\Project\wireless-dsp-learning-hub\matlab');   % 각 PC의 clone 위치로
setup_path
```

수업은 MATLAB R2025b 기준입니다. `setup_path`는 지금 릴리스에 **없는** 함수만 `compat/`의 대체 함수로 채우고,
이미 있는 함수는 건드리지 않습니다. R2025b에서는 아무것도 추가하지 않습니다.

## 3. 수업 실행

Notion 수업의 `cd('C:\Users\USER\Desktop\MATLAB_DSP\practice\W01-S1')`는 자료를 만든 PC의 경로입니다. 이 저장소에서는:

```matlab
repo = fileparts(fileparts(which('setup_path')));   % setup_path 를 addpath 한 저장소
cd(fullfile(repo, 'matlab', 'kit', 'practice', 'W01-S1'));
which run_checks -all
validation = run_checks();
```

결과(`results/`)는 세션 폴더 안에 생깁니다. 변수를 바꿔 비교하는 실험은 원본 대신 `sessions/`에 복사한 사본에서 합니다.

## 4. MATLAB 릴리스 호환 (2026-10-30 실측)

작업 PC의 **MATLAB R2018a**에서 키트를 실제로 실행한 결과입니다.
설치 제품: MATLAB 9.4, Signal Processing 8.0, Communications System 6.6, DSP System 9.6,
Phased Array System 3.6, Simulink 9.1, MATLAB Coder 4.0 (5G·Antenna Toolbox 없음).

| 대상 | `setup_path` 없이 | `setup_path` 후 | 원인 |
|---|---|---|---|
| 미니 실습 W01~W24 | 24/24 통과 | 24/24 통과 | 기본 함수만 사용 |
| W01-S2 · W01-S3 · W02-S1 · W02-S2 | 통과 | 통과 | |
| **W01-S1** `run_checks` | 실패 | **통과** | `jsonencode(...,'PrettyPrint')` — R2021a+ |
| W03-S1 `W03_S1_qpsk` · W03-S2 `W03_S2_confidence` | 실패 | **통과** | `exportgraphics` — R2020a+ |
| W03-S3 `W03_S3_sweep` · `W03_S3_compare` | 실패 | **통과** | `tiledlayout`/`nexttile` — R2019b+, `yline` — R2018b+ |
| W02-S3 `W02_S3_gui` | — | 미실행 | GUI(`uifigure`) 그림 저장은 구 릴리스 `print`가 지원하지 않음 |
| 기준선 `kit/matlab/` 5개 | 4개 실패 | 4개 통과, `ofdm_link_demo` 실패 | `sum(x,'all')` — R2018b+, 대체 함수 없음 |

대체 함수와 실제 함수의 차이:

- `exportgraphics(ax, ...)` — 축만이 아니라 그 축이 있는 그림 전체를 저장합니다. `Resolution` 외의 옵션은 무시합니다.
- `jsonencode` — `PrettyPrint`를 빼고 내장 함수로 넘깁니다. JSON 내용은 같고 들여쓰기만 없습니다.
- `tiledlayout(m,n)` / `nexttile` — `subplot`으로 배치합니다. 칸 병합(`nexttile([r c])`)과 `title(t,...)`은 없습니다.
- `yline` — 호출 시점의 x 범위에 가로선을 그리고 그 범위를 고정합니다.
- `sum(x,'all')`이 필요한 코드는 사본에서 `sum(x(:))`로 바꿉니다.

R2025b가 설치된 PC에서는 `setup_path`가 아무것도 바꾸지 않으므로 Notion의 기준값과 그대로 비교할 수 있습니다.

## 5. 저장소 규칙

- 공개 저장소입니다. `kit/`(원본), 실행 결과(`results*/`, `comparisons/`, `*.mat`), 개인 학습 기록은 올리지 않습니다.
- 올리는 것: 내가 수정·작성한 `.m` 코드(`sessions/`), 이 트랙의 도구(`setup_path.m`, `compat/`).
- 학습 기록(관측값·실패 원인·질문)은 Notion 세션 페이지의 「학습 기록」에 적습니다.
- PC·Jetson 연동(MATLAB `tcpclient` 클라이언트, QPSK·OFDM 기준 예제)은 [`../jetson/`](../jetson/) 트랙에 있습니다.
