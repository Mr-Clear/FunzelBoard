from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class Config:
    BACKGROUND_COLOR = QColor(0x222222)
    GRID_COLOR_LIGHT = QColor.fromRgba(0x88888888)
    GRID_COLOR_DARK = QColor.fromRgba(0x44888888)
    GRID_COLOR_MAIN = QColor.fromRgba(0xAA888888)
    NOTE_BORDER_COLOR = QColor(0x2244FF)
    NOTE_FILL_BASE_COLOR = QColor(0x64, 0xB4, 0xFF)
    HOVER_TRACK_HIGHLIGHT_COLOR = QColor.fromRgba(0x05FFFFFF)
    HOVER_TRACK_BORDER_COLOR = QColor.fromRgba(0x33FFFFFF)
    HOVER_TRACK_BORDER_WIDTH = 1

    DRAG_MOUSE_BUTTON = Qt.RightButton           # pyright: ignore[reportAttributeAccessIssue]

    NORMAL_MOUSE_POINTER = Qt.ArrowCursor        # pyright: ignore[reportAttributeAccessIssue]
    DRAG_MOUSE_POINTER = Qt.ClosedHandCursor     # pyright: ignore[reportAttributeAccessIssue]

    ZOOM_X_MODIFIER = Qt.ControlModifier         # pyright: ignore[reportAttributeAccessIssue]
    ZOOM_Y_MODIFIER = Qt.ShiftModifier           # pyright: ignore[reportAttributeAccessIssue]

    MIN_ZOOM_X = 0.01
    MIN_ZOOM_Y = 0.1
    MAX_ZOOM_X = 10.0
    MAX_ZOOM_Y = 2.0