import math
import numpy as np

class Stereo:
    def __init__(self):
        self.b0 = 1.0
        self.b1 = 0.0
        self.b2 = 0.0
        self.a1 = 0.0
        self.a2 = 0.0
        self.reset()

    def reset(self):
        self.x1L=self.x2L=self.y1L=self.y2L=0.0
        self.x1R=self.x2R=self.y1R=self.y2R=0.0

    def _set_coeffs(self,b0,b1,b2,a0,a1,a2):
        if a0 == 0:
            a0 = 1.0
        self.b0=b0/a0
        self.b1=b1/a0
        self.b2=b2/a0
        self.a1=a1/a0
        self.a2=a2/a0

    def set_low_shelf(self,fs,f0,gain_lin):
        A = max(1e-4, math.sqrt(max(gain_lin,1e-8)))
        w0 = 2*math.pi*f0/fs
        cosw0 = math.cos(w0)
        sinw0 = math.sin(w0)
        alpha = sinw0/2 * math.sqrt(2)
        sqrtA = math.sqrt(A)

        b0 = A*((A+1)-(A-1)*cosw0 + 2*sqrtA*alpha)
        b1 = 2*A*((A-1)-(A+1)*cosw0)
        b2 = A*((A+1)-(A-1)*cosw0 - 2*sqrtA*alpha)
        a0 = (A+1)+(A-1)*cosw0 + 2*sqrtA*alpha
        a1 = -2*((A-1)+(A+1)*cosw0)
        a2 = (A+1)+(A-1)*cosw0 - 2*sqrtA*alpha

        self._set_coeffs(b0,b1,b2,a0,a1,a2)

    def set_high_shelf(self,fs,f0,gain_lin):
        A = max(1e-4, math.sqrt(max(gain_lin,1e-8)))
        w0 = 2*math.pi*f0/fs
        cosw0 = math.cos(w0)
        sinw0 = math.sin(w0)
        alpha = sinw0/2 * math.sqrt(2)
        sqrtA = math.sqrt(A)

        b0 = A*((A+1)+(A-1)*cosw0 + 2*sqrtA*alpha)
        b1 = -2*A*((A-1)+(A+1)*cosw0)
        b2 = A*((A+1)+(A-1)*cosw0 - 2*sqrtA*alpha)
        a0 = (A+1)-(A-1)*cosw0 + 2*sqrtA*alpha
        a1 = 2*((A-1)-(A+1)*cosw0)
        a2 = (A+1)-(A-1)*cosw0 - 2*sqrtA*alpha

        self._set_coeffs(b0,b1,b2,a0,a1,a2)

    def set_peaking(self,fs,f0,Q,gain_lin):
        A = max(1e-4, math.sqrt(max(gain_lin,1e-8)))
        w0 = 2*math.pi*f0/fs
        cosw0 = math.cos(w0)
        sinw0 = math.sin(w0)
        alpha = sinw0/(2*Q)

        b0 = 1 + alpha*A
        b1 = -2*cosw0
        b2 = 1 - alpha*A
        a0 = 1 + alpha/A
        a1 = -2*cosw0
        a2 = 1 - alpha/A

        self._set_coeffs(b0,b1,b2,a0,a1,a2)

    def process(self, x):
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
