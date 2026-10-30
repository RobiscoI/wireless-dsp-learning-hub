"""심화 CPU 실습: 상태 유지 FIR, ULA MUSIC, unitary FFT covariance 불변성.
NumPy 필요. 네트워크 서버의 기능이 아닌 독립 수치 실험이다.
"""
import json
import numpy as np


def fir_stream(x, h, block_size):
    """블록 경계마다 과거 L-1개 샘플을 넘겨 연속 필터와 같은 출력을 만든다."""
    state = np.zeros(len(h)-1, dtype=complex)
    outputs = []
    for start in range(0,len(x),block_size):
        block = x[start:start+block_size]
        extended = np.concatenate((state,block))
        # valid convolution 길이는 block 길이와 같다.
        outputs.append(np.convolve(extended,h,mode="valid"))
        state = extended[-(len(h)-1):].copy()
    return np.concatenate(outputs)


def steering(m, angle_deg):
    # ULA, d/lambda=0.5, broadside 기준; 수신모델 x=a(theta)s+noise.
    return np.exp(1j*np.pi*np.arange(m)[:,None]*np.sin(np.deg2rad(angle_deg)))


def main():
    rng = np.random.RandomState(42) # 오래된 Jetson NumPy와 호환
    fs, n = 48000, 2048
    t=np.arange(n)/fs
    x=np.exp(2j*np.pi*3000*t)+.5*np.exp(2j*np.pi*12000*t)
    length, cutoff = 65, 6000
    k=np.arange(length)-(length-1)/2
    h=(2*cutoff/fs)*np.sinc(2*cutoff/fs*k)*np.hamming(length)
    h/=h.sum()
    actual=fir_stream(x,h,127) # FFT 길이와 다른 블록으로 경계 검증
    expected=np.convolve(x,h)[:n]
    fir_error=float(np.max(np.abs(actual-expected)))
    assert fir_error<1e-12

    m, snapshots, sources = 8, 4096, 2
    truth=np.array([-20.,30.])
    a=steering(m,truth)
    s=(rng.randn(sources,snapshots)+1j*rng.randn(sources,snapshots))/np.sqrt(2)
    noise=(rng.randn(m,snapshots)+1j*rng.randn(m,snapshots))/np.sqrt(2)
    iq=a.dot(s)+.1*noise # 소스별/센서 기준 신호전력1, noise전력0.01
    covariance=iq.dot(iq.conj().T)/snapshots
    values,vectors=np.linalg.eigh(covariance) # 고유값 오름차순
    en=vectors[:,:m-sources]
    angles=np.linspace(-90,90,1801)
    denom=np.sum(np.abs(en.conj().T.dot(steering(m,angles)))**2,axis=0)
    spectrum=1/np.maximum(denom,1e-15)
    candidates=np.where((spectrum[1:-1]>spectrum[:-2]) &
                        (spectrum[1:-1]>spectrum[2:]))[0]+1
    chosen=[]
    for idx in candidates[np.argsort(spectrum[candidates])[::-1]]:
        if all(abs(angles[idx]-angles[old])>=2 for old in chosen):
            chosen.append(idx)
        if len(chosen)==sources: break
    doa=np.sort(angles[chosen])
    assert len(doa)==sources and np.max(abs(doa-truth))<=.3
    # 전 bin을 유지한 unitary FFT는 R을 바꾸지 않는다.
    transformed=np.fft.fft(iq,axis=1)/np.sqrt(snapshots)
    rf=transformed.dot(transformed.conj().T)/snapshots
    covariance_error=float(np.linalg.norm(rf-covariance)/np.linalg.norm(covariance))
    assert covariance_error<1e-12
    report={"fir_max_error":fir_error,"fir_delay_samples":32,
            "music_true_deg":truth.tolist(),"music_estimated_deg":doa.tolist(),
            "music_eigenvalues":values.tolist(),"fft_covariance_relative_error":covariance_error,
            "assumptions":"ULA half wavelength, independent sources, known K=2, white noise"}
    print(json.dumps(report,indent=2))


if __name__=="__main__":
    main()
