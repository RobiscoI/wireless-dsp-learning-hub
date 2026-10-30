# 10. 프로젝트 지침·오픈소스·설계 템플릿

## 1. 이 프로젝트의 운영 규칙

목표는 하나의 기능을 설계부터 검증과 전달까지 완성하는 것입니다. 기능 개수보다 왜 그 설정을 썼는지 설명할 수 있는지를 우선합니다. 문서는 처음 보는 사람이 입력·출력·실행 위치를 알 수 있게 쓰고, 코드는 모든 실행 파일의 전체 내용을 제공합니다.

1. 새 기능은 목적, 비목표, 입력/출력, 데이터 형식, 예제값, 허용차부터 작성합니다.
2. MATLAB/Python 수치 기준선을 만들고 CPU C++로 옮긴 다음 GPU 여부를 결정합니다.
3. 기본 실행은 추가 RF 보드 없이 가능합니다. SDR·FPGA·안테나 연결은 별도 확장으로 표시합니다.
4. 교육용 예제와 실제 NR/실측 채널/산업용 DF 검증을 구분합니다.
5. 시행한 시험만 '실행 검증'이라 쓰며, MATLAB/Jetson 미실행은 그대로 적습니다.
6. 날짜와 예상 소요시간은 일정 참고입니다. 다음 단계 진입은 완료 기준으로 결정합니다.
7. 기존 Notion 세션 ID와 학습 메모를 보존하고 원래 첨부 패키지와 새 코드를 구분합니다.
8. 공개 저장소에는 합성 입력·새 코드·설계서·작은 검증 요약을 넣습니다. 원본 첨부 ZIP/PDF는 재배포하지 않습니다.
9. 코드 변경은 Git diff와 시험 결과로 검토합니다. Notion 전체 코드 복사본은 GitHub와 자동 동기화되지 않습니다.

## 2. AI에게 작업을 맡길 때 붙여 넣는 지침

```text
이 프로젝트는 개인 학습용 MATLAB/Python/C++ 무선 DSP 실험이다.
사용 장비는 PC와 Jetson Nano 2GB이며 첫 실습은 추가 RF 보드 없이 LAN으로 진행한다.
먼저 현재 파일과 실험 명세를 읽고, 변경 목적과 입력/출력/단위/배열 크기를 정리하라.
실행 위치를 PC Git Bash / Jetson SSH / MATLAB Command Window로 구분하라.
수식의 정규화, IQ ordering, endian, 좌표계, 난수 seed를 명시하라.
코드를 작성하면 주석을 포함한 전체 실행 파일과 정확한 실행 명령을 제공하라.
정상 입력뿐 아니라 잘못된 길이, 연결 종료, 상태 초기화 같은 실패도 검증하라.
수치 기준선을 통과하기 전에 성능 최적화나 라이브러리 교체를 섞지 말라.
실행한 환경과 실행하지 못한 환경을 나누고 실제 측정하지 않은 성능을 추정값으로 포장하지 말라.
Notion 기존 학습 기록과 첨부물은 보존하라.
새 소스와 교재의 기준 위치는 GitHub 저장소이며 commit과 결과를 함께 기록하라.
```

저장소의 `AGENTS.md`에는 위 원칙을 개발 도구가 읽기 쉬운 형태로 넣었습니다. 지침 파일 자체가 시험을 자동으로 실행하거나 정확도를 보장하지는 않습니다. 사람도 결과를 확인해야 합니다.

## 3. 실험 명세 예시

| 항목 | 예시 |
|---|---|
| 실험 ID | EDSP-001 |
| 질문 | PC의 IQ와 Jetson의 FFT 결과가 같은가? |
| 입력 | 2×2048 complex, Fs=48000 Hz, +3kHz A1/-6kHz A0.5 |
| 전달 형식 | IQ01, sample-major, little-endian float32 |
| 알고리즘 | rectangular window, unnormalized forward FFT |
| 기대값 | peak 3000/-6000 Hz, power 1/0.25 |
| 허용차 | amplitude/power 1e-5, Parseval 1e-8 |
| 실행 위치 | C++ Jetson, Python 또는 MATLAB PC |
| 로그 | commit, OS, compiler, parameters, JSON, stderr |
| 실패 시험 | header mismatch, truncation, NaN, timeout |
| 완료 조건 | 수치/통신시험 통과, 새 폴더에서 재실행 |

## 4. 오픈소스는 어디에 활용하나

| 프로젝트 | 역할 | 첫 적용 방법 | 주의할 경계 |
|---|---|---|---|
| Python | 실행·TCP·시험 자동화 | 표준 socket/struct/unittest | Nano Python 버전과 문법 호환 |
| NumPy | 배열·FFT·Hermitian eig 기준선 | 독립 심화 예제 | Jetson은 배포판 패키지부터 확인 |
| KISS FFT | 작은 C FFT 대체 후보 | 현재 FFT 함수와 입력/출력 비교 | 선택 commit의 LICENSE·정밀도 확인 |
| FFTW | CPU FFT 최적화 후보 | plan 재사용·배치 비교 | GPL/상용 라이선스 조건 확인 |
| GNU Radio | 신호 흐름을 블록으로 학습 | PC의 Signal Source→FFT/파일 흐름 | 실제 RF 입출력은 별도 장비 |
| Sionna | 통신/채널 연구 | 호환 PC/서버에서 경로·채널 산출 | Nano 최신 패키지 호환을 가정하지 않음 |
| Git | 소스/실험 이력 | branch/commit/tag | 빌드와 데이터 백업을 대신하지 않음 |

이번 C++ FFT는 외부 코드를 복사하지 않은 교육 구현이며 서버의 필수 외부 FFT 의존성은 없습니다. MATLAB은 오픈소스가 아니라 유료 상용 환경입니다. cuFFT 역시 NVIDIA 제공 라이브러리로 분류합니다. '무료 다운로드'와 '오픈소스'는 같은 말이 아닙니다.

서드파티 코드를 가져올 때에는 저장소 URL, commit/tag, 라이선스 파일, 저작권 고지, 변경 파일, 테스트 결과를 `THIRD_PARTY.md`에 적는 방식으로 관리합니다. 이 저장소 전체에 새 라이선스를 임의로 부여하지 않았습니다. 공개 저장소라는 사실만으로 자유로운 재배포 권한이 생기지는 않으므로 재사용 정책은 소유자가 결정합니다.

## 5. 읽어야 할 공식 자료와 목적

| 자료 | 읽을 부분 | 연결 과제 |
|---|---|---|
| [Nano 2GB User Guide](https://developer.nvidia.com/embedded/learn/jetson-nano-2gb-devkit-user-guide) | 전원·포트·headless | 내 보드의 연결도 그리기 |
| [Nano 시작 절차](https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-2gb-devkit) | microSD·최초 부팅 | 모델/버전/IP 기록 |
| [JetPack 4 EOL](https://forums.developer.nvidia.com/t/announcing-end-of-life-for-nvidia-jetpack-4-with-the-release-of-jetpack-4-6-6/314300) | Nano 지원 계열 | Orin 설치법과 구분 |
| [Python Socket HOWTO](https://docs.python.org/3/howto/sockets.html) | partial send/recv | read_exact의 필요성 설명 |
| [MATLAB tcpclient](https://www.mathworks.com/help/matlab/ref/tcpclient.html) | ByteOrder, Timeout | wire format과 객체 설정 연결 |
| [NumPy FFT](https://numpy.org/doc/stable/reference/generated/numpy.fft.fft.html) | sign/normalization | FFT 결과 scaling 확인 |
| [NumPy eigh](https://numpy.org/doc/stable/reference/generated/numpy.linalg.eigh.html) | Hermitian/정렬 | noise subspace 선택 |
| [GitHub Desktop](https://docs.github.com/en/desktop/making-changes-in-a-branch) | commit/push/branch | 같은 실험을 GUI로 기록 |
| [KISS FFT](https://github.com/mborgerding/kissfft) | README/LICENSE | CPU 기준 FFT 대체 검토 |
| [FFTW](https://www.fftw.org/) | API/라이선스 | batch와 plan 재사용 |
| [GNU Radio](https://github.com/gnuradio/gnuradio) | 설치·예제·라이선스 | PC에서 소프트웨어 신호 흐름 |
| [Sionna](https://github.com/NVlabs/sionna) | 요구사항·예제 | 서버 결과를 작은 데이터로 교환 |
| [NR PDSCH](https://www.mathworks.com/help/5g/ug/nr-pdsch-throughput.html) | 처리 체인·SNR·채널 | 교육 OFDM과 차이 작성 |
| [RayTracingChannel](https://www.mathworks.com/help/comm/ref/comm.raytracingchannel-system-object.html) | 경로·배열·정규화 | 경로 교환 포맷 정의 |
| [ISAC 예제](https://www.mathworks.com/help/5g/ug/integrated-sensing-and-communication-using-5g-waveform.html) | 표적·통신 KPI | sensing과 EVM 분리 |

자료 확인 기준일은 2026-10-04입니다. 최신 웹 문서는 설치된 MATLAB/JetPack 릴리스보다 새로울 수 있으므로 실제 실행 환경에서는 해당 릴리스 문서를 선택합니다.

## 6. 최종 제출 템플릿

문제와 목표 → 입력/출력 스펙 → 구조도 → 수식/가정 → 전체 소스 위치 → 설치/실행 → 정상시험 → 실패시험 → 수치·그림 → 성능 조건 → 한계 → 다음 실험 순으로 작성합니다. '동작한다' 대신 '어떤 입력에서 어떤 허용차를 통과했는가'를 적습니다.
