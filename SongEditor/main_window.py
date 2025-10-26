from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QMainWindow, QDockWidget, QSizePolicy, QLabel

from song_details_widget import SongDetailsWidget
from song_widget import SongWidget, KeysStatus
from control_panel import ControlPanel
from tracks_list_widget import TracksListWidget
from notes_list_widget import NotesListWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Funzl Bredl Song Editor")

        self.song_widget = SongWidget(self)
        self.song_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setCentralWidget(self.song_widget)

        # Bottom controls dock
        self.control_panel = ControlPanel(self.song_widget, self)
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
        self.song_widget.track_added.connect(self.track_list_widget.add_track)
        self.song_widget.track_removed.connect(self.track_list_widget.remove_track)
        self.song_widget.hover_track_changed.connect(self.track_list_widget.set_hover_track)
        self.song_widget.note_selection_changed.connect(self.notes_list_widget.set_selected_notes)
        self.song_widget.key_status_update.connect(self.update_status_keys)
        self.notes_list_widget.note_changed.connect(self.song_widget.update)
        self.notes_list_widget.note_changed.connect(self.track_list_widget.on_track_updated)
        self.notes_list_widget.note_changed.connect(self.song_details_widget.update_labels)
        self.notes_list_widget.hover_changed.connect(self.song_widget.set_highlighted_note)
        self.track_list_widget.track_changed.connect(self.song_widget.update)
        self.track_list_widget.move_up_requested.connect(self.song_widget.move_track_up)
        self.track_list_widget.move_down_requested.connect(self.song_widget.move_track_down)
        self.track_list_widget.select_track_requested.connect(self.song_widget.select_track)
        self.track_list_widget.hover_changed.connect(self.song_widget.set_highlighted_track)

        self.resize(1200, 700)
        self.showMaximized()

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
