
from PySide6.QtCore import Qt, QPointF, QTimer, QRectF
from PySide6.QtGui import QPainter, QPen, QColor, QFont
from PySide6.QtWidgets import QWidget, QSizePolicy

from config import Config
from midi_loader import Track

def create_font(family: str, point_size: float) -> QFont:
    font = QFont(family)
    font.setPointSizeF(point_size)
    return font

class SongWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(800, 400)
        self.notes = []  # Each note: (start_tick, duration, pitch)
        self.playhead_tick = 0
        self.is_playing = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.advance_playhead)

        self.zoom_x = 1.0
        self.zoom_y = 1.0
        self.pitch_height = 10
        self.second_width = 100
        self.shift = QPointF(0, 0)
        self.min_shift_x = 0
        self._dragging = False
        self._drag_start = QPointF()
        self._shift_start = QPointF()
        self.tracks: list[Track] = []


    def add_tracks(self, tracks):
        self.tracks.extend(tracks)
        self.playhead_tick = 0
        self.update()

    def start_playback(self):
        self.is_playing = True
        self.timer.start(30)

    def stop_playback(self):
        self.is_playing = False
        self.timer.stop()
        self.playhead_tick = 0
        self.update()

    def advance_playhead(self):
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Config.DRAG_MOUSE_BUTTON:
            self._dragging = True
            self._drag_start = event.position()
            self._shift_start = self.shift
            self.setCursor(Config.DRAG_MOUSE_POINTER)

    def mouseMoveEvent(self, event):
        if self._dragging:
            delta = event.position() - self._drag_start
            self.shift = self._shift_start + delta
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Config.DRAG_MOUSE_BUTTON and self._dragging:
            self._dragging = False
            self.setCursor(Config.NORMAL_MOUSE_POINTER)

    def paintEvent(self, event):
        self.shift = QPointF(min(self.shift.x(), self.min_shift_x), min(self.shift.y(), 0))

        p = QPainter(self)
        p.fillRect(self.rect(), Config.BACKGROUND_COLOR)
        p.save()
        y = self.pitch_height * 2 * self.zoom_y
        for i, track in enumerate(self.tracks):
            y += self._draw_track(p, i, y) + self.pitch_height * 4 * self.zoom_y
        p.restore()

    def time_to_x(self, tick: int) -> float:
        return float(tick) / 1000000. * self.second_width * self.zoom_x

    def _draw_track(self, p: QPainter, track_index: int, y_offset: float) -> float:
        track = self.tracks[track_index]
        height = (track.max_pitch - track.min_pitch) * self.pitch_height * self.zoom_y + self.pitch_height

        p.save()
        p.translate(self.shift)
        for pitch in range(track.min_pitch - 1, track.max_pitch + 1):
            if (pitch - track.min_pitch) % 2 == 1:
                p.setPen(QPen(Config.GRID_COLOR_LIGHT, 1))
            else:
                p.setPen(QPen(Config.GRID_COLOR_DARK, 1))
            y = y_offset + (track.pitch_range - pitch + track.min_pitch) * (self.pitch_height * self.zoom_y)
            p.drawLine(QPointF(0, y), QPointF(self.time_to_x(track.duration), y))

        for note in track.notes:
            x = self.time_to_x(note.start_tick)
            y = y_offset + (track.pitch_range - note.pitch + track.min_pitch) * (self.pitch_height * self.zoom_y)
            w = self.time_to_x(note.duration)
            h = self.pitch_height * self.zoom_y
            c = Config.NOTE_FILL_BASE_COLOR
            c.setAlpha((note.velocity - track.min_velocity) * 255 // track.velocity_range)
            p.fillRect(QRectF(x, y, w, h), c)
            p.setPen(QPen(Config.NOTE_BORDER_COLOR, 1))
            p.drawRect(QRectF(x, y, w, h))
        p.restore()

        if self.zoom_y > 0.2:
            p.save()
            p.translate(QPointF(0, self.shift.y()))
            p.setPen(QPen(QColor.fromRgba(0xAAFFFFFF), 1))

            p.save()
            p.rotate(-90)
            p.setFont(create_font("Sans", self.pitch_height * self.zoom_y * 2))
            fm = p.fontMetrics()
            p.drawText(QPointF(-y_offset - (height + fm.horizontalAdvance(f'{track.name}')) / 2, fm.ascent() * 0.8), f'{track.name}')
            title_height = fm.height() * 0.6
            p.restore()

            p.setFont(create_font("Mono", self.pitch_height * self.zoom_y * 0.8))
            max_pitch_width = p.fontMetrics().horizontalAdvance('000')
            for pitch in range(track.min_pitch, track.max_pitch + 1):
                y = y_offset + (track.pitch_range - pitch + track.min_pitch) * (self.pitch_height * self.zoom_y)
                pitch_text = f'{pitch}'
                pitch_width = p.fontMetrics().horizontalAdvance(pitch_text)
                note_text = SongWidget.pitch_to_note_name(pitch)
                pitch_text = f'{pitch_text} {note_text}'
                p.drawText(QPointF(title_height + max_pitch_width - pitch_width, y + self.pitch_height * self.zoom_y * 0.9), pitch_text)
                self.min_shift_x = title_height + p.fontMetrics().horizontalAdvance('000 C#4')
            p.restore()

        return height

    def wheelEvent(self, event):
        # Zoom in/out with mouse wheel, centered on mouse position
        delta = event.angleDelta().y()
        factor = 1.15 if delta > 0 else 1/1.15
        old_zoom_x = self.zoom_x
        old_zoom_y = self.zoom_y

        # Optionally: hold Ctrl for x-zoom, Shift for y-zoom, else both
        modifiers = event.modifiers()
        pos = event.position()
        if modifiers & Config.ZOOM_X_MODIFIER:
            self.zoom_x *= factor
        elif modifiers & Config.ZOOM_Y_MODIFIER:
            self.zoom_y *= factor
        else:
            self.zoom_x *= factor
            self.zoom_y *= factor

        # Clamp zoom
        self.zoom_x = max(Config.MIN_ZOOM_X, min(self.zoom_x, Config.MAX_ZOOM_X))
        self.zoom_y = max(Config.MIN_ZOOM_Y, min(self.zoom_y, Config.MAX_ZOOM_Y))

        # Optional: keep mouse position stable (zoom to cursor)
        # Calculate logical position before and after zoom, adjust shift accordingly
        rel = pos - self.shift
        if modifiers & Config.ZOOM_X_MODIFIER or modifiers & Config.ZOOM_Y_MODIFIER or True:
            # Always zoom to cursor for user-friendliness
            scale_x = self.zoom_x / old_zoom_x
            scale_y = self.zoom_y / old_zoom_y
            self.shift = pos - QPointF(rel.x() * scale_x, rel.y() * scale_y)

        self.update()

    @staticmethod
    def pitch_to_note_name(pitch: int) -> str:
        names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (pitch // 12) - 1
        name = names[pitch % 12]
        return f'{name}{octave}'