import re
from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QMainWindow, QDockWidget, QSizePolicy, QLabel, QFileDialog
import json

from dataclasses import asdict

from funzl_board import FunzlBoard
from config import Config
from song_details_widget import SongDetailsWidget
from song_widget import SongWidget, KeysStatus
from control_panel import ControlPanel
from tracks_list_widget import TracksListWidget
from notes_list_widget import NotesListWidget
from song import Song

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.file_name: str | None = None

        self.setWindowTitle("Funzl Bredl Song Editor")

        self.song_widget = SongWidget(self)
        self.song_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setCentralWidget(self.song_widget)

        # Bottom controls dock
        self.control_panel = ControlPanel(self.song_widget, self.statusBar(), self.song_widget.song, self)
        bottom_dock = QDockWidget("Playback Controls", self)
        bottom_dock.setWidget(self.control_panel)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, bottom_dock)

        # Left Song Details Dock
        self.song_details_widget = SongDetailsWidget(self.song_widget.song, self)
        self.song_details_widget.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        song_dock = QDockWidget("Song Details", self)
        song_dock.setWidget(self.song_details_widget)
        song_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable
                               | QDockWidget.DockWidgetFeature.DockWidgetFloatable
                               | QDockWidget.DockWidgetFeature.DockWidgetClosable)
        song_dock.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, song_dock)

        # Left Tracks Dock
        self.track_list_widget = TracksListWidget(self)
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

        track_dock.setMinimumWidth(320)

        # Status bar
        self.status_keys_label = QLabel("")
        self.statusBar().addPermanentWidget(self.status_keys_label)

        self.song_widget.hover_note_changed.connect(self.notes_list_widget.set_hover_note)
        self.song_widget.track_removed.connect(self.track_list_widget.remove_track)
        self.song_widget.track_added.connect(self.track_list_widget.add_track)
        self.song_widget.hover_track_changed.connect(self.track_list_widget.set_hover_track)
        self.song_widget.note_selection_changed.connect(self.notes_list_widget.set_selected_notes)
        self.song_widget.note_selection_changed.connect(self.control_panel.selected_notes_changed)
        self.song_widget.key_status_update.connect(self.update_status_keys)
        self.song_widget.song_changed.connect(self.control_panel.on_song_changed)
        self.notes_list_widget.hover_changed.connect(self.song_widget.set_highlighted_note)
        self.track_list_widget.move_up_requested.connect(self.song_widget.move_track_up)
        self.track_list_widget.move_down_requested.connect(self.song_widget.move_track_down)
        self.track_list_widget.select_track_requested.connect(self.song_widget.select_track)
        self.track_list_widget.hover_changed.connect(self.song_widget.set_highlighted_track)
        self.song_details_widget.save_requested.connect(self.save_file_clicked)
        self.song_details_widget.save_as_requested.connect(self.save_as_clicked)
        self.song_details_widget.load_requested.connect(self.open_file_clicked)
        self.song_details_widget.export_requested.connect(self.export_clicked)

        self.resize(1200, 700)
        self.showMaximized()

        if Config.last_song:
            self.open_file(Config.last_song)
        else:
            QTimer.singleShot(0, self.control_panel.open_file)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.control_panel.stop()
        return super().closeEvent(event)

    def update_status_keys(self, status: int):
        if status == KeysStatus.NONE:
            self.status_keys_label.setText("")
        elif status == KeysStatus.ADD:
            self.status_keys_label.setText("Add")
        elif status == KeysStatus.REMOVE:
            self.status_keys_label.setText("Remove")
        elif status == KeysStatus.SPAN:
            self.status_keys_label.setText("Span")
        elif status == KeysStatus.TOGGLE:
            self.status_keys_label.setText("Toggle")
        elif status == KeysStatus.SCALE_X:
            self.status_keys_label.setText("Scale X")
        elif status == KeysStatus.SCALE_Y:
            self.status_keys_label.setText("Scale Y")
        else:
            self.status_keys_label.setText("")

    def save_file_clicked(self):
        if not self.file_name:
            self.save_as_clicked()
        else:
            self.save_file(self.file_name)

    def save_file(self, file_name: str):
        with open(file_name, 'w') as f:
            f.write(self.song_widget.song.to_json())
        self.statusBar().showMessage(f"Saved song to {file_name}", 5000)
        print(f"Saved song to {file_name}")

    def save_as_clicked(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Song As", Config.last_opened_directory, "Funzl Board Song Files (*.fbsong);;All Files (*)")
        if file_name:
            self.file_name = file_name
            self.save_file(self.file_name)

    def open_file_clicked(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Song", Config.last_opened_directory, "Funzl Board Song Files (*.fbsong);;All Files (*)")
        if file_name:
            self.open_file(file_name)

    def open_file(self, file_name: str):
        with open(file_name, 'r') as f:
            data = f.read()
        song = Song.from_json(data)
        self.song_widget.set_song(song)
        self.song_details_widget.set_song(song)
        for track in song.tracks:
            self.track_list_widget.add_track(track)
        self.notes_list_widget.set_hover_note(None)
        self.notes_list_widget.set_selected_notes([])
        self.file_name = file_name
        Config.last_song = file_name

    def export_clicked(self):
        if not self.song_widget.song:
            self.statusBar().showMessage("No song to export.", 2000)
            return

        file_name = namespace = ''.join(p.capitalize() for p in [p for p in re.split(r'[^0-9A-Za-z]+', self.song_widget.song.name) if p]) or 'Song'
        file_name = file_name[0].lower() + file_name[1:] + '.h'
        file_name = f'/home/thomas/Develop/ESP32/FunzlBrett/src/music/songs/{file_name}'

        file_name, _ = QFileDialog.getSaveFileName(self, "Export Song", file_name, "C++ Header Files (*.h);;All Files (*)")
        if not file_name:
            return

        exported_code = FunzlBoard.export(self.song_widget.song)
        with open(file_name, 'w') as f:
            f.write(exported_code)

        self.statusBar().showMessage(f"Exported song to {file_name}", 5000)
        print(f"Exported song to {file_name}")
