from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QMainWindow, QDockWidget, QSizePolicy

from song_widget import SongWidget
from control_panel import ControlPanel
from tracks_list_widget import TracksListWidget
from notes_list_widget import NotesListWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Funzl Bredl Song Editor")

        self.song_widget = SongWidget(self)
        self.song_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.song_widget.setMinimumHeight(200)
        self.setCentralWidget(self.song_widget)

        # Bottom controls dock
        self.control_panel = ControlPanel(self.song_widget, self)
        bottom_dock = QDockWidget("Playback Controls", self)
        bottom_dock.setWidget(self.control_panel)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, bottom_dock)

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

        self.splitDockWidget(track_dock, notes_dock, Qt.Orientation.Vertical)
        self.resizeDocks([track_dock, notes_dock], [300, 400], Qt.Orientation.Vertical)

        self.resize(1200, 700)

        self.song_widget.hover_note_changed.connect(self.notes_list_widget.set_hover_note)
        self.song_widget.track_added.connect(self.track_list_widget.add_track)
        self.song_widget.track_removed.connect(self.track_list_widget.remove_track)
        self.song_widget.hover_track_changed.connect(self.track_list_widget.set_hover_track)
        self.song_widget.note_selection_changed.connect(self.notes_list_widget.set_selected_notes)

        QTimer.singleShot(0, self.control_panel.open_file)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.control_panel.stop()
        return super().closeEvent(event)
