import sys
from PyQt6.QtWidgets import QApplication
from dist.params import Params
from dist.audio import AudioEngine
from dist.gui import MainWindow

def main():
    app = QApplication(sys.argv)
    params = Params()
    engine = AudioEngine(params)
    win = MainWindow(engine, params)
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
