from PySide6.QtGui import QCloseEvent, QEnterEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, \
                              QLineEdit, QToolButton
from PySide6.QtCore import Signal, QEvent, QTimer

from song import Song, Buzzer

class SongDetailsWidget(QWidget):
    song_name_changed = Signal(str)
    save_requested = Signal()
    save_as_requested = Signal()
    load_requested = Signal()
    export_requested = Signal()
    undo_requested = Signal()
    redo_requested = Signal()

    def __init__(self, song: Song | None, parent=None):
        super().__init__(parent)
        self.song = song
        layout = QVBoxLayout(self)
        self.name_text = QLineEdit()
        layout.addWidget(self.name_text)
        self.name_text.textChanged.connect(self._on_name_changed)

        buttons_widget = QWidget(self)
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)

        save_button = QToolButton(self)
        save_button.setText("💾")
        buttons_layout.addWidget(save_button)
        save_button.clicked.connect(lambda: self.save_requested.emit())

        save_as_button = QToolButton(self)
        save_as_button.setText("💾✏️")
        buttons_layout.addWidget(save_as_button)
        save_as_button.clicked.connect(lambda: self.save_as_requested.emit())

        load_button = QToolButton(self)
        load_button.setText("📂")
        buttons_layout.addWidget(load_button)
        load_button.clicked.connect(lambda: self.load_requested.emit())

        buttons_layout.addStretch()

        export_button = QToolButton(self)
        export_button.setText("📤")
        buttons_layout.addWidget(export_button)
        export_button.clicked.connect(lambda: self.export_requested.emit())

        buttons_layout.addStretch()

        undo_button = QToolButton(self)
        undo_button.setText("↩️")
        undo_button.setEnabled(False)
        buttons_layout.addWidget(undo_button)
        undo_button.clicked.connect(lambda: self.undo_requested.emit())

        redo_button = QToolButton(self)
        redo_button.setText("↪️")
        redo_button.setEnabled(False)
        buttons_layout.addWidget(redo_button)
        redo_button.clicked.connect(lambda: self.redo_requested.emit())

        layout.addWidget(buttons_widget)

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
        if self.song:
            self.song.remove_change_listener(self.update_labels)
        self.song = song
        self.name_text.setText(song.name if song else "No Song")
        self.update_labels()
        if song:
            song.add_change_listener(self.update_labels)

    def _on_name_changed(self, text: str):
        if self.song and self.song.name != text:
            self.song.name = text
            self.song_name_changed.emit(text)

    def update_labels(self):
        if self.song:
            self.duration_label.setText(f'{self.song.duration_us / 1000000:.2f} s')
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

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.song:
            self.song.remove_change_listener(self.update_labels)
        return super().closeEvent(event)
