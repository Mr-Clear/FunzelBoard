
from typing import Optional
from PySide6.QtCore import Qt, QPointF, QTimer, QRectF, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QFont
from PySide6.QtWidgets import QWidget, QSizePolicy

from config import Config
from song import Note, Song, Track

def create_font(family: str, point_size: float) -> QFont:
    font = QFont(family)
    font.setPointSizeF(point_size)
    return font

class SongWidget(QWidget):
    hover_note_changed = Signal(object)
    hover_track_changed = Signal(object)

    track_added = Signal(Track)
    track_removed = Signal(Track)

    note_selection_changed = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(800, 400)
        self.setMouseTracking(True)
        self.mouse_position: QPointF | None = None
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
        self.song: Song = Song(name="Untitled", tracks=[])
        self.hover_track: Track | None = None
        self.hover_note: Note | None = None
        self.pressed_note: Note | None = None
        self.selected_notes: list[Note] = []

    def set_song(self, song: Song):
        for track in self.song.tracks:
            self.track_removed.emit(track)
        self.song = song
        for track in self.song.tracks:
            self.track_added.emit(track)
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
        if event.button() == Config.SELECT_MOUSE_BUTTON:
            self.pressed_note = self.hover_note
        else:
            self.pressed_note = None
        if event.button() == Config.DRAG_MOUSE_BUTTON:
            self._dragging = True
            self._drag_start = event.position()
            self._shift_start = self.shift
            self.setCursor(Config.DRAG_MOUSE_POINTER)

    def mouseMoveEvent(self, event):
        self.mouse_position = event.position()
        zoomed_pos = event.position() - self.shift
        if self._dragging:
            delta = event.position() - self._drag_start
            self.shift = self._shift_start + delta
            self.update()
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Config.SELECT_MOUSE_BUTTON and self.pressed_note == self.hover_note:
            last_selected = set(self.selected_notes)
            if event.modifiers() & Config.SELECT_NOTE_ADD_MODIFIER:
                if self.hover_note and self.hover_note not in self.selected_notes:
                    self.selected_notes.append(self.hover_note)
            elif event.modifiers() & Config.SELECT_NOTE_REMOVE_MODIFIER:
                if self.hover_note and self.hover_note in self.selected_notes:
                    self.selected_notes.remove(self.hover_note)
            elif event.modifiers() & Config.SELECT_NOTE_SPAN_MODIFIER:
                if self.hover_note and self.selected_notes:
                    first_note = self.selected_notes[0]
                    track = None
                    for t in self.song.tracks:
                        if first_note in t.notes:
                            track = t
                            break
                    if track and self.hover_note in track.notes:
                        first_index = track.notes.index(first_note)
                        hover_index = track.notes.index(self.hover_note)
                        start_index = min(first_index, hover_index)
                        end_index = max(first_index, hover_index)
                        self.selected_notes = track.notes[start_index:end_index + 1]
            else:
                self.selected_notes = [self.hover_note] if self.hover_note else []
            if set(self.selected_notes) != last_selected:
                self.note_selection_changed.emit(self.selected_notes)
                self.update()
        elif event.button() == Config.DRAG_MOUSE_BUTTON and self._dragging:
            self._dragging = False
            self.setCursor(Config.NORMAL_MOUSE_POINTER)
        self.pressed_note = None

    def paintEvent(self, event):
        self.shift = QPointF(min(self.shift.x(), self.min_shift_x), min(self.shift.y(), 0))

        last_hover_track = self.hover_track
        last_hover_note = self.hover_note
        self.hover_track = None
        self.hover_note = None

        p = QPainter(self)
        p.fillRect(self.rect(), Config.BACKGROUND_COLOR)
        p.save()
        y = self.pitch_height * 2 * self.zoom_y
        for i, track in enumerate(self.song.tracks):
            track_height = self._draw_track(p, i, y)
            track_end_y = y + track_height
            y = track_end_y + self.pitch_height * 4 * self.zoom_y
        p.restore()

        if last_hover_track != self.hover_track:
            self.hover_track_changed.emit(self.hover_track)
        if last_hover_note != self.hover_note:
            self.hover_note_changed.emit(self.hover_note)

    def time_to_x(self, tick: int) -> float:
        return float(tick) / 1000000. * self.second_width * self.zoom_x

    def _draw_track(self, p: QPainter, track_index: int, y_offset: float) -> float:
        track = self.song.tracks[track_index]
        height = (track.max_pitch - track.min_pitch) * self.pitch_height * self.zoom_y + self.pitch_height * self.zoom_y
        track_rect = QRectF(0, y_offset, self.time_to_x(track.duration), height)
        hovered = self.mouse_position is not None and track_rect.contains(self.mouse_position - self.shift)

        p.save()
        p.translate(self.shift)
        hover_pitch: int | None = None
        if hovered:
            self.hover_track = track
            p.fillRect(track_rect, Config.HOVER_TRACK_HIGHLIGHT_COLOR)
            p.setPen(QPen(Config.HOVER_TRACK_BORDER_COLOR, Config.HOVER_TRACK_BORDER_WIDTH))
            p.drawRect(track_rect)
            hover_pitch = int((y_offset + height - (self.mapFromGlobal(self.cursor().pos()).y() - self.shift.y())) // (self.pitch_height * self.zoom_y)) + track.min_pitch

        if self.pitch_height * self.zoom_y >= 3:
            for pitch in range(track.min_pitch - 1, track.max_pitch + 1):
                if (pitch + 1) % 12 == 0:
                    p.setPen(QPen(Config.GRID_COLOR_MAIN, 2))
                elif (pitch - track.min_pitch) % 2 == 1:
                    p.setPen(QPen(Config.GRID_COLOR_LIGHT, 1))
                else:
                    p.setPen(QPen(Config.GRID_COLOR_DARK, 1))
                y = y_offset + (track.pitch_range - pitch + track.min_pitch) * (self.pitch_height * self.zoom_y)
                p.drawLine(QPointF(0, y), QPointF(self.time_to_x(track.duration), y))
        else:
            for pitch in range((((track.min_pitch - 1) // 12) + 1) * 12 - 1, track.max_pitch + 1, 12):
                p.setPen(QPen(Config.GRID_COLOR_DARK, 1))
                y = y_offset + (track.pitch_range - pitch + track.min_pitch) * (self.pitch_height * self.zoom_y)
                p.drawLine(QPointF(0, y), QPointF(self.time_to_x(track.duration), y))

        for note in track.notes:
            x = self.time_to_x(note.start_tick)
            y = y_offset + (track.pitch_range - note.pitch + track.min_pitch) * (self.pitch_height * self.zoom_y)
            w = self.time_to_x(note.duration)
            h = self.pitch_height * self.zoom_y
            if w > 0 and h > 0:
                note_rect = QRectF(x, y, w, h)
                if self.mouse_position and hovered and note_rect.contains(self.mouse_position - self.shift):
                    if note in self.selected_notes:
                        c = Config.NOTE_HOVER_SELECTED_FILL_BASE_COLOR
                        p.setPen(QPen(Config.NOTE_HOVER_SELECTED_BORDER_COLOR, 1))
                    else:
                        c = Config.NOTE_HOVER_FILL_BASE_COLOR
                        p.setPen(QPen(Config.NOTE_HOVER_BORDER_COLOR, 1))
                    self.hover_note = note
                elif note in self.selected_notes:
                    c = Config.NOTE_SELECTED_FILL_BASE_COLOR
                    p.setPen(QPen(Config.NOTE_SELECTED_BORDER_COLOR, 1))
                else:
                    c = Config.NOTE_FILL_BASE_COLOR
                    p.setPen(QPen(Config.NOTE_BORDER_COLOR, 1))
                if track.velocity_range > 0:
                    c.setAlpha((note.velocity - track.min_velocity) * 255 // track.velocity_range)
                p.fillRect(note_rect, c)
                p.drawRect(note_rect)
        p.restore()

        if self.zoom_y > 0.2:
            p.save()
            p.translate(QPointF(0, self.shift.y()))
            p.setPen(QPen(QColor.fromRgba(0xAAFFFFFF), 1))

            p.save()
            p.rotate(-90)
            p.setFont(create_font("Sans", self.pitch_height * self.zoom_y * 2))
            fm = p.fontMetrics()
            if hovered:
                p.setPen(QPen(Config.TRACK_TEXT_COLOR_HOVER))
            else:
                p.setPen(QPen(Config.TRACK_TEXT_COLOR))
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
                if hover_pitch == pitch:
                    p.setPen(QPen(Config.TRACK_TEXT_COLOR_HOVER))
                else:
                    p.setPen(QPen(Config.TRACK_TEXT_COLOR))
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
