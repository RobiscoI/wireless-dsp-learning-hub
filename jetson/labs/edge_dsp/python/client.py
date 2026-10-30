"""Python 3.6+ 표준 라이브러리: IQ 생성, TCP 전송, 결과 검증/저장.
서버는 Linux/Jetson에서 실행한다. 이 클라이언트는 Windows에서도 실행 가능하다.
"""
import argparse
import cmath
import csv
import json
import math
import os
import socket
import struct
import time


def recv_exact(sock, count):
    data = bytearray()
    while len(data) < count:
        part = sock.recv(count - len(data))
        if not part:
            raise EOFError("응답 도중 연결이 종료되었습니다")
        data.extend(part)
    return bytes(data)


def make_frame(samples, fs, seq=1):
    """samples[ch][n]을 sample-major I0,Q0,I1,Q1... byte 배열로 변환."""
    m, n = len(samples), len(samples[0])
    if any(len(row) != n for row in samples):
        raise ValueError("모든 채널의 snapshot 수가 같아야 합니다")
    flat = [v for k in range(n) for ch in range(m)
            for v in (samples[ch][k].real, samples[ch][k].imag)]
    payload = struct.pack("<{}f".format(len(flat)), *flat)
    return struct.pack("<4s5I", b"IQ01", seq, m, n, fs, len(payload)) + payload


def exchange(sock, frame):
    begin = time.perf_counter()
    sock.sendall(frame)
    length = struct.unpack("<I", recv_exact(sock, 4))[0]
    if length == 0 or length > 16 * 1024 * 1024:
        raise ValueError("응답 길이가 허용 범위를 벗어났습니다")
    result = json.loads(recv_exact(sock, length).decode("utf-8"))
    result["roundtrip_ms"] = (time.perf_counter() - begin) * 1000
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--output", default="output/edge-dsp")
    args = parser.parse_args()
    fs, n = 48000, 2048
    # FFT bin 128 -> 3000 Hz. 두 번째 채널은 음의 주파수와 진폭 scaling 검증.
    tones = [(3000, 1.0), (-6000, 0.5)]
    samples = [[amp * cmath.exp(2j * math.pi * freq * k / fs)
                for k in range(n)] for freq, amp in tones]
    with socket.create_connection((args.host, args.port), timeout=10) as sock:
        result = exchange(sock, make_frame(samples, fs))
    assert (result["seq"], result["channels"], result["n"], result["fs_hz"]) == (1, 2, n, fs)
    for row, (freq, amp) in zip(result["results"], tones):
        assert abs(row["peak_hz"] - freq) < 1e-8
        assert abs(row["peak_amplitude"] - amp) < 1e-5
        assert abs(row["mean_power"] - amp**2) < 1e-5
        assert abs(row["psd_integral"] - row["mean_power"]) < 1e-8
    os.makedirs(args.output, exist_ok=True)
    with open(os.path.join(args.output, "result.json"), "w") as f:
        json.dump(result, f, indent=2)
    with open(os.path.join(args.output, "psd.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["frequency_hz", "channel_0_power_per_hz", "channel_1_power_per_hz"])
        for k in range(n//2, n + n//2):
            index = k % n
            freq = (index if index < n//2 else index-n)*fs/n
            writer.writerow([freq] + [row["psd"][index] for row in result["results"]])
    compact = dict(result)
    compact["results"] = [{k: v for k, v in row.items() if k != "psd"}
                          for row in result["results"]]
    print(json.dumps(compact, indent=2))
    print("PASS: frequency, amplitude, power, Parseval")


if __name__ == "__main__":
    main()
