import json
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from dataclasses import dataclass, fields

@dataclass
class ConfigClass:
    BACKGROUND_COLOR = QColor(0x222222)
    GRID_COLOR_LIGHT = QColor.fromRgba(0x88888888)
    GRID_COLOR_DARK = QColor.fromRgba(0x44888888)
    GRID_COLOR_MAIN = QColor.fromRgba(0xAA888888)
    NOTE_BORDER_COLOR = QColor(0x2244FF)
    NOTE_HOVER_BORDER_COLOR = QColor.fromRgb(0x4488FF)
    NOTE_SELECTED_BORDER_COLOR = QColor(0xFFFF44)
    NOTE_HOVER_SELECTED_BORDER_COLOR = QColor(0xFFAA00)
    NOTE_FILL_COLOR = QColor(0x888888)
    NOTE_BUZZER_FILL_COLORS = [QColor(0x00FF00), QColor(0x0000FF), QColor(0x00FFFF)]
    NOTE_ERROR_FILL_COLOR = QColor(0xFF4444)
    HOVER_TRACK_HIGHLIGHT_COLOR = QColor.fromRgba(0x05FFFFFF)
    HOVER_TRACK_BORDER_COLOR = QColor.fromRgba(0x33FFFFFF)
    HOVER_TRACK_BORDER_WIDTH = 1
    TRACK_TEXT_COLOR = QColor.fromRgba(0x88FFFFFF)
    TRACK_TEXT_COLOR_HOVER = QColor.fromRgba(0xAAFFFFFF)
    SELECTION_FRAME_BORDER_COLOR = QColor.fromRgba(0xFF55FF55)
    SELECTION_FRAME_COLOR = QColor.fromRgba(0x1155FF55)
    SELECTION_FRAME_NOTE_BORDER_COLOR = QColor.fromRgba(0xFFAAFFAA)
    SELECTION_FRAME_NOTE_FILL_BASE_COLOR = QColor.fromRgba(0x3355FF55)

    SELECT_MOUSE_BUTTON = Qt.MouseButton.LeftButton
    DRAG_MOUSE_BUTTON = Qt.MouseButton.RightButton

    NORMAL_MOUSE_POINTER = Qt.CursorShape.ArrowCursor
    DRAG_MOUSE_POINTER = Qt.CursorShape.ClosedHandCursor

    ZOOM_X_MODIFIER = Qt.KeyboardModifier.ControlModifier
    ZOOM_Y_MODIFIER = Qt.KeyboardModifier.ShiftModifier
    SELECT_NOTE_ADD_MODIFIER = Qt.KeyboardModifier.ControlModifier
    SELECT_NOTE_REMOVE_MODIFIER = Qt.KeyboardModifier.AltModifier
    SELECT_NOTE_SPAN_MODIFIER = Qt.KeyboardModifier.ShiftModifier

    MIN_ZOOM_X = 0.01
    MIN_ZOOM_Y = 0.1
    MAX_ZOOM_X = 10.0
    MAX_ZOOM_Y = 2.0

    INDICATE_VELOCITY = False

    last_opened_directory = ''
    last_song = ''

    @staticmethod
    def _serialize_value(value):
        if isinstance(value, QColor):
            return f"{value.rgba():08X}"
        elif isinstance(value, (Qt.MouseButton, Qt.CursorShape, Qt.KeyboardModifier)):
            return value.name
        else:
            return value

    @staticmethod
    def _deserialize_value(orig, value):
        if isinstance(orig, QColor):
            return QColor.fromRgba(int(value, 16))
        elif isinstance(orig, Qt.MouseButton):
            return Qt.MouseButton(value)
        elif isinstance(orig, Qt.CursorShape):
            return Qt.CursorShape(value)
        elif isinstance(orig, Qt.KeyboardModifier):
            return Qt.KeyboardModifier(value)
        else:
            return value

    @staticmethod
    def load(fname: str):
        try:
            with open(fname, 'r') as f:
                data = json.load(f)
                for k, v in data.items():
                    if hasattr(Config, k):
                        orig = getattr(Config, k)
                        setattr(Config, k, ConfigClass._deserialize_value(orig, v))
        except Exception as e:
            print(f"Could not load config: {e}")

    @staticmethod
    def save(fname: str):
        try:
            data = {}
            for k in vars(Config):
                if k.startswith("__") or callable(getattr(Config, k)):
                    continue
                v = getattr(Config, k)
                data[k] = ConfigClass._serialize_value(v)
            with open(fname, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Could not save config: {e}")

Config = ConfigClass()
