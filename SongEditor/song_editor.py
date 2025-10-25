#! /usr/bin/env python3

import sys
from PySide6.QtCore import Qt, QRect, QSize, QTimer, QPointF, QRectF, QLocale
from PySide6.QtGui import QCloseEvent, QPainter, QPen, QColor, QAction, QFont, QFontMetrics
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSizePolicy, QVBoxLayout, QHBoxLayout, QComboBox,
    QPushButton, QFileDialog, QLabel, QSlider, QStyle, QStyleOptionSlider, QDockWidget, QToolBox,
    QDoubleSpinBox, QLabel, QScrollArea
)

from midi_loader import MidiLoader
from song_widget import SongWidget
from song_player import Player
from song import Track, Note

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
        self.player: Player | None = None

    def open_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open MIDI File", "", "MIDI Files (*.mid *.midi)")
        if fname:
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

class TrackWidget(QWidget):
    def __init__(self, track: Track, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        self.track = track
        self.label = QLabel(track.name, self)
        layout.addWidget(self.label)

class TrackListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        self.container = QWidget(self)
        self.vbox_layout = QVBoxLayout(self.container)
        self.container.setLayout(self.vbox_layout)

        self.scroll_area.setWidget(self.container)
        self.main_layout.addWidget(self.scroll_area)
        self.setLayout(self.main_layout)

    def add_track(self, track: Track):
        track_widget = TrackWidget(track, self)
        self.vbox_layout.addWidget(track_widget)

    def remove_track(self, track: Track):
        for i in range(self.vbox_layout.count()):
            item = self.vbox_layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, TrackWidget) and widget.track == track:
                widget.setParent(None)
                break

    def set_hover_track(self, track: Track | None):
        for i in range(self.vbox_layout.count()):
            item = self.vbox_layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, TrackWidget):
                if track and widget.track == track:
                    widget.setStyleSheet("background-color: darkgray;")
                    self.scroll_area.ensureWidgetVisible(widget)
                else:
                    widget.setStyleSheet("")

class NoteWidget(QWidget):
    def __init__(self, note: Note | None, parent=None):
        super().__init__(parent)
        self.note = note
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.start_spinner = QDoubleSpinBox(self)
        self.start_spinner.setRange(0, 1_000_000)
        self.start_spinner.setDecimals(3)
        self.pitch_combobox = QComboBox(self)
        self.pitch_combobox.addItems([str(p) for p in range(128)])
        self.duration_spinner = QDoubleSpinBox(self)
        self.duration_spinner.setRange(0, 1_000_000)
        self.duration_spinner.setDecimals(3)
        self.buzzer_selector = QComboBox(self)
        self.buzzer_selector.addItems(['1', '2', '3', 'None', 'Any'])

        # show thousands separators and use system locale
        for sb in (self.start_spinner, self.duration_spinner):
            sb.setGroupSeparatorShown(True)
            sb.setLocale(QLocale.system())

        layout.addWidget(self.start_spinner)
        layout.addWidget(self.pitch_combobox)
        layout.addWidget(self.duration_spinner)
        layout.addWidget(self.buzzer_selector)

        self.set_note(note)

    def set_note(self, note: Note | None):
        self.note = note
        if note:
            self.setEnabled(True)
            self.start_spinner.setValue(note.start_tick / 1000.0)
            self.pitch_combobox.setCurrentText(str(note.pitch))
            self.duration_spinner.setValue(note.duration / 1000.0)
            self.buzzer_selector.setCurrentText(str(note.buzzer))
        else:
            self.setEnabled(False)
            self.start_spinner.setValue(0)
            self.pitch_combobox.setCurrentText("0")
            self.duration_spinner.setValue(0)
            self.buzzer_selector.setCurrentText("None")

class NotesListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vbox_layout = QVBoxLayout(self)
        self.setLayout(self.vbox_layout)

        self.hover_label = QLabel("Hover:", self)
        self.vbox_layout.addWidget(self.hover_label)

        self.hover = NoteWidget(None, self)
        self.hover_layout = QVBoxLayout(self.hover)
        self.hover.setLayout(self.hover_layout)
        self.vbox_layout.addWidget(self.hover)

        self.selected_label = QLabel("Selected:", self)
        self.vbox_layout.addWidget(self.selected_label)

        self.selected_container = QWidget(self)
        self.selected_layout = QVBoxLayout(self.selected_container)
        self.selected_container.setLayout(self.selected_layout)
        self.vbox_layout.addWidget(self.selected_container)

        self.vbox_layout.addStretch()

    def set_hover_note(self, note: Note | None):
        self.hover.set_note(note)

    def add_note(self, note):
        note_widget = NoteWidget(note, self)
        self.vbox_layout.addWidget(note_widget)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Funzl Bredl Song Editor")

        self.song_widget = SongWidget(self)
        self.song_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.song_widget.setMinimumHeight(200)
        self.setCentralWidget(self.song_widget)

        # Bottom controls dock
        self.control_panel = PlayControlPanel(self.song_widget, self)
        bottom_dock = QDockWidget("Playback Controls", self)
        bottom_dock.setWidget(self.control_panel)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, bottom_dock)

        # Left Tracks Dock
        self.track_list_widget = TrackListWidget(self)
        track_dock = QDockWidget("Tracks", self)
        track_dock.setWidget(self.track_list_widget)
        track_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable
                               | QDockWidget.DockWidgetFeature.DockWidgetFloatable
                               | QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, track_dock)

        # Left Notes Dock
        self.notes_list_widget = NotesListWidget(self)
        notes_dock = QDockWidget("Notes", self)
        notes_dock.setWidget(self.notes_list_widget)
        notes_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable
                               | QDockWidget.DockWidgetFeature.DockWidgetFloatable
                               | QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, notes_dock)

        self.splitDockWidget(track_dock, notes_dock, Qt.Orientation.Vertical)
        self.resizeDocks([track_dock, notes_dock], [300, 400], Qt.Orientation.Vertical)

        self.resize(1200, 700)

        self.song_widget.hover_note_changed.connect(self.notes_list_widget.set_hover_note)
        self.song_widget.track_added.connect(self.track_list_widget.add_track)
        self.song_widget.track_removed.connect(self.track_list_widget.remove_track)
        self.song_widget.hover_track_changed.connect(self.track_list_widget.set_hover_track)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.control_panel.stop()
        return super().closeEvent(event)

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
