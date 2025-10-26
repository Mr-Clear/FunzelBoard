from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QFileDialog,\
                              QMainWindow, QStatusBar, QApplication

from song_widget import SongWidget
from midi_loader import MidiLoader
from song_player import Player
from config import Config
from funzl_board import FunzlBoard

class ControlPanel(QWidget):
    def __init__(self, canvas: SongWidget, status_bar: QStatusBar, parent=None):
        super().__init__(parent)

        self._selected_notes: list = []
        self.canvas = canvas
        self.status_bar = status_bar

        layout = QHBoxLayout(self)
        self.send_selected_btn = QPushButton("Send Selected")
        self.play_btn = QPushButton("Play")
        self.stop_btn = QPushButton("Stop")
        self.open_btn = QPushButton("Open MIDI")
        self.status = QLabel("No file loaded")

        layout.addWidget(self.send_selected_btn)
        layout.addWidget(self.open_btn)
        layout.addWidget(self.play_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(self.status)

        self.send_selected_btn.clicked.connect(self.send_selected)
        self.play_btn.clicked.connect(self.play)
        self.stop_btn.clicked.connect(self.stop)
        self.open_btn.clicked.connect(self.open_file)
        self.player: Player | None = None

        self.selected_notes_changed([])

    def send_selected(self):
        selected_notes = self.canvas._selected_notes
        if not selected_notes:
            self.status.setText("No notes selected to send.")
            return

        result = FunzlBoard.send_notes(selected_notes, progress_callback=self.cb)
        self.cb(result)

    def cb(self, message: str):
        self.status_bar.showMessage(message, 2000)
        QApplication.processEvents()


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
        self.player = Player(self.canvas._song)
        self.player.start()

    def stop(self):
        if self.player:
            self.player.stop()

    def selected_notes_changed(self, notes):
        self._selected_notes = notes
        if not notes:
            self.send_selected_btn.setEnabled(False)
            return
        for note in notes:
            if note in self.canvas._song.error_notes:
                self.send_selected_btn.setEnabled(False)
                return
        notes_with_buzzer = [note for note in notes if note.buzzer != None]
        self.send_selected_btn.setEnabled(len(notes_with_buzzer) != 0)
