from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QFileDialog

from song_widget import SongWidget
from midi_loader import MidiLoader
from song_player import Player
from config import Config

class ControlPanel(QWidget):
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
        self.player: Player | None = None

    def open_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open MIDI File", Config.last_opened_directory, "MIDI Files (*.mid *.midi)")
        if fname:
            Config.last_opened_directory = fname.rsplit('/', 1)[0]
            self.add_file(fname)

    def add_file(self, fname: str):
        song = MidiLoader.load_midi_file(fname)
        self.canvas.set_song(song)
        self.status.setText(f"Loaded: {fname}")

    def play(self):
        self.player = Player(self.canvas.song)
        self.player.start()

    def stop(self):
        if self.player:
            self.player.stop()
