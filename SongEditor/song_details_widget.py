from PySide6.QtGui import QEnterEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, \
                              QLineEdit, QToolButton
from PySide6.QtCore import Signal, QEvent, QTimer

from song import Song, Buzzer

class SongDetailsWidget(QWidget):
    song_name_changed = Signal(str)

    def __init__(self, song: Song | None, parent=None):
        super().__init__(parent)
        self.song = song
        layout = QVBoxLayout(self)
        self.name_text = QLineEdit()
        layout.addWidget(self.name_text)
        self.name_text.textChanged.connect(self._on_name_changed)

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
        layout.addWidget(status_widget)

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

        layout.addWidget(notes_widget)

        self.set_song(song)

    def set_song(self, song: Song | None):
        self.song = song
        self.name_text.setText(song.name if song else "No Song")
        self.update_labels()

    def _on_name_changed(self, text: str):
        if self.song and self.song.name != text:
            self.song.name = text
            self.song_name_changed.emit(text)

    def update_labels(self):
        if self.song:
            self.duration_label.setText(f'{self.song.duration / 1000000:.2f} s')
            min_pitch, max_pitch = self.song.pitch_range
            self.pitch_range_label.setText(f'{min_pitch}-{max_pitch}')
            min_velocity, max_velocity = self.song.velocity_range
            self.velocity_range_label.setText(f'{min_velocity}-{max_velocity}')
            self.notes_count_label.setText(str(sum(len(track.notes) for track in self.song.tracks)))
            buzzers_usage = {buzzer: 0 for buzzer in Buzzer}
            for track in self.song.tracks:
                for note in track.notes:
                    buzzers_usage[note.buzzer] += 1
            self.notes_buzzer_none_label.setText(str(buzzers_usage[Buzzer.NONE]))
            self.notes_buzzer_1_label.setText(str(buzzers_usage[Buzzer.BUZZER_1]))
            self.notes_buzzer_2_label.setText(str(buzzers_usage[Buzzer.BUZZER_2]))
            self.notes_buzzer_3_label.setText(str(buzzers_usage[Buzzer.BUZZER_3]))
            self.notes_error_label.setText(str(sum(track.error_notes_count for track in self.song.tracks)))
        else:
            self.duration_label.setText("0.00 s")
            self.pitch_range_label.setText("0-0")
            self.velocity_range_label.setText("0-0")
            self.notes_count_label.setText("0")
            self.notes_buzzer_none_label.setText("0")
            self.notes_buzzer_1_label.setText("0")
            self.notes_buzzer_2_label.setText("0")
            self.notes_buzzer_3_label.setText("0")
            self.notes_error_label.setText("0")

        QTimer.singleShot(0, lambda: self.setMaximumHeight(self.sizeHint().height()))
