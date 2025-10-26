from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, \
                              QLineEdit, QToolButton
from PySide6.QtCore import Signal

from song import Track

class TrackWidget(QWidget):
    track_changed = Signal(Track)
    move_up_requested = Signal(Track)
    move_down_requested = Signal(Track)

    def _on_name_changed(self):
        self.track.name = self.name_text.text()
        self.track_changed.emit(self.track)

    def __init__(self, track: Track, parent=None):
        super().__init__(parent)
        self.track = track
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        title_widget = QWidget(self)
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        self.index_label = QLabel(f'..:', self)
        title_layout.addWidget(self.index_label)

        self.name_text = QLineEdit(track.name, self)
        self.name_text.editingFinished.connect(self._on_name_changed)
        title_layout.addWidget(self.name_text)

        title_layout.addStretch()
        self.up_button = QToolButton(self)
        self.up_button.setText('⬆')
        self.up_button.clicked.connect(lambda: self.move_up_requested.emit(self.track))
        title_layout.addWidget(self.up_button)

        self.down_button = QToolButton(self)
        self.down_button.setText('⬇')
        self.down_button.clicked.connect(lambda: self.move_down_requested.emit(self.track))
        title_layout.addWidget(self.down_button)

        layout.addWidget(title_widget)

class TracksListWidget(QWidget):
    track_changed = Signal(Track)
    move_up_requested = Signal(Track)
    move_down_requested = Signal(Track)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        self.container = QWidget(self)
        self.vbox_layout = QVBoxLayout(self.container)
        self.container.setLayout(self.vbox_layout)

        stretch_container = QWidget(self)
        stretch_layout = QVBoxLayout(stretch_container)
        stretch_layout.addWidget(self.container)
        stretch_layout.addStretch()

        self.scroll_area.setWidget(stretch_container)
        self.main_layout.addWidget(self.scroll_area)
        self.setLayout(self.main_layout)

    def add_track(self, track: Track):
        track_widget = TrackWidget(track, self)
        self.vbox_layout.addWidget(track_widget)
        track_widget.track_changed.connect(self.track_changed.emit)
        track_widget.move_up_requested.connect(self._track_moved_up)
        track_widget.move_down_requested.connect(self._track_moved_down)
        self._update_list()

    def remove_track(self, track: Track):
        for i in range(self.vbox_layout.count()):
            item = self.vbox_layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, TrackWidget) and widget.track == track:
                widget.setParent(None)
                self._update_list()
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

    def _track_moved_up(self, track: Track):
        self.move_up_requested.emit(track)
        for i in range(self.vbox_layout.count()):
            item = self.vbox_layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, TrackWidget) and widget.track == track:
                if i == 0:
                    return
                prev_widget = self.vbox_layout.itemAt(i - 1).widget()
                if not isinstance(prev_widget, TrackWidget):
                    return

                # remove and re-insert swapped
                self.vbox_layout.removeWidget(prev_widget)
                self.vbox_layout.removeWidget(widget)
                self.vbox_layout.insertWidget(i - 1, widget)
                self.vbox_layout.insertWidget(i, prev_widget)

                self._update_list()

    def _track_moved_down(self, track: Track):
        self.move_down_requested.emit(track)
        for i in range(self.vbox_layout.count()):
            item = self.vbox_layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, TrackWidget) and widget.track == track:
                if i == self.vbox_layout.count() - 1:
                    return
                next_widget = self.vbox_layout.itemAt(i + 1).widget()
                if not isinstance(next_widget, TrackWidget):
                    return

                # remove and re-insert swapped
                self.vbox_layout.removeWidget(widget)
                self.vbox_layout.removeWidget(next_widget)
                self.vbox_layout.insertWidget(i, next_widget)
                self.vbox_layout.insertWidget(i + 1, widget)

                self._update_list()
                return

    def _update_list(self):
        total = self.vbox_layout.count()
        for idx in range(total):
            it = self.vbox_layout.itemAt(idx)
            w = it.widget()
            if isinstance(w, TrackWidget):
                w.index_label.setText(f'{idx + 1}:')
                w.up_button.setEnabled(idx != 0)
                w.down_button.setEnabled(idx != total - 1)

        total = self.vbox_layout.count()
        for idx in range(total):
            it = self.vbox_layout.itemAt(idx)
            w = it.widget()
            if isinstance(w, TrackWidget):
                w.up_button.setEnabled(idx != 0)
                w.down_button.setEnabled(idx != total - 1)

        total = self.vbox_layout.count()
        for idx in range(total):
            it = self.vbox_layout.itemAt(idx)
            w = it.widget()
            if isinstance(w, TrackWidget):
                w.up_button.setEnabled(idx != 0)
                w.down_button.setEnabled(idx != total - 1)
