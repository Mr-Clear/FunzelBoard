from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QDoubleSpinBox, QLabel, QScrollArea
from song import Buzzer, Note

class NoteWidget(QWidget):
    note_changed = Signal(Note)
    hover_changed = Signal(object)

    def __init__(self, note: Note | None, parent=None):
        super().__init__(parent)
        self.note = note
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.start_spinner = QDoubleSpinBox(self)
        self.pitch_combobox = QComboBox(self)
        self.pitch_combobox.addItems([str(p) for p in range(128, 0, -1)])
        self.duration_spinner = QDoubleSpinBox(self)
        self.buzzer_selector = QComboBox(self)
        self.buzzer_selector.addItems(['None', '1', '2', '3', 'Any'])

        for sb in (self.start_spinner, self.duration_spinner):
            sb.setGroupSeparatorShown(True)
            sb.setDecimals(3)
            sb.setRange(0, 1_000_000)

        layout.addWidget(self.start_spinner)
        layout.addWidget(self.pitch_combobox)
        layout.addWidget(self.duration_spinner)
        layout.addWidget(self.buzzer_selector)

        self.start_spinner.valueChanged.connect(self._set_note_start)
        self.pitch_combobox.currentTextChanged.connect(self._set_note_pitch)
        self.duration_spinner.valueChanged.connect(self._set_note_duration)
        self.buzzer_selector.currentTextChanged.connect(self._set_note_buzzer)

        self.set_note(note)

    def enterEvent(self, event):
        if self.note:
            self.hover_changed.emit(self.note)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hover_changed.emit(None)
        super().leaveEvent(event)

    def set_note(self, note: Note | None):
        self.note = note
        if note:
            self.setEnabled(True)
            self.start_spinner.setValue(note.start_tick / 1000.0)
            self.pitch_combobox.setCurrentText(str(note.pitch))
            self.duration_spinner.setValue(note.duration / 1000.0)
            self.buzzer_selector.setCurrentIndex(note.buzzer.value)
        else:
            self.setEnabled(False)
            self.start_spinner.setValue(0)
            self.pitch_combobox.setCurrentText("1")
            self.duration_spinner.setValue(0)
            self.buzzer_selector.setCurrentIndex(0)

    def _set_note_start(self, start: float):
        if self.note:
            self.note.start_tick = int(start * 1000)
            self.note_changed.emit(self.note)

    def _set_note_pitch(self, pitch_str: str):
        if self.note:
            self.note.pitch = int(pitch_str)
            self.note_changed.emit(self.note)

    def _set_note_duration(self, duration: float):
        if self.note:
            self.note.duration = int(duration * 1000)
            self.note_changed.emit(self.note)

    def _set_note_buzzer(self, buzzer_str: str):
        if self.note:
            buzzer_map = {
                '1': Buzzer.BUZZER_1,
                '2': Buzzer.BUZZER_2,
                '3': Buzzer.BUZZER_3,
                'None': Buzzer.NONE,
                'Any': Buzzer.ANY
            }
            self.note.buzzer = buzzer_map.get(buzzer_str, Buzzer.ANY)
            self.note_changed.emit(self.note)


class NotesListWidget(QWidget):
    note_changed = Signal(Note)
    hover_changed = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vbox_layout = QVBoxLayout(self)
        self.setLayout(self.vbox_layout)

        self.hover_label = QLabel("Hover:", self)
        self.vbox_layout.addWidget(self.hover_label)

        self.hover = NoteWidget(None, self)
        self.vbox_layout.addWidget(self.hover)

        self.selected_label = QLabel("Selected:", self)
        self.vbox_layout.addWidget(self.selected_label)

        self.selected_container = QWidget(self)
        self.selected_layout = QVBoxLayout(self.selected_container)
        self.selected_layout.setContentsMargins(0, 0, 0, 0)
        self.selected_container.setLayout(self.selected_layout)

        stretch_container = QWidget(self)
        stretch_layout = QVBoxLayout(stretch_container)
        stretch_layout.setContentsMargins(0, 0, 0, 0)
        stretch_layout.addWidget(self.selected_container)
        stretch_layout.addStretch()

        self.selected_scroll = QScrollArea(self)
        self.selected_scroll.setWidgetResizable(True)
        self.selected_scroll.setWidget(stretch_container)
        self.vbox_layout.addWidget(self.selected_scroll)

        self.hover.note_changed.connect(self.note_changed)
        self.hover.hover_changed.connect(self.hover_changed)

    def set_hover_note(self, note: Note | None):
        self.hover.set_note(note)

        for i in range(self.selected_layout.count()):
            item = self.selected_layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, NoteWidget):
                if note and widget.note == note:
                    widget.setStyleSheet("background-color: lightgray;")
                    self.selected_scroll.ensureWidgetVisible(widget)
                else:
                    widget.setStyleSheet("")

    def set_selected_notes(self, notes: list[Note]):
        for i in reversed(range(self.selected_layout.count())):
            item = self.selected_layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.setParent(None)
        for note in sorted(notes, key=lambda n: (n.start_tick, n.pitch)):
            note_widget = NoteWidget(note, self)
            self.selected_layout.addWidget(note_widget)
            note_widget.note_changed.connect(self.note_changed)
