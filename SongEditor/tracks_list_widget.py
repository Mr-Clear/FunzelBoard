from PySide6.QtGui import QEnterEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, \
                              QLineEdit, QToolButton
from PySide6.QtCore import Signal, QEvent

from song import Track, Buzzer

class TrackWidget(QWidget):
    track_changed = Signal(Track)
    move_up_requested = Signal(Track)
    move_down_requested = Signal(Track)
    select_track_requested = Signal(Track)
    hover_changed = Signal(object)

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

        select_all_button = QToolButton(self)
        select_all_button.setText('☑')
        title_layout.addWidget(select_all_button)
        select_all_button.clicked.connect(lambda: self.select_track_requested.emit(self.track))

        title_layout.addSpacing(4)

        self.up_button = QToolButton(self)
        self.up_button.setText('⬆')
        self.up_button.clicked.connect(lambda: self.move_up_requested.emit(self.track))
        title_layout.addWidget(self.up_button)

        self.down_button = QToolButton(self)
        self.down_button.setText('⬇')
        self.down_button.clicked.connect(lambda: self.move_down_requested.emit(self.track))
        title_layout.addWidget(self.down_button)

        status_widget = QWidget(self)
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(0, 0, 0, 0)

        status_layout.addWidget(QLabel('⏱', self))
        self.duration_label = QLabel(self)
        status_layout.addWidget(self.duration_label)
        status_layout.addStretch()

        status_layout.addWidget(QLabel('♩', self))
        self.pitch_range_label = QLabel(self)
        status_layout.addWidget(self.pitch_range_label)
        status_layout.addStretch()

        status_layout.addWidget(QLabel('🔊', self))
        self.velocity_range_label = QLabel(self)
        status_layout.addWidget(self.velocity_range_label)

        notes_widget = QWidget(self)
        notes_layout = QHBoxLayout(notes_widget)
        notes_layout.setContentsMargins(0, 0, 0, 0)

        notes_layout.addWidget(QLabel('∑', self))
        self.notes_count_label = QLabel(self)
        notes_layout.addWidget(self.notes_count_label)
        notes_layout.addStretch()

        notes_layout.addWidget(QLabel('∅', self))
        self.notes_buzzer_none_label = QLabel(self)
        notes_layout.addWidget(self.notes_buzzer_none_label)
        notes_layout.addStretch()

        notes_layout.addWidget(QLabel('➊', self))
        self.notes_buzzer_1_label = QLabel(self)
        notes_layout.addWidget(self.notes_buzzer_1_label)
        notes_layout.addStretch()

        notes_layout.addWidget(QLabel('➋', self))
        self.notes_buzzer_2_label = QLabel(self)
        notes_layout.addWidget(self.notes_buzzer_2_label)
        notes_layout.addStretch()

        notes_layout.addWidget(QLabel('➌', self))
        self.notes_buzzer_3_label = QLabel(self)
        notes_layout.addWidget(self.notes_buzzer_3_label)
        notes_layout.addStretch()

        notes_layout.addWidget(QLabel('⚠️', self))
        self.notes_error_label = QLabel('?', self)
        notes_layout.addWidget(self.notes_error_label)

        layout.addWidget(title_widget)
        layout.addWidget(status_widget)
        layout.addWidget(notes_widget)

        self.update_track()

    def enterEvent(self, event: QEnterEvent) -> None:
        self.hover_changed.emit(self.track)
        return super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        self.hover_changed.emit(None)
        return super().leaveEvent(event)

    def update_track(self):
        self.notes_count_label.setText(str(self.track.notes_count))
        buzzers = self.track.buzzers_usage
        self.notes_buzzer_none_label.setText(str(buzzers[Buzzer.NONE]))
        self.notes_buzzer_1_label.setText(str(buzzers[Buzzer.BUZZER_1]))
        self.notes_buzzer_2_label.setText(str(buzzers[Buzzer.BUZZER_2]))
        self.notes_buzzer_3_label.setText(str(buzzers[Buzzer.BUZZER_3]))
        self.notes_error_label.setText(str(self.track.error_notes_count))
        self.duration_label.setText(f'{self.track.duration / 1000000:.2f} s')
        self.pitch_range_label.setText(f'{self.track.min_pitch}-{self.track.max_pitch}')
        self.velocity_range_label.setText(f'{self.track.min_velocity}-{self.track.max_velocity}')


class TracksListWidget(QWidget):
    track_changed = Signal(Track)
    move_up_requested = Signal(Track)
    move_down_requested = Signal(Track)
    select_track_requested = Signal(Track)
    hover_changed = Signal(object)

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
        track_widget.select_track_requested.connect(self.select_track_requested.emit)
        track_widget.hover_changed.connect(self.hover_changed.emit)
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

    def on_track_updated(self):
        for i in range(self.vbox_layout.count()):
            item = self.vbox_layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, TrackWidget):
                widget.update_track()
