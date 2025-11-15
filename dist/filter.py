import numpy as np
import math

class BiquadStereo:
    def __init__(self):
        self.b0 = 1.0
        self.b1 = 0.0
        self.b2 = 0.0
        self.a1 = 0.0
        self.a2 = 0.0
        self.reset()

    def reset(self):
        self.x1L=self.x2L=0.0
        self.y1L=self.y2L=0.0
        self.x1R=self.x2R=0.0
        self.y1R=self.y2R=0.0

    def _set(self,b0,b1,b2,a0,a1,a2):
        if a0 == 0: a0 = 1.0
        self.b0=b0/a0
        self.b1=b1/a0
        self.b2=b2/a0
        self.a1=a1/a0
        self.a2=a2/a0

    # ---------------------
    # LPF
    # ---------------------
    def set_lpf(self,fs,f0):
        w0 = 2*math.pi*f0/fs
        cosw = math.cos(w0)
        sinw = math.sin(w0)
        alpha = sinw / math.sqrt(2)

        b0 = (1 - cosw) / 2
        b1 = 1 - cosw
        b2 = (1 - cosw) / 2
        a0 = 1 + alpha
        a1 = -2 * cosw
        a2 = 1 - alpha

        self._set(b0,b1,b2,a0,a1,a2)

    # ---------------------
    # HPF
    # ---------------------
    def set_hpf(self,fs,f0):
        w0 = 2*math.pi*f0/fs
        cosw = math.cos(w0)
        sinw = math.sin(w0)
        alpha = sinw / math.sqrt(2)

        b0 = (1 + cosw) / 2
        b1 = -(1 + cosw)
        b2 = (1 + cosw) / 2
        a0 = 1 + alpha
        a1 = -2 * cosw
        a2 = 1 - alpha

        self._set(b0,b1,b2,a0,a1,a2)

    # ---------------------
    # BPF (constant skirt gain)
    # ---------------------
    def set_bpf(self,fs,f0,Q):
        w0 = 2*math.pi*f0/fs
        cosw = math.cos(w0)
        sinw = math.sin(w0)
        alpha = sinw/(2*Q)

        b0 =   alpha
        b1 =   0
        b2 =  -alpha
        a0 =   1 + alpha
        a1 =  -2*cosw
        a2 =   1 - alpha

        self._set(b0,b1,b2,a0,a1,a2)

    # ---------------------
    def process(self,x):
        out = np.empty_like(x)
        for n in range(x.shape[0]):
            xl = float(x[n,0])
            xr = float(x[n,1])

            yl = self.b0*xl + self.b1*self.x1L + self.b2*self.x2L - self.a1*self.y1L - self.a2*self.y2L
            self.x2L=self.x1L ; self.x1L=xl
            self.y2L=self.y1L ; self.y1L=yl

            yr = self.b0*xr + self.b1*self.x1R + self.b2*self.x2R - self.a1*self.y1R - self.a2*self.y2R
            self.x2R=self.x1R ; self.x1R=xr
            self.y2R=self.y1R ; self.y1R=yr

            out[n,0]=yl
            out[n,1]=yr

        return out
