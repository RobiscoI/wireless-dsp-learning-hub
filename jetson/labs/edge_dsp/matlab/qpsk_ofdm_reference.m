function report = qpsk_ofdm_reference()
% 교육용 QPSK/OFDM 기준선. NR 표준 모뎀이 아니며 추가 Toolbox가 필요 없습니다.
% 난수 BER는 고정 숫자와 일치시키지 않고 오류 수, 비트 수, 통계 범위를 읽습니다.
rng(42); Nbits=200000; ebn0dB=0:2:8;
bits=randi([0 1],2,Nbits/2);
s=((1-2*bits(1,:))+1j*(1-2*bits(2,:)))/sqrt(2);
errors=zeros(size(ebn0dB)); ber=errors;
for idx=1:numel(ebn0dB)
    gamma=10^(ebn0dB(idx)/10); N0=1/(2*gamma);
    noise=sqrt(N0/2)*(randn(size(s))+1j*randn(size(s)));
    r=s+noise;
    decoded=[real(r)<0;imag(r)<0];
    errors(idx)=sum(decoded(:)~=bits(:)); ber(idx)=errors(idx)/Nbits;
end
theory=0.5*erfc(sqrt(10.^(ebn0dB/10)));
% OFDM은 무잡음·정확한 동기·정수 지연 FIR부터 검증합니다.
Nfft=64; Ncp=16; Nsym=100;
b=randi([0 1],2,Nfft*Nsym);
symbols=reshape(((1-2*b(1,:))+1j*(1-2*b(2,:)))/sqrt(2),Nfft,Nsym);
time=ifft(symbols,[],1)*sqrt(Nfft); % unitary IFFT
withCP=[time(end-Ncp+1:end,:);time];
h=[1;0;0.3*exp(1j*0.4)]; % 최대 지연 2 samples, CP16이 충분
rx=filter(h,1,withCP(:));
frames=reshape(rx,Nfft+Ncp,Nsym);
Y=fft(frames(Ncp+1:end,:),[],1)/sqrt(Nfft);
H=fft(h,Nfft);
estimated=bsxfun(@rdivide,Y,H); % 완전히 알려진 채널、ZF
evm=sqrt(mean(abs(estimated(:)-symbols(:)).^2)/mean(abs(symbols(:)).^2));
assert(evm<1e-12,'Noiseless OFDM baseline failed');
report=struct('EbN0dB',ebn0dB,'errors',errors,'bitsPerPoint',Nbits,...
    'ber',ber,'theory',theory,'ofdmEvm',evm,'seed',42);
disp(report);
figure; semilogy(ebn0dB,theory,'-',ebn0dB,max(ber,1/Nbits),'o');
grid on; xlabel('Eb/N0 (dB)'); ylabel('BER'); legend('Theory','Simulation');
end
