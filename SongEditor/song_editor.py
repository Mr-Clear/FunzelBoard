#! /usr/bin/env python3

import sys
from PySide6.QtCore import Qt, QRect, QSize, QTimer, QPointF, QRectF
from PySide6.QtGui import QPainter, QPen, QColor, QAction, QFont, QFontMetrics
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSizePolicy, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QLabel, QSlider, QStyle, QStyleOptionSlider
)

from midi_loader import MidiLoader, Track
from song_widget import SongWidget

class PlayControlPanel(QWidget):
    def __init__(self, canvas: SongWidget, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        layout = QHBoxLayout(self)
        self.play_btn = QPushButton("Play")
        self.stop_btn = QPushButton("Stop")
        self.open_btn = QPushButton("Open MIDI")
        self.status = QLabel("No file loaded")
        layout.addWidget(self.open_btn)
        layout.addWidget(self.play_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(self.status)
        self.play_btn.clicked.connect(self.play)
        self.stop_btn.clicked.connect(self.stop)
        self.open_btn.clicked.connect(self.open_file)

        self.add_file('/home/thomas/Develop/ESP32/FunzlBrett/Fur-Elise-3.mid')

    def open_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open MIDI File", "", "MIDI Files (*.mid *.midi)")
        if fname:
            self.add_file(fname)

    def add_file(self, fname: str):
        tracks = MidiLoader.load_midi_file(fname)
        self.canvas.add_tracks(tracks)
        self.status.setText(f"Loaded: {fname}")

    def play(self):
        self.canvas.start_playback()
        self.status.setText("Playing...")

    def stop(self):
        self.canvas.stop_playback()
        self.status.setText("Stopped.")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Funzl Bredl Song Editor")
        self.canvas = SongWidget(self)
        self.panel = PlayControlPanel(self.canvas, self)
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(self.canvas)
        layout.addWidget(self.panel)
        self.setCentralWidget(central)
        self.resize(1200, 700)

def main():
    # Suppress Qt debug output (including "kf.kio.core.connection: ..." etc.)
    import os
    os.environ["QT_LOGGING_RULES"] = "*.debug=false"

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
