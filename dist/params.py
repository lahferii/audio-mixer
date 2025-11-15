import math

class Params:
    def __init__(self):
        self.playing = False
        self.ch1_gain_db = -3.0
        self.ch2_gain_db = 0.0
        self.ch1_pan = -0.5
        self.ch2_pan = 0.5
        self.bass_db = 0.0
        self.mid_db = 0.0
        self.treble_db = 0.0

    def reset_all(self):
        self.__init__()

    def get(self):
        return dict(
            ch1_gain = 10 ** (self.ch1_gain_db / 20),
            ch2_gain = 10 ** (self.ch2_gain_db / 20),
            ch1_pan = self.ch1_pan,
            ch2_pan = self.ch2_pan,
            bass = 10 ** (self.bass_db / 20),
            mid = 10 ** (self.mid_db / 20),
            treble = 10 ** (self.treble_db / 20),
            playing = self.playing
        )

    def set_attr(self, name, value):
        setattr(self, name, value)
