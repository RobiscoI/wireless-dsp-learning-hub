# PC·Jetson Edge DSP 트랙 — 교재 00~10장

PC가 만든 복소 IQ를 LAN(TCP)으로 Jetson Nano 2GB에 보내고, Jetson CPU의 C++ FFT·PSD 결과를 PC에서 정답과 비교합니다.
이후 상태 FIR·MUSIC·스트리밍·CPU/GPU 설계로 확장합니다. 교재 본문은 Notion 허브의 「Jetson 실습 교재」가 기준이고,
`docs/edge-dsp/`는 같은 원고의 저장소 사본입니다.

**모든 명령은 이 `jetson/` 폴더에서 실행합니다** (`cd wireless-dsp-learning-hub/jetson`).
교재에 나오는 `labs/edge_dsp/...`, `build/`, `output/` 경로는 모두 이 폴더 기준입니다.

## 교재

- 1단계 흐름·환경: [00 시작 안내](docs/edge-dsp/00-start-here.md) · [01 PC·Jetson·LAN 설치](docs/edge-dsp/01-system-setup.md) · [02 IQ·FFT·PSD](docs/edge-dsp/02-iq-fft-psd.md)
- 2단계 구현·검증: [03 IQ 프로토콜](docs/edge-dsp/03-protocol.md) · [04 빌드·실행](docs/edge-dsp/04-build-run-code.md) · [05 검증·디버깅](docs/edge-dsp/05-validation-debug.md) · [06 Git·GitHub](docs/edge-dsp/06-git-github.md)
- 3단계 심화: [07 FIR·공분산·MUSIC](docs/edge-dsp/07-advanced-dsp.md) · [08 스트리밍·성능](docs/edge-dsp/08-streaming-performance.md) · [09 24주 과정 연결](docs/edge-dsp/09-wireless-roadmap.md) · [10 프로젝트 지침](docs/edge-dsp/10-project-rules-sources.md)
- [실행 검증 기록](docs/edge-dsp/verification.md) · [Notion 학습 허브](https://app.notion.com/p/3e12eac098bd81569f76efed94daf130)

## 폴더

| 경로 | 내용 | 실행 위치 |
|---|---|---|
| `labs/edge_dsp/cpp/server.cpp` | IQ01 TCP 서버, CPU FFT·PSD (C++11, Linux POSIX 소켓) | Jetson · Linux |
| `labs/edge_dsp/python/client.py` | IQ 생성·전송·결과 검증 (Python 3.6+ 표준 라이브러리) | PC · Jetson |
| `labs/edge_dsp/python/advanced_dsp.py` | 상태 FIR · MUSIC · FFT 공분산 (NumPy) | PC · Jetson |
| `labs/edge_dsp/python/make_figures.py` | 교재 그림 재생성 (NumPy, Matplotlib 2.2+) | PC |
| `labs/edge_dsp/matlab/run_edge_client.m` | MATLAB 클라이언트 (`tcpclient`, R2020b+) | PC |
| `labs/edge_dsp/matlab/qpsk_ofdm_reference.m` | QPSK·AWGN·OFDM 기준 예제 (네트워크 불필요) | PC |
| `labs/edge_dsp/tests/test_transport.py` | 서버 통합시험 6개 (`unittest`) | Linux · Jetson |
| `build/`, `output/` | 빌드 산출물 · 실행 결과 (git 제외) | |

## 빠른 실행 — Jetson 내부 통신

```bash
cd ~/wireless-dsp-learning-hub/jetson
mkdir -p build
g++ -std=c++11 -O2 -Wall -Wextra labs/edge_dsp/cpp/server.cpp -o build/edge_server
./build/edge_server 127.0.0.1 5000
```

다른 터미널에서:

```bash
cd ~/wireless-dsp-learning-hub/jetson
python3 labs/edge_dsp/python/client.py --host 127.0.0.1
```

마지막 줄이 `PASS: frequency, amplitude, power, Parseval`이면 통과입니다. PC↔Jetson은 서버 bind 주소와 `--host`를
Jetson의 LAN IPv4로 바꿉니다 (04장). Windows에서는 Python 클라이언트를 실행하고 C++ 서버는 Linux·Jetson에서 빌드합니다.

## 실행 환경과 확인 범위

| 환경 | 상태 |
|---|---|
| Jetson Nano 2GB, JetPack 4.6.x (Ubuntu 18.04) | 2026-10-30 부팅 복구·첫 설정 완료. 이 코드의 빌드·실행은 아직 |
| Ubuntu 18.04 Python 3.6.9 (WSL2 — JetPack 4와 같은 배포판) | 2026-10-30 Python 파일 4개 구문 검사 통과, `client.make_frame` 실행 확인. g++ 미설치라 C++ 빌드·통합시험은 미실행 |
| Linux x86_64, g++ 13.3, Python 3.12 | 2026-10-04 통합시험 6개 · FIR/MUSIC 통과 ([verification.md](docs/edge-dsp/verification.md)) |
| MATLAB R2018a (작업 PC) | `qpsk_ofdm_reference.m` 통과. `run_edge_client.m`은 R2018a `tcpclient`에 `ByteOrder` 속성이 없어 그대로는 동작하지 않음 → Python 클라이언트 사용 |

Jetson 준비 메모 (Ubuntu 18.04 apt 후보 버전, 2026-10-30 확인):

- `g++` 7.4 · `cmake` 3.10.2 — 서버는 C++11만 쓰므로 g++ 7로 충분합니다.
- `python3-numpy` 1.13.3 — `advanced_dsp.py`에 필요. 코드가 오래된 NumPy용 `np.random.RandomState`를 씁니다.
- `python3-matplotlib` 2.1.1 — `make_figures.py`의 `constrained_layout`(2.2+)이 없어 그림 재생성은 PC에서 합니다.

## Jetson Flow Lab과 코드를 섞지 않기

웹 실습실은 JFL1 20바이트 헤더 · TCP 9000 · 8192 Hz, 이 교재는 IQ01 24바이트 헤더 · TCP 5000 · 첫 실습 48000 Hz입니다.
사이트 계산기 설정이 이 폴더의 프로그램 인수를 바꾸지 않습니다.
