"""교재의 정확한 수치 그림을 재생성. 선택 의존성: NumPy, Matplotlib."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parents[3] / "docs/edge-dsp/assets"
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.size":11,"axes.spines.top":False,"axes.spines.right":False})
fs,n=48000,2048
t=np.arange(n)/fs
x=np.exp(2j*np.pi*3000*t)
fig,axes=plt.subplots(2,2,figsize=(12,7),constrained_layout=True)
ax=axes[0,0]
ax.plot(t[:33]*1000,x[:33].real,"o-",label="I = cos")
ax.plot(t[:33]*1000,x[:33].imag,"s-",label="Q = sin")
ax.set(xlabel="Time (ms)",ylabel="Amplitude",title="1. IQ samples: one cycle = 16 samples")
ax.legend(loc="upper right"); ax.grid(alpha=.2)
ax=axes[0,1]
ax.plot(x[:17].real,x[:17].imag,"o-")
for k in [0,4,8,12]: ax.annotate("n={}".format(k),(x[k].real,x[k].imag),xytext=(8,7),textcoords="offset points")
ax.set(xlabel="I",ylabel="Q",title="2. Complex plane: positive frequency",xlim=(-1.4,1.4),ylim=(-1.4,1.4))
ax.set_aspect("equal");ax.grid(alpha=.2)
f=np.fft.fftshift(np.fft.fftfreq(n,1/fs))
ax=axes[1,0]
for frequency,label in [(3000,"3000 Hz: bin centered"),(3100,"3100 Hz: off grid")]:
    a=np.exp(2j*np.pi*frequency*t)
    spectrum=np.abs(np.fft.fftshift(np.fft.fft(a)))/n
    ax.plot(f,20*np.log10(np.maximum(spectrum,1e-6)),label=label)
ax.set(xlabel="Frequency (Hz)",ylabel="Amplitude (dB)",title="3. Rectangular window and leakage",xlim=(2400,3700),ylim=(-65,3));ax.legend();ax.grid(alpha=.2)
ax=axes[1,1]
psd=np.abs(np.fft.fft(x))**2/(fs*n)
ax.bar(["Time mean power","PSD integral"],[np.mean(abs(x)**2),psd.sum()*fs/n],color=["#167c9c","#f49d37"])
ax.set(ylabel="Normalized power",title="4. Parseval: both values equal 1",ylim=(0,1.25));ax.grid(axis="y",alpha=.2)
fig.suptitle("Edge DSP baseline | Fs = 48 kS/s | N = 2048 | A = 1",fontsize=16)
fig.savefig(OUT/"iq_fft_psd.png",dpi=130);plt.close(fig)

fig,axes=plt.subplots(1,2,figsize=(12,4.5),constrained_layout=True)
length=65;k=np.arange(length)-(length-1)/2
h=(2*6000/fs)*np.sinc(2*6000/fs*k)*np.hamming(length);h/=h.sum()
H=np.fft.fft(h,8192);freq=np.arange(4096)*fs/8192
axes[0].plot(freq,20*np.log10(np.maximum(abs(H[:4096]),1e-8)))
axes[0].axvline(3000,color="#167c9c",linestyle="--",label="Input 3 kHz")
axes[0].axvline(12000,color="#e45b52",linestyle="--",label="Input 12 kHz")
axes[0].set(xlabel="Frequency (Hz)",ylabel="Gain (dB)",title="65-tap FIR | delay = 32 samples",ylim=(-100,5));axes[0].legend();axes[0].grid(alpha=.2)
rng=np.random.RandomState(42);m=8;ns=4096
def a(theta): return np.exp(1j*np.pi*np.arange(m)[:,None]*np.sin(np.deg2rad(theta)))
s=(rng.randn(2,ns)+1j*rng.randn(2,ns))/np.sqrt(2)
w=(rng.randn(m,ns)+1j*rng.randn(m,ns))/np.sqrt(2)
X=a(np.array([-20,30])).dot(s)+.1*w
_,U=np.linalg.eigh(X.dot(X.conj().T)/ns)
theta=np.linspace(-90,90,1801)
P=1/np.maximum(np.sum(abs(U[:,:6].conj().T.dot(a(theta)))**2,axis=0),1e-15)
axes[1].plot(theta,10*np.log10(P/P.max()),color="#167c9c")
for angle in [-20,30]: axes[1].axvline(angle,color="#f49d37",linestyle="--")
axes[1].set(xlabel="Broadside angle (deg)",ylabel="Normalized MUSIC (dB)",title="ULA 8 | K = 2 | truth = -20 / +30 deg",ylim=(-65,2));axes[1].grid(alpha=.2)
fig.suptitle("Advanced DSP | synthetic data, CPU reference",fontsize=16)
fig.savefig(OUT/"fir_music.png",dpi=130);plt.close(fig)
