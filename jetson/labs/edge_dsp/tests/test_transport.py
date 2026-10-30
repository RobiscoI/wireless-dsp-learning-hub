"""Linux에서 실제 C++ 서버를 구동해 통신/수치 경계를 검증한다. NumPy 불필요."""
import cmath
import json
import math
import os
from pathlib import Path
import random
import socket
import struct
import subprocess
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "labs/edge_dsp/python"))
from client import exchange, make_frame, recv_exact


class Integration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # OS에 빈 포트를 요청; readiness 확인은 연결 성공으로 판단한다.
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            cls.port = probe.getsockname()[1]
        exe = os.environ.get("EDGE_SERVER", str(ROOT / "build/edge_server"))
        cls.proc = subprocess.Popen([exe, "127.0.0.1", str(cls.port)],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if cls.proc.poll() is not None:
                raise RuntimeError("server exited before readiness")
            try:
                with socket.create_connection(("127.0.0.1", cls.port), timeout=.1):
                    return
            except OSError:
                time.sleep(.02)
        cls.proc.terminate()
        cls.proc.wait(timeout=5)
        raise RuntimeError("server start timeout")

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        cls.proc.wait(timeout=5)

    def connect(self):
        return socket.create_connection(("127.0.0.1", self.port), timeout=10)

    def test_signed_tones_and_persistent_connection(self):
        n, fs = 2048, 48000
        tones = [(3000, 1), (-6000, .5)]
        x = [[a*cmath.exp(2j*math.pi*f*k/fs) for k in range(n)] for f,a in tones]
        with self.connect() as s:
            for seq in (1,2):
                r = exchange(s, make_frame(x, fs, seq))
                self.assertEqual(r["seq"],seq)
                for row,(freq,amp) in zip(r["results"],tones):
                    self.assertAlmostEqual(row["peak_hz"],freq,places=8)
                    self.assertAlmostEqual(row["peak_amplitude"],amp,places=6)
                    self.assertAlmostEqual(row["mean_power"],amp**2,places=6)
                    self.assertAlmostEqual(sum(row["psd"])*fs/n,row["mean_power"],places=8)

    def test_fragmentation_and_independent_dft(self):
        # 작은 N에서 정의식 DFT와 비교. FFT와 같은 구현을 기대값으로 쓰지 않는다.
        rng=random.Random(42); n=32; fs=8000
        x=[[complex(rng.uniform(-1,1),rng.uniform(-1,1)) for _ in range(n)]]
        frame=make_frame(x,fs,7)
        packed=struct.unpack("<{}f".format(2*n),frame[24:])
        quantized=[complex(packed[2*k],packed[2*k+1]) for k in range(n)]
        expected=[abs(sum(quantized[t]*cmath.exp(-2j*math.pi*k*t/n)
                          for t in range(n)))**2/(fs*n) for k in range(n)]
        with self.connect() as s:
            for offset in range(0,len(frame),3):
                s.sendall(frame[offset:offset+3])
            count=struct.unpack("<I",recv_exact(s,4))[0]
            actual=json.loads(recv_exact(s,count).decode())["results"][0]["psd"]
        self.assertLess(max(abs(a-b) for a,b in zip(actual,expected)),1e-12)

    def test_coalesced_frames(self):
        x=[[1+0j]*8]
        with self.connect() as s:
            s.sendall(make_frame(x,8000,11)+make_frame(x,8000,12))
            for seq in (11,12):
                count=struct.unpack("<I",recv_exact(s,4))[0]
                r=json.loads(recv_exact(s,count).decode())
                self.assertEqual(r["seq"],seq)

    def assert_rejected(self, packet):
        with self.connect() as s:
            s.sendall(packet)
            s.shutdown(socket.SHUT_WR)
            try:
                self.assertEqual(s.recv(1),b"")
            except ConnectionResetError:
                pass
        # 불량 입력 이후에도 프로세스가 살아 있어야 한다.
        with self.connect() as s:
            self.assertEqual(exchange(s,make_frame([[0j]*8],8000))["seq"],1)

    def test_bad_header_lengths_and_nan(self):
        cases=[b"BAD!"+struct.pack("<5I",1,1,8,8000,64),
               struct.pack("<4s5I",b"IQ01",1,17,8,8000,1088),
               struct.pack("<4s5I",b"IQ01",1,1,9,8000,72),
               struct.pack("<4s5I",b"IQ01",1,1,8,0,64),
               struct.pack("<4s5I",b"IQ01",1,1,8,8000,63),
               make_frame([[complex(float('nan'),0)]*8],8000)]
        for packet in cases:
            with self.subTest(packet=packet[:24]): self.assert_rejected(packet)

    def test_truncation(self):
        packet=make_frame([[1j]*8],8000)
        for length in (3,24,30):
            with self.subTest(length=length): self.assert_rejected(packet[:length])

    def test_receive_timeout(self):
        with self.connect() as s:
            s.sendall(b"IQ")
            self.assertEqual(s.recv(1),b"")


if __name__ == "__main__":
    unittest.main(verbosity=2)
