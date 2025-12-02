import numpy as np
import matplotlib.pyplot as plt
from PyQt6 import QtWidgets, QtCore
from scipy import signal
from dist.equalizerParametric import EQ



class MainWindow(QtWidgets.QWidget):
    def __init__(self, engine, params):
        super().__init__()
        self.engine = engine
        self.params = params

        self.setWindowTitle("Dasar Sistem Komunikasi - Mixer Audio")
        layout = QtWidgets.QGridLayout(self)

        self.btn1 = QtWidgets.QPushButton("Pilih Audio 1")
        self.btn2 = QtWidgets.QPushButton("Pilih Audio 2")
        self.lbl1 = QtWidgets.QLabel("Belum pilih file 1")
        self.lbl2 = QtWidgets.QLabel("Belum pilih file 2")

        layout.addWidget(self.btn1,0,0)
        layout.addWidget(self.lbl1,0,1)
        layout.addWidget(self.btn2,1,0)
        layout.addWidget(self.lbl2,1,1)

        self.btn1.clicked.connect(self.sel1)
        self.btn2.clicked.connect(self.sel2)

        def slider(text,minv,maxv,init,step,fmt):
            L=QtWidgets.QLabel(text)
            V=QtWidgets.QLabel(fmt.format(init))
            S=QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
            S.setMinimum(minv)
            S.setMaximum(maxv)
            S.setValue(int(init*step))
            return L,V,S

        self.controls=[
            slider("Ch1 Gain dB",-600,120,-3.0,10,"{:.1f}"),
            slider("Ch2 Gain dB",-600,120, 0.0,10,"{:.1f}"),
            slider("Ch1 Pan",-100,100,-0.5,100,"{:.2f}"),
            slider("Ch2 Pan",-100,100, 0.5,100,"{:.2f}"),
            slider("Bass dB",-120,120,0.0,10,"{:.1f}"),
            slider("Mid dB",-120,120,0.0,10,"{:.1f}"),
            slider("Treble dB",-120,120,0.0,10,"{:.1f}")
        ]

        row=2
        for L,V,S in self.controls:
            layout.addWidget(L,row,0)
            layout.addWidget(S,row,1)
            layout.addWidget(V,row,2)
            row+=1

        mapping=[
            "ch1_gain_db","ch2_gain_db","ch1_pan","ch2_pan",
            "bass_db","mid_db","treble_db"
        ]

        for (L,V,S),name in zip(self.controls,mapping):
            S.valueChanged.connect(lambda v,n=name,l=V: self.update_param(n,v,l))

        bar = QtWidgets.QHBoxLayout()
        self.btnPlay=QtWidgets.QPushButton("Play")
        self.btnReset=QtWidgets.QPushButton("Reset")
        self.btnExp=QtWidgets.QPushButton("Export WAV")
        self.btnAnal=QtWidgets.QPushButton("Analisa Spektrum")
        bar.addWidget(self.btnPlay)
        bar.addWidget(self.btnReset)
        bar.addWidget(self.btnExp)
        bar.addWidget(self.btnAnal)

        layout.addLayout(bar,row,0,1,3)

        self.btnPlay.clicked.connect(self.play)
        self.btnReset.clicked.connect(self.reset)
        self.btnExp.clicked.connect(self.export)
        self.btnAnal.clicked.connect(self.analyze)

    def sel1(self):
        p,_=QtWidgets.QFileDialog.getOpenFileName(self,"Audio 1","","Audio (*.wav *.mp3 *.flac *.ogg)")
        if p:
            self.lbl1.setText(p)
            self.engine.load_audio1(p)

    def sel2(self):
        p,_=QtWidgets.QFileDialog.getOpenFileName(self,"Audio 2","","Audio (*.wav *.mp3 *.flac *.ogg)")
        if p:
            self.lbl2.setText(p)
            self.engine.load_audio2(p)

    def update_param(self,name,v,label):
        if "pan" in name:
            val=v/100.0
            label.setText(f"{val:.2f}")
        else:
            val=v/10.0
            label.setText(f"{val:.1f}")
        self.params.set_attr(name,val)

    def play(self):
        self.params.set_attr("playing",True)
        self.engine.start()

    def reset(self):
        self.params.reset_all()
        self.engine.reset()

        defs=[-3.0,0.0,-0.5,0.5,0.0,0.0,0.0]
        st=[10,10,100,100,10,10,10]

        idx=0
        for (L,V,S),(d,s) in zip(self.controls,zip(defs,st)):
            S.setValue(int(d*s))
            if "Pan" in L.text(): V.setText(f"{d:.2f}")
            else: V.setText(f"{d:.1f}")
            idx+=1

    def export(self):
        path,_=QtWidgets.QFileDialog.getSaveFileName(self,"Export WAV","mix.wav","WAV (*.wav)")
        if not path:
            return
        ok=self.engine.export_mix(path)
        if ok:
            QtWidgets.QMessageBox.information(self,"OK","Export selesai!")
        else:
            QtWidgets.QMessageBox.warning(self,"Gagal","Minimal 1 audio diperlukan!")

    def analyze(self):
        fs=self.engine.fs
        if fs is None:
            return

        N = fs*10

        def get_last(arr,N):
            if arr is None:
                return None
            ch=arr[:,0]
            if len(ch)>=N:
                return ch[-N:]
            else:
                pad=N-len(ch)
                return np.concatenate([np.zeros(pad,dtype=np.float32),ch])

        s1=get_last(self.engine.a1,N)
        s2=get_last(self.engine.a2,N)

        if s1 is not None and s2 is not None:
            seg=0.5*(s1+s2)
        elif s1 is not None:
            seg=s1
        else:
            seg=s2

        f,Pb=signal.welch(seg,fs,nperseg=4096)
        before=10*np.log10(Pb+1e-12)

        p=self.params.get()

        stereo = np.stack([seg,seg],axis=1)
        eq = EQ(fs)
        eq.update(p["bass"],p["mid"],p["treble"])
        y=eq.process(stereo)
        yL=y[:,0]

        _,Pa=signal.welch(yL,fs,nperseg=4096)
        after=10*np.log10(Pa+1e-12)

        plt.figure(figsize=(8,4))
        plt.title("Spektrum Sebelum Dan Sesudah EQ")
        plt.plot(f,before,label="Before")
        plt.plot(f,after,label="After")
        plt.xscale("log")
        plt.grid(True)
        plt.legend()
        plt.show()