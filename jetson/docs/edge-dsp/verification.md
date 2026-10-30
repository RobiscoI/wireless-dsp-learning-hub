# 새 Edge DSP 코드 검증 기록

작성·실행일: 2026-10-04. 아래는 작성 환경에서 실제 실행한 결과입니다.

## 실행 환경

- Linux x86_64, kernel 6.18.44, glibc 2.39
- g++ 13.3.0, C++11, -O2 -Wall -Wextra -Werror
- Python 3.12.14, NumPy 2.3.5
- 네트워크: 동일 호스트의 TCP loopback

## 결과

| 시험 | 결과 |
|---|---|
| C++ 컴파일, 경고를 오류 처리 | 통과 |
| signed tone / persistent connection | 통과 |
| fragmented TCP / independent DFT | 통과 |
| coalesced two frames | 통과 |
| invalid headers / lengths / NaN | 통과 |
| truncated header / payload | 통과 |
| receive timeout | 통과 |
| unittest 합계 | 6 tests, OK |
| FIR streaming vs whole convolution 최대오차 | 3.3306690738754696e-16 |
| MUSIC 정답 / 추정 | [-20°,30°] / [-20°,30°] |
| unitary FFT 전후 covariance 상대오차 | 2.8452219289213545e-16 |

## 직접 실행한 명령

2026-10-04 실행 당시에는 저장소 루트 기준이었습니다. 2026-10-30 저장소 반영 이후에는 같은 명령을 `jetson/` 폴더에서 실행합니다.

```bash
mkdir -p build
g++ -std=c++11 -O2 -Wall -Wextra -Werror labs/edge_dsp/cpp/server.cpp -o build/edge_server
python3 -m unittest discover -s labs/edge_dsp/tests -v
python3 labs/edge_dsp/python/advanced_dsp.py
```

## 아직 확인하지 않은 범위

- Jetson Nano 2GB ARM64에서의 빌드·실행·메모리·온도·처리속도
- Windows Python 실행 및 PC↔Jetson 실제 LAN
- MATLAB run_edge_client와 qpsk_ofdm_reference 실행
- CUDA/GPU, 지속적인 실시간 입력, RF 하드웨어

이 결과는 Jetson 성능 측정이나 RF 수신 정확도의 근거가 아닙니다. 제시한 허용차는 합성 입력을 사용하는 소프트웨어 회귀 기준입니다. 사용자 장비에서 같은 시험을 수행하고 환경과 결과를 추가하세요.
