from typing import Any
from PySide6.QtCore import Signal, QItemSelectionModel, QEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QTableView, \
                              QDoubleSpinBox, QLabel, QScrollArea, QToolButton, QStyledItemDelegate
from song import Buzzer, Note
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex, QPersistentModelIndex



class NotesTableModel(QAbstractTableModel):
    def __init__(self, notes: list[Note], parent=None):
        super().__init__(parent)
        self.notes = notes
        self.buzzer_icons = {
            Buzzer.NONE: '∅',
            Buzzer.BUZZER_1: '➊',
            Buzzer.BUZZER_2: '➋',
            Buzzer.BUZZER_3: '➌'
        }

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        return len(self.notes)

    def columnCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        return 4  # Columns: Start, Duration, Pitch, Buzzer

    def set_node_list(self, notes: list[Note]):
        self.beginResetModel()
        self.notes = notes
        self.endResetModel()

    def data(self, index: QModelIndex | QPersistentModelIndex, /, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None

        note = self.notes[index.row()]
        column = index.column()

        if column == 0:  # Start
            return note.start_us / 1000.0
        elif column == 1:  # Duration
            return note.duration_us / 1000.0
        elif column == 2:  # Pitch
            return note.pitch
        elif column == 3:  # Buzzer
            return self.buzzer_icons[note.buzzer]
        return None

    def setData(self, index: QModelIndex | QPersistentModelIndex, value, role: int = Qt.ItemDataRole.DisplayRole) -> bool:
        if not index.isValid() or role != Qt.ItemDataRole.EditRole:
            return False

        note = self.notes[index.row()]
        column = index.column()

        try:
            if column == 0:  # Start
                note.start_us = int(float(value) * 1000)
            elif column == 1:  # Duration
                note.duration_us = int(float(value) * 1000)
            elif column == 2:  # Pitch
                note.pitch = int(value)
            elif column == 3:  # Buzzer
                note.buzzer = Buzzer(int(value))
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole])
            return True
        except (ValueError, KeyError):
            return False

    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return ["Start", "Dur.", "♩", "🔈"][section]
        return None


class NotesListWidget(QWidget):
    note_changed = Signal(Note)
    hover_changed = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vbox_layout = QVBoxLayout(self)
        self.setLayout(self.vbox_layout)

        self.hovered_note = QTableView(self)
        self.hovered_note_model = NotesTableModel([], self)
        self.hovered_note.setModel(self.hovered_note_model)
        self.hovered_note.setMaximumHeight(64)
        self._setup_table_view(self.hovered_note)
        self.vbox_layout.addWidget(self.hovered_note)

        selected_title_widget = QWidget(self)
        selected_title_layout = QHBoxLayout(selected_title_widget)
        selected_title_layout.setContentsMargins(0, 0, 0, 0)
        self.selected_label = QLabel("Selected:", self)
        selected_title_layout.addWidget(self.selected_label)

        self.buzzer_buttons: list[tuple[QToolButton, str, Buzzer]] = [ # pyright: ignore[reportAttributeAccessIssue]
            (None, '∅', Buzzer.NONE),
            (None, '➊', Buzzer.BUZZER_1),
            (None, '➋', Buzzer.BUZZER_2),
            (None, '➌', Buzzer.BUZZER_3)]
        for i in range(len(self.buzzer_buttons)):
            btn = QToolButton(self)
            btn.setText(self.buzzer_buttons[i][1])
            btn.setCheckable(True)
            self.buzzer_buttons[i] = (btn, self.buzzer_buttons[i][1], self.buzzer_buttons[i][2])
            selected_title_layout.addWidget(btn)
            btn.clicked.connect(lambda checked, b=self.buzzer_buttons[i][2]: self._set_selected_buzzer(b))

        self.vbox_layout.addWidget(selected_title_widget)

        self.selected_notes_view = QTableView(self)
        self.selected_notes_model = NotesTableModel([], self)
        self.selected_notes_view.setModel(self.selected_notes_model)
        self._setup_table_view(self.selected_notes_view)
        self.vbox_layout.addWidget(self.selected_notes_view)
        self.selected_notes_view.viewport().installEventFilter(self)
        self.selected_notes_view.setMouseTracking(True)

        self.selected_notes: list[Note] = []
        self.set_selected_notes([])

    def set_hover_note(self, note: Note | None):
        self.hovered_note_model.set_node_list([note] if note else [])
        if note:
            try:
                row = self.selected_notes.index(note)
                index = self.selected_notes_model.index(row, 0)
                self.selected_notes_view.selectionModel().select(
                    index,
                    QItemSelectionModel.SelectionFlag.ClearAndSelect | QItemSelectionModel.SelectionFlag.Rows
                )
                self.selected_notes_view.scrollTo(index)
            except ValueError:
                pass  # Note not in list

    def set_selected_notes(self, notes: list[Note]):
        self.selected_notes = sorted(notes, key=lambda n: (n.start_us, n.duration_us, n.pitch, n.buzzer.value))
        self.selected_notes_model.set_node_list(self.selected_notes)
        if notes:
            for btn, _, b in self.buzzer_buttons:
                btn.setEnabled(True)
        else:
            for btn, _, b in self.buzzer_buttons:
                btn.setEnabled(False)

        buzzers = set()
        for note in notes:
            buzzers.add(note.buzzer)
        for btn, _, b in self.buzzer_buttons:
            btn.setChecked(b in buzzers)

    def _set_selected_buzzer(self, buzzer: Buzzer):
        for note in self.selected_notes:
            note.buzzer = buzzer
            self.note_changed.emit(note)
        for btn, _, b in self.buzzer_buttons:
            btn.setChecked(b == buzzer)

    def _setup_table_view(self, table_view: QTableView):
        header = table_view.horizontalHeader()
        header.setStretchLastSection(False)
        header.setMinimumSectionSize(20)
        table_view.verticalHeader().setVisible(False)
        # Columns: 0=Start, 1=Dur., 2=♩, 3=🔈
        table_view.setColumnWidth(0, 70)
        table_view.setColumnWidth(1, 70)
        table_view.setColumnWidth(2, 38)
        table_view.setColumnWidth(3, 26)

        table_view.setItemDelegateForColumn(0, TimeDelegate(table_view))
        table_view.setItemDelegateForColumn(1, TimeDelegate(table_view))
        table_view.setItemDelegateForColumn(2, PitchDelegate(table_view))
        table_view.setItemDelegateForColumn(3, BuzzerDelegate(self.hovered_note_model.buzzer_icons, table_view))

    def eventFilter(self, obj, event):
        # Track mouse movements over the selected_notes_view viewport
        if obj == self.selected_notes_view.viewport():
            if event.type() == QEvent.Type.MouseMove:
                pos = event.position().toPoint()
                index = self.selected_notes_view.indexAt(pos)
                if index.isValid():
                    row = index.row()
                    if 0 <= row < len(self.selected_notes):
                        note = self.selected_notes[row]
                        self.hover_changed.emit(note)
                else:
                    self.hover_changed.emit(None)
            elif event.type() == QEvent.Type.Leave:
                self.hover_changed.emit(None)
        return super().eventFilter(obj, event)


class TimeDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QDoubleSpinBox(parent)
        editor.setDecimals(3)
        editor.setMinimum(0.0)
        editor.setMaximum(10_000_000.0)
        return editor

    def setEditorData(self, editor: QWidget, index):
        if not isinstance(editor, QDoubleSpinBox):
            return
        value = index.data(Qt.ItemDataRole.DisplayRole)
        if value is not None:
            editor.setValue(float(value))

    def setModelData(self, editor: QWidget, model, index):
        if not isinstance(editor, QDoubleSpinBox):
            return
        value = editor.value()
        model.setData(index, value, Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        rect = option.rect
        rect.setWidth(120)
        editor.setGeometry(rect)


class PitchDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems([str(p) for p in range(127, -1, -1)])  # MIDI pitches 0-127
        return editor

    def setEditorData(self, editor: QWidget, index):
        if not isinstance(editor, QComboBox):
            return
        value = index.data(Qt.ItemDataRole.DisplayRole)
        if value is not None:
            editor.setCurrentText(str(value))

    def setModelData(self, editor: QWidget, model, index):
        if not isinstance(editor, QComboBox):
            return
        value = editor.currentText()
        model.setData(index, int(value), Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        rect = option.rect
        rect.setWidth(60)
        editor.setGeometry(rect)


class BuzzerDelegate(QStyledItemDelegate):
    def __init__(self, buzzer_icons: dict, parent=None):
        super().__init__(parent)
        self.buzzer_icons = buzzer_icons
        self.reverse_icons = {v: k for k, v in buzzer_icons.items()}

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(list(self.buzzer_icons.values()))
        return editor

    def setEditorData(self, editor: QWidget, index):
        if not isinstance(editor, QComboBox):
            return
        value = index.data(Qt.ItemDataRole.DisplayRole)
        if value is not None:
            editor.setCurrentText(value)

    def setModelData(self, editor: QWidget, model, index):
        if not isinstance(editor, QComboBox):
            return
        icon = editor.currentText()
        buzzer = self.reverse_icons.get(icon)
        if buzzer:
            model.setData(index, buzzer.value, Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        rect = option.rect
        rect.setWidth(40)
        editor.setGeometry(rect)
