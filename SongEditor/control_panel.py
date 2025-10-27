from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QFileDialog,\
                              QMainWindow, QStatusBar, QApplication

from song_widget import SongWidget
from midi_loader import MidiLoader
from song_player import Player
from config import Config
from funzl_board import FunzlBoard
from song import Song

class ControlPanel(QWidget):
    def __init__(self, canvas: SongWidget, status_bar: QStatusBar, song: Song, parent=None):
        super().__init__(parent)

        self._selected_notes: list = []
        self.canvas = canvas
        self.status_bar = status_bar
        self._song: Song | None = None

        layout = QHBoxLayout(self)
        self.send_song_btn = QPushButton("Send Song")
        self.send_selected_btn = QPushButton("Send Selected")
        self.stop_btn = QPushButton("Send Stop")
        self.open_btn = QPushButton("Import MIDI")
        self.fix_overlaps_btn = QPushButton("Fix Overlaps")

        layout.addWidget(self.send_song_btn)
        layout.addWidget(self.send_selected_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(self.open_btn)
        layout.addWidget(self.fix_overlaps_btn)

        self.send_song_btn.clicked.connect(self.send_song)
        self.send_selected_btn.clicked.connect(self.send_selected)
        self.stop_btn.clicked.connect(self.stop)
        self.open_btn.clicked.connect(self.open_file)
        self.fix_overlaps_btn.clicked.connect(self.fix_overlaps)
        self.player: Player | None = None

        self.on_song_changed(song)
        self.selected_notes_changed([])

    def send_song(self):
        song = self.canvas._song
        if not song:
            self.status_bar.showMessage("No song loaded to send.", 2000)
            return

        result = FunzlBoard.send_song(song, progress_callback=self.showMessage)
        self.showMessage(result)

    def send_selected(self):
        selected_notes = self.canvas._selected_notes
        if not selected_notes:
            self.status_bar.showMessage("No notes selected to send.", 2000)
            return

        result = FunzlBoard.send_notes(selected_notes, progress_callback=self.showMessage)
        self.showMessage(result)

    def showMessage(self, message: str):
        self.status_bar.showMessage(message, 2000)
        QApplication.processEvents()

    def on_song_changed(self, song):
        if self._song:
            self._song.remove_change_listener(self.on_song_has_changed)
        self._song = song
        if self._song:
            self._song.add_change_listener(self.on_song_has_changed)
        self.on_song_has_changed()

    def on_song_has_changed(self):
        '''Called when the song content has changed.'''
        if self._song:
            self.send_song_btn.setEnabled(len(self._song.error_notes) == 0 and len(self._song.all_notes) > 0)

    def open_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open MIDI File", Config.last_opened_directory, "MIDI Files (*.mid *.midi)")
        if fname:
            Config.last_opened_directory = fname.rsplit('/', 1)[0]
            self.add_file(fname)

    def add_file(self, fname: str):
        song = MidiLoader.load_midi_file(fname)
        self.canvas.set_song(song)
        self.status_bar.showMessage(f"Loaded: {fname}", 2000)

    def play(self):
        self.player = Player(self.canvas._song)
        self.player.start()

    def stop(self):
        result = FunzlBoard.send_stop()

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

    def fix_overlaps(self):
        if not self.canvas._song:
            return
        self.canvas._song.fix_overlaps()
