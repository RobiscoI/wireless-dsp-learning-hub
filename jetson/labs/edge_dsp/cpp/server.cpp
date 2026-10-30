// C++11 / Linux POSIX sockets. 교육용 CPU FFT 서버: 외부 FFT 라이브러리 불필요.
// Wire format은 docs/edge-dsp/03-protocol.md 참조. 구조체를 그대로 전송하지 않는다.
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <unistd.h>
#include <cerrno>
#include <cmath>
#include <complex>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <iomanip>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <vector>
#include <chrono>

struct Socket { // 범위를 벗어나면 소켓을 닫는다(RAII).
    int fd;
    explicit Socket(int value) : fd(value) {}
    ~Socket() { if (fd >= 0) ::close(fd); }
    Socket(const Socket&) = delete;
    Socket& operator=(const Socket&) = delete;
};
void require(bool ok, const char* why) { if (!ok) throw std::runtime_error(why); }
bool read_exact(int fd, unsigned char* dst, size_t n) {
    size_t done = 0;
    while (done < n) { // TCP recv 한 번이 한 프레임이라는 보장은 없다.
        ssize_t r = recv(fd, dst + done, n - done, 0);
        if (r < 0 && errno == EINTR) continue;
        if (r == 0 && done == 0) return false;
        require(r > 0, "receive timeout / truncated frame / socket error");
        done += static_cast<size_t>(r);
    }
    return true;
}
void write_all(int fd, const unsigned char* src, size_t n) {
    size_t done = 0;
    while (done < n) {
        ssize_t r = send(fd, src + done, n - done, MSG_NOSIGNAL);
        if (r < 0 && errno == EINTR) continue;
        require(r > 0, "send timeout / disconnected client");
        done += static_cast<size_t>(r);
    }
}
uint32_t u32le(const unsigned char* p) {
    return uint32_t(p[0]) | (uint32_t(p[1]) << 8) |
           (uint32_t(p[2]) << 16) | (uint32_t(p[3]) << 24);
}
float f32le(const unsigned char* p) {
    uint32_t bits = u32le(p); float value;
    std::memcpy(&value, &bits, sizeof(value)); // aliasing 위반 없이 비트 해석
    return value;
}
void fft(std::vector<std::complex<double> >& a) {
    const size_t n = a.size();
    // Bit reversal 후 radix-2 butterfly. 부호와 scaling은 MATLAB fft와 동일.
    for (size_t i = 1, j = 0; i < n; ++i) {
        size_t bit = n >> 1;
        for (; j & bit; bit >>= 1) j ^= bit;
        j ^= bit;
        if (i < j) std::swap(a[i], a[j]);
    }
    const double pi = std::acos(-1.0);
    for (size_t len = 2; len <= n; len <<= 1) {
        std::complex<double> step = std::polar(1.0, -2*pi/len);
        for (size_t i = 0; i < n; i += len) {
            std::complex<double> w(1, 0);
            for (size_t j = 0; j < len/2; ++j) {
                auto u = a[i+j]; auto v = a[i+j+len/2] * w;
                a[i+j] = u+v; a[i+j+len/2] = u-v; w *= step;
            }
        }
    }
}
std::string process(uint32_t seq, uint32_t m, uint32_t n, uint32_t fs,
                    const std::vector<unsigned char>& raw) {
    auto begin = std::chrono::steady_clock::now();
    std::ostringstream out; out << std::setprecision(12);
    out << "{\"seq\":" << seq << ",\"channels\":" << m
        << ",\"n\":" << n << ",\"fs_hz\":" << fs << ",\"results\":[";
    for (uint32_t ch = 0; ch < m; ++ch) {
        std::vector<std::complex<double> > x(n);
        double power = 0;
        for (uint32_t k = 0; k < n; ++k) {
            size_t offset = 8 * (size_t(k)*m + ch); // sample-major, I/Q interleaved
            double re = f32le(&raw[offset]), im = f32le(&raw[offset+4]);
            require(std::isfinite(re) && std::isfinite(im), "non-finite IQ");
            x[k] = {re, im}; power += std::norm(x[k])/n;
        }
        fft(x);
        size_t peak = 0; double integral = 0;
        for (size_t k = 0; k < n; ++k) {
            if (std::norm(x[k]) > std::norm(x[peak])) peak = k;
            integral += std::norm(x[k])/(double(n)*n);
        }
        // 출력 PSD는 unshifted 양측 값이며 복소 IQ에 2배를 적용하지 않는다.
        double freq = (peak < n/2 ? double(peak) : double(peak)-n)*fs/n;
        if (ch) out << ',';
        out << "{\"channel\":" << ch << ",\"peak_hz\":" << freq
            << ",\"peak_amplitude\":" << std::abs(x[peak])/n
            << ",\"mean_power\":" << power << ",\"psd_integral\":" << integral
            << ",\"psd\":[";
        for (size_t k = 0; k < n; ++k) {
            if (k) out << ',';
            out << std::norm(x[k])/(double(fs)*n);
        }
        out << "]}";
    }
    // FFT 단독 시간이 아니다: parsing, FFT, metrics, PSD JSON 작성까지 포함.
    double ms = std::chrono::duration<double, std::milli>(
        std::chrono::steady_clock::now()-begin).count();
    out << "],\"processing_ms\":" << ms << '}';
    return out.str();
}
int main(int argc, char** argv) {
    static_assert(sizeof(float) == 4 && std::numeric_limits<float>::is_iec559,
                  "IEEE754 binary32 required");
    try {
        const char* host = argc > 1 ? argv[1] : "127.0.0.1";
        std::string port_text = argc > 2 ? argv[2] : "5000";
        size_t end = 0; int port = std::stoi(port_text, &end);
        require(end == port_text.size() && port > 0 && port <= 65535, "invalid port");
        Socket listener(socket(AF_INET, SOCK_STREAM, 0));
        require(listener.fd >= 0, "socket failed");
        int one = 1;
        require(setsockopt(listener.fd, SOL_SOCKET, SO_REUSEADDR, &one, sizeof(one)) == 0,
                "setsockopt failed");
        sockaddr_in addr{}; addr.sin_family = AF_INET; addr.sin_port = htons(port);
        require(inet_pton(AF_INET, host, &addr.sin_addr) == 1, "IPv4 address required");
        require(bind(listener.fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) == 0,
                "bind failed: address/port unavailable");
        require(listen(listener.fd, 4) == 0, "listen failed");
        std::cout << "Listening " << host << ':' << port << std::endl;
        for (;;) {
            int fd = accept(listener.fd, nullptr, nullptr);
            if (fd < 0 && errno == EINTR) continue;
            require(fd >= 0, "accept failed"); Socket client(fd);
            timeval timeout{5, 0};
            require(setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout)) == 0,
                    "receive timeout setup failed");
            require(setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout)) == 0,
                    "send timeout setup failed");
            try {
                unsigned char h[24];
                while (read_exact(fd, h, sizeof(h))) {
                    require(std::memcmp(h, "IQ01", 4) == 0, "bad magic/version");
                    uint32_t seq=u32le(h+4), m=u32le(h+8), n=u32le(h+12);
                    uint32_t fs=u32le(h+16), bytes=u32le(h+20);
                    require(m>=1 && m<=16 && n>=8 && n<=16384 && (n&(n-1))==0,
                            "invalid channel count / FFT length");
                    require(fs>0 && fs<=10000000 && bytes==uint64_t(m)*n*8,
                            "invalid sample rate / payload size");
                    std::vector<unsigned char> raw(bytes);
                    require(read_exact(fd, raw.data(), raw.size()), "missing payload");
                    std::string response=process(seq,m,n,fs,raw);
                    uint32_t len=static_cast<uint32_t>(response.size());
                    unsigned char prefix[4];
                    for (int k=0;k<4;++k) prefix[k]=(len>>(8*k))&255;
                    write_all(fd,prefix,4);
                    write_all(fd,reinterpret_cast<const unsigned char*>(response.data()),len);
                    std::cerr << "seq=" << seq << " M=" << m << " N=" << n
                              << " input_bytes=" << bytes << " status=ok\n";
                }
            } catch (const std::exception& e) { // 불량 연결만 닫고 다음 연결을 받는다.
                std::cerr << "status=rejected reason=" << e.what() << '\n';
            }
        }
    } catch (const std::exception& e) { std::cerr << e.what() << '\n'; return 1; }
}
