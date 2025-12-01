from dist.filter import Stereo

class EQ:
    def __init__(self, fs):
        self.fs = fs
        self.low = BiquadStereo()
        self.mid = BiquadStereo()
        self.high = BiquadStereo()

    def update(self, bass_gain, mid_gain, treble_gain):
        self.low.set_low_shelf(self.fs, 400.0, bass_gain)
        self.mid.set_peaking(self.fs, 1000.0, 1.0, mid_gain)
        self.high.set_high_shelf(self.fs, 5000.0, treble_gain)

    def process(self, x):
        y = self.low.process(x)
        y = self.mid.process(y)
        y = self.high.process(y)
        return y

    def reset(self):
        self.low.reset()
        self.mid.reset()
        self.high.reset()