from PySide6.QtCore import QLocale
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QDoubleSpinBox, QLabel, QScrollArea
from song import Note

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
