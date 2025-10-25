from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea

from song import Track

class TrackWidget(QWidget):
    def __init__(self, track: Track, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        self.track = track
        self.label = QLabel(track.name, self)
        layout.addWidget(self.label)

class TracksListWidget(QWidget):
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
