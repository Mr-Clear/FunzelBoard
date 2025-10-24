from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class Config:
    BACKGROUND_COLOR = QColor(0x222222)
    GRID_COLOR_LIGHT = QColor.fromRgba(0x88888888)
    GRID_COLOR_DARK = QColor.fromRgba(0x44888888)
    NOTE_BORDER_COLOR = QColor(0x2244FF)
    NOTE_FILL_BASE_COLOR = QColor(0x64, 0xB4, 0xFF)

    DRAG_MOUSE_BUTTON = Qt.RightButton           # type: ignore

    NORMAL_MOUSE_POINTER = Qt.ArrowCursor        # type: ignore
    DRAG_MOUSE_POINTER = Qt.ClosedHandCursor     # type: ignore

    ZOOM_X_MODIFIER = Qt.ControlModifier         # type: ignore
    ZOOM_Y_MODIFIER = Qt.ShiftModifier           # type: ignore

    MIN_ZOOM_X = 0.01
    MIN_ZOOM_Y = 0.1
    MAX_ZOOM_X = 10.0
    MAX_ZOOM_Y = 2.0