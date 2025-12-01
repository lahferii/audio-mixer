from dist.filter import Stereo

class EQ:
    def __init__(self, fs):
        self.fs = fs
        self.low = Stereo()
        self.mid = Stereo()
        self.high = Stereo()

    def update(self, bass_gain, mid_gain, treble_gain):
        fc_low  = 250
        fc_mid  = 2000
        fc_high = 5000

        self.bass_gain = bass_gain
        self.mid_gain = mid_gain
        self.treble_gain = treble_gain

        self.low.set_lpf(self.fs, fc_low)
        self.mid.set_bpf(self.fs, fc_mid, Q=1.0)
        self.high.set_hpf(self.fs, fc_high)

    def process(self, x):
        L = self.low.process(x)      * self.bass_gain
        M = self.mid.process(x)      * self.mid_gain
        H = self.high.process(x)     * self.treble_gain
        return L + M + H

    def reset(self):
        self.low.reset()
        self.mid.reset()
        self.high.reset()
