function result = run_edge_client(host, port)
% MATLAB 기본 함수 + tcpclient. 서버는 Jetson/Linux에서 먼저 실행합니다.
% 전체 실행: addpath('labs/edge_dsp/matlab'); run_edge_client('192.168.0.50',5000)
% host는 예시 주소가 아닌 실제 Jetson IP로 바꾸세요.
if nargin < 1, host = '127.0.0.1'; end
if nargin < 2, port = 5000; end
fs = 48000; N = 2048; M = 2; seq = 1;
n = 0:N-1;
x = [exp(1j*2*pi*3000*n/fs); 0.5*exp(-1j*2*pi*6000*n/fs)];
% MATLAB은 column-major: 2M x N 배열을 펴면 한 시점의 전 채널이 먼저 나옵니다.
iq = zeros(2*M,N,'single');
iq(1:2:end,:) = single(real(x));
iq(2:2:end,:) = single(imag(x));
t = tcpclient(host,port,'Timeout',10);
t.ByteOrder = 'little-endian';
tic;
write(t,uint8('IQ01'),'uint8');
write(t,uint32([seq M N fs 8*M*N]),'uint32');
write(t,iq(:),'single');
% read(count,type)는 해당 개수 또는 timeout까지 기다립니다. 반환 길이도 확인합니다.
L = read(t,1,'uint32');
assert(numel(L)==1 && L>0 && L<=16*1024*1024,'Invalid response length');
raw = read(t,double(L),'uint8');
assert(numel(raw)==double(L),'Truncated response');
result = jsondecode(native2unicode(raw(:).','UTF-8'));
result.roundtrip_ms = toc*1000;
clear t; % 정상/오류 종료 시 함수 범위의 객체를 해제합니다.
assert(result.seq==seq && result.channels==M && result.n==N && result.fs_hz==fs);
% 비교 기준도 wire float32로 양자화된 IQ를 사용합니다.
xref = double(iq(1:2:end,:))+1j*double(iq(2:2:end,:));
X = fft(xref,[],2);
psd = abs(X).^2/(fs*N); % 직사각 창, 양측 PSD; 단위: 정규화 전력/Hz
f = (-N/2:N/2-1)*fs/N;
figure('Name','PC MATLAB vs Edge CPU');
expectedFreq = [3000 -6000]; expectedAmp = [1 0.5];
for ch=1:M
    remote = result.results(ch);
    remotePsd = double(remote.psd(:).');
    assert(numel(remotePsd)==N);
    assert(max(abs(remotePsd-psd(ch,:)))<1e-8,'PSD mismatch');
    assert(abs(remote.peak_hz-expectedFreq(ch))<1e-8);
    assert(abs(remote.peak_amplitude-expectedAmp(ch))<1e-5);
    assert(abs(remote.psd_integral-remote.mean_power)<1e-8);
    subplot(M,1,ch);
    plot(f,10*log10(max(fftshift(psd(ch,:)),1e-15)),'-'); hold on;
    plot(f,10*log10(max(fftshift(remotePsd),1e-15)),'--');
    xlabel('Frequency (Hz)'); ylabel('PSD (dB/Hz, normalized)'); grid on;
    legend('MATLAB','Edge CPU'); title(sprintf('Channel %d',ch-1));
end
out = fullfile('output','edge-dsp-matlab');
if ~exist(out,'dir'), mkdir(out); end
save(fullfile(out,'result.mat'),'result','xref','psd','f');
saveas(gcf,fullfile(out,'comparison.png'));
fprintf('PASS: PSD / frequency / amplitude / power. RTT %.3f ms\n',result.roundtrip_ms);
end
