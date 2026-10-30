# 04. 전체 코드의 흐름과 최초 실행

> 저장소 반영 (2026-10-30): 이 교재와 코드는 저장소의 `jetson/` 폴더에 있습니다. 교재의 명령은 모두 clone 한 저장소의 `jetson/` 폴더(`cd wireless-dsp-learning-hub/jetson`)에서 실행합니다.

## 1. 먼저 코드를 준비합니다

GitHub 저장소를 PC와 Jetson에 각각 clone합니다. PC 사본과 Jetson 사본은 독립적입니다. 같은 commit으로 맞춘 뒤 실행해야 비교가 의미 있습니다. 아래 명령은 clone 한 뒤 저장소의 `jetson/` 폴더로 이동해 실행합니다.

```bash
# PC Git Bash: 최초 한 번
git clone https://github.com/RobiscoI/wireless-dsp-learning-hub.git
cd wireless-dsp-learning-hub/jetson
git log -1 --oneline
```

```bash
# Jetson SSH 터미널: 최초 한 번
git clone https://github.com/RobiscoI/wireless-dsp-learning-hub.git
cd wireless-dsp-learning-hub/jetson
mkdir -p build
g++ -std=c++11 -O2 -Wall -Wextra labs/edge_dsp/cpp/server.cpp -o build/edge_server
```

`-std=c++11`은 문법 버전, `-O2`는 최적화, `-Wall -Wextra`는 경고, `-o`는 실행 파일 이름입니다. 컴파일 성공 시 보통 출력 없이 프롬프트로 돌아옵니다. 이 소스는 Linux POSIX 소켓을 사용하므로 Windows Git Bash에서 같은 g++ 명령이 곧바로 통하는 것은 아닙니다. Windows는 Python/MATLAB 클라이언트를 실행하고 서버는 Jetson 또는 Linux에 둡니다.

## 2. 먼저 Jetson 내부 통신으로 확인

Jetson SSH 창 A에서 서버를 켭니다. 이 창은 계속 실행 중인 상태로 두세요.

```bash
./build/edge_server 127.0.0.1 5000
```

`Listening 127.0.0.1:5000`이 나오면 Jetson SSH 창 B를 새로 열고 다음을 실행합니다.

```bash
cd ~/wireless-dsp-learning-hub/jetson
python3 labs/edge_dsp/python/client.py --host 127.0.0.1
```

예상값은 channel0 peak=3000 Hz, amplitude≈1, power≈1; channel1 peak=-6000 Hz, amplitude≈0.5, power≈0.25입니다. 마지막에 `PASS: frequency, amplitude, power, Parseval`이 나옵니다. 처리시간은 장비마다 다르므로 정답 숫자로 고정하지 않습니다. `output/edge-dsp/result.json`과 `psd.csv`가 생성됩니다.

이 순서가 필요한 이유는 네트워크 케이블/IP 문제가 들어오기 전에 컴파일·메모리·수식을 먼저 분리하기 위해서입니다. 내부 시험을 통과한 뒤 서버 창에서 Ctrl+C로 종료합니다.

## 3. PC→Jetson LAN 실행

```bash
# Jetson 창 A: 실제 LAN IP로 바꿔 실행
./build/edge_server 192.168.0.50 5000
```

```bash
# PC Git Bash, 저장소의 jetson 폴더: Windows Python launcher가 있는 경우
py -3 labs/edge_dsp/python/client.py --host 192.168.0.50
# py가 없고 python 명령이 설정되어 있으면 아래 명령 사용
# python labs/edge_dsp/python/client.py --host 192.168.0.50
```

클라이언트는 서버가 뜬 뒤 실행합니다. Python 스크립트에 컴파일 단계는 없습니다. Linux의 `python3`, Windows의 `py -3` 또는 `python`은 동일한 `.py` 파일을 실행합니다.

## 4. MATLAB에서 같은 실험 실행

MATLAB Current Folder를 clone한 저장소의 `jetson` 폴더로 바꾸고 Command Window에서 실행합니다.

> MATLAB 릴리스 주의: 아래 `run_edge_client.m`은 R2020b 이후의 `tcpclient`(`ByteOrder` 속성, `write(t,data,type)`)를 사용합니다. R2018a의 `tcpclient`에는 `Address·Port·Timeout·BytesAvailable·ConnectTimeout` 속성만 있어 이 함수가 그대로는 동작하지 않습니다(2026-10-30, R2018a에서 속성 목록 확인). 이전 릴리스에서는 Python 클라이언트로 진행하세요.

```matlab
version
ver
which tcpclient
addpath('labs/edge_dsp/matlab');
result = run_edge_client('192.168.0.50',5000);
```

`tcpclient`는 PC가 서버에 접속하는 객체입니다. 서버는 C++가 담당하므로 MATLAB 서버 기능이나 Simulink가 필요하지 않습니다. 이 예제는 기본 MATLAB 함수 경로를 대상으로 작성했으며 실제 설치 릴리스에서 `which tcpclient`로 확인합니다. MATLAB 미설치 시 Python 경로만으로 첫 프로젝트를 완료할 수 있습니다.

그래프에서 MATLAB 실선과 Jetson 점선이 겹쳐야 합니다. `output/edge-dsp-matlab/comparison.png`와 `result.mat`를 확인합니다. MATLAB의 기준 계산도 전송된 float32 IQ를 다시 double로 바꿔 사용하므로 입력 양자화와 FFT 계산 오차를 분리합니다. 새 `.m` 코드는 본 작성 환경에서 MATLAB 실행 검증을 하지 않았습니다.

## 5. C++ 전체 프로그램을 읽는 순서

전체 파일: [server.cpp](../../labs/edge_dsp/cpp/server.cpp)

| 함수/구간 | 들어오는 것 | 하는 일 | 확인할 점 |
|---|---|---|---|
| main 초기화 | IPv4, port | socket→bind→listen | 어디에서 접속을 받는가 |
| accept | 접속 요청 | 연결마다 client fd 생성 | listener와 client socket은 다름 |
| read_exact | 필요한 byte 수 | 여러 recv를 합침 | TCP 경계가 곧 프레임 경계가 아님 |
| u32le/f32le | 4바이트 | 정수/float 복원 | 숫자 변환과 비트 재해석의 차이 |
| process | M,N,Fs,IQ | 채널별 FFT·PSD·통계 | offset과 정규화 분모 |
| fft | N개 complex<double> | bit reversal와 butterfly | 길이 2의 거듭제곱, 음의 지수 |
| write_all | length+JSON | 부분 송신을 이어 보냄 | send 반환 길이 확인 |
| Socket 소멸자 | fd | close | 정상/예외에서 자원 반환 |

FFT의 butterfly는 두 길이 L/2 결과를 회전인자 W로 결합합니다. `u+v`, `u-v`로 짝을 만들며 L=2→4→8…N으로 커집니다. 데이터 정렬을 먼저 bit reversal로 바꾸면 이 작은 결합을 제자리에서 수행할 수 있습니다. 이 구현의 목적은 수식을 따라갈 수 있는 CPU 기준선입니다. FFTW보다 빠르다는 주장은 하지 않습니다.

## 6. 클라이언트 전체 코드 읽기

[client.py](../../labs/edge_dsp/python/client.py)의 `make_frame`은 숫자를 바이트로 직렬화하고, `exchange`는 전송과 길이 기반 응답 수신을 담당하며, `main`은 신호 생성과 기대값 검증을 담당합니다. 이 세 역할을 나누면 나중에 합성 신호 대신 파일 IQ를 넣어도 TCP 코드를 고칠 필요가 없습니다.

[run_edge_client.m](../../labs/edge_dsp/matlab/run_edge_client.m)은 같은 헤더를 `uint32`, IQ를 `single`로 보냅니다. `ByteOrder='little-endian'`은 다바이트 값의 전송 순서를 정합니다. `read(t,L,'uint8')`의 L은 JSON의 문자 개수가 아니라 바이트 개수입니다.

Notion의 해당 장에는 위 세 파일의 전체 코드가 함께 수록되어 있습니다. GitHub 파일이 수정되면 Notion 복사본과 차이가 생길 수 있으므로 파일 링크와 commit을 기준으로 버전을 확인합니다.

## 7. 수정 후 다시 실행하는 순서

1. C++ 파일을 바꿨다면 서버를 Ctrl+C로 종료합니다.
2. 위 g++ 명령으로 다시 빌드합니다. 오류가 나면 이전 실행 파일로 시험하지 않습니다.
3. 새 서버를 시작하고 클라이언트를 다시 실행합니다.
4. PC에서 수정하고 push했다면 Jetson에서 `git pull --ff-only` 후 빌드합니다.
5. Python/MATLAB 수정은 파일 저장 후 새 실행으로 반영합니다. 기존 프로세스가 자동 교체되지는 않습니다.

다음 장의 자동 시험을 통과한 다음에만 본인 Jetson에서 검증 완료라고 기록합니다.
