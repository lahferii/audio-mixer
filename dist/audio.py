import numpy as np
import soundfile as sf
import sounddevice as sd
from dist.equalizerParametric import EQ

def stereoize(x):
    if x.ndim == 1:
        return np.stack([x, x], axis=1)
    return x

class AudioEngine:
    def __init__(self, params, blocksize=1024):
        self.params = params
        self.blocksize = blocksize
        self.fs = None
        self.a1 = None
        self.a2 = None
        self.pos1 = 0
        self.pos2 = 0
        self.stream = None
        self.eq = None

    def load_audio1(self, path):
        data, fs = sf.read(path, always_2d=False)
        self.a1 = stereoize(data.astype(np.float32))
        if self.fs is None:
            self.fs = fs
            self.eq = EQ(self.fs)
        self.pos1 = 0

    def load_audio2(self, path):
        data, fs = sf.read(path, always_2d=False)
        self.a2 = stereoize(data.astype(np.float32))
        if self.fs is None:
            self.fs = fs
            self.eq = EQ(self.fs)
        self.pos2 = 0

    def _read_block(self, arr, pos):
        if arr is None:
            return np.zeros((self.blocksize, 2), dtype=np.float32), 0
        end = pos + self.blocksize
        if end <= arr.shape[0]:
            blk = arr[pos:end]
            pos = end
        else:
            blk = np.vstack([arr[pos:], arr[:end - arr.shape[0]]])
            pos = end - arr.shape[0]
        return blk, pos

    @staticmethod
    def apply_pan(x, pan):
        L = np.cos((pan + 1) * np.pi / 4)
        R = np.sin((pan + 1) * np.pi / 4)
        y = np.empty_like(x)
        y[:, 0] = x[:, 0] * L
        y[:, 1] = x[:, 1] * R
        return y

    def start(self):
        if self.a1 is None and self.a2 is None:
            print("Minimal 1 audio diperlukan.")
            return
        if self.stream:
            return

        self.stream = sd.OutputStream(
            samplerate=self.fs,
            channels=2,
            dtype="float32",
            blocksize=self.blocksize,
            callback=self._callback
        )
        self.stream.start()

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    def reset(self):
        self.pos1 = 0
        self.pos2 = 0
        if self.eq:
            self.eq.reset()

    def export_mix(self, path):
        if self.a1 is None and self.a2 is None:
            return False

        p = self.params.get()

        L = min(
            len(self.a1) if self.a1 is not None else 10**12,
            len(self.a2) if self.a2 is not None else 10**12
        )
        if L == 10**12:
            L = len(self.a1) if self.a1 is not None else len(self.a2)

        a1 = self.a1[:L] if self.a1 is not None else np.zeros((L,2),dtype=np.float32)
        a2 = self.a2[:L] if self.a2 is not None else np.zeros((L,2),dtype=np.float32)

        m1 = self.apply_pan(a1*p["ch1_gain"], p["ch1_pan"])
        m2 = self.apply_pan(a2*p["ch2_gain"], p["ch2_pan"])

        mix = 0.5*(m1+m2)

        self.eq.update(p["bass"], p["mid"], p["treble"])
        out = self.eq.process(mix)

        peak = np.max(np.abs(out))
        if peak>1: out/=peak

        sf.write(path, out, self.fs)
        return True

    def _callback(self, out, frames, time, status):
        p = self.params.get()
        if not p["playing"]:
            out[:] = 0
            return

        b1, self.pos1 = self._read_block(self.a1, self.pos1)
        b2, self.pos2 = self._read_block(self.a2, self.pos2)

        b1 = self.apply_pan(b1*p["ch1_gain"], p["ch1_pan"])
        b2 = self.apply_pan(b2*p["ch2_gain"], p["ch2_pan"])

        mix = 0.5*(b1+b2)

        self.eq.update(p["bass"], p["mid"], p["treble"])
        y = self.eq.process(mix)

        out[:] = y.astype(np.float32)