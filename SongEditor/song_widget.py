from enum import Enum
from typing import Iterable

from PySide6.QtCore import Qt, QEvent, QPointF, QTimer, QRectF, Signal, QLineF
from PySide6.QtGui import QKeyEvent, QPainter, QPen, QColor, QFont
from PySide6.QtWidgets import QWidget, QSizePolicy

from config import Config
from song import Note, Song, Track, Buzzer

class KeysStatus(Enum):
    NONE = 1
    ADD = 2
    REMOVE = 3
    SPAN = 4
    TOGGLE = 5
    SCALE_X = 6
    SCALE_Y = 7

def create_font(family: str, point_size: float) -> QFont:
    font = QFont(family)
    font.setPointSizeF(point_size)
    return font

class SongWidget(QWidget):
    hover_note_changed = Signal(object)
    hover_track_changed = Signal(object)

    track_added = Signal(Track)
    track_removed = Signal(Track)

    key_status_update = Signal(KeysStatus)

    note_selection_changed = Signal(list)

    song_changed = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(800, 400)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # Enable focus for key events
        self._mouse_position: QPointF | None = None
        self._notes = []  # Each note: (start_tick, duration, pitch)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.advance_playhead)

        self._zoom_x = 1.0
        self._zoom_y = 1.0
        self._pitch_height = 10
        self._second_width = 100
        self._shift = QPointF(0, 0)
        self._min_shift_x = 0
        self._dragging = False
        self._drag_start = QPointF()
        self._shift_start = QPointF()
        self._song: Song = Song(name="Untitled", tracks=[])
        self._hover_track: Track | None = None
        self._hover_note: Note | None = None
        self._pressed_note: Note | None = None
        self._selected_notes: list[Note] = []
        self._highlighted_track: Track | None = None
        self._highlighted_note: Note | None = None
        self._error_notes: set[Note] = set()
        self._selection_frame_start: QPointF | None = None
        self._selection_frame: QRectF | None = None
        self._keyboard_modifiers: set[Qt.KeyboardModifier] = set()
        self._keys_status: KeysStatus = KeysStatus.NONE

    def set_song(self, song: Song):
        if self._song:
            self._song.remove_change_listener(self.update)
        for track in self._song.tracks:
            self.track_removed.emit(track)
        self._song = song
        for track in self._song.tracks:
            self.track_added.emit(track)
        self.update()
        self._song.add_change_listener(self.update)
        self.song_changed.emit(song)

    @property
    def song(self) -> Song:
        return self._song

    def advance_playhead(self):
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Config.SELECT_MOUSE_BUTTON:
            self._pressed_note = self._hover_note
            self._selection_frame_start = event.position()
        else:
            self._pressed_note = None
        if event.button() == Config.DRAG_MOUSE_BUTTON:
            self._dragging = True
            self._drag_start = event.position()
            self._shift_start = self._shift
            self.setCursor(Config.DRAG_MOUSE_POINTER)
        self._update_keys_status()

    def mouseMoveEvent(self, event):
        self._mouse_position = event.position()

        if self._dragging:
            delta = event.position() - self._drag_start
            self._shift = self._shift_start + delta
            self.update()
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Config.SELECT_MOUSE_BUTTON:
            last_selected = set(self._selected_notes)
            selection_frame_distance = QLineF(self._selection_frame_start, event.position()).length() if self._selection_frame_start else 0
            if selection_frame_distance > 2 and self.selection_frame_notes:
                if event.modifiers() & Config.SELECT_NOTE_ADD_MODIFIER or event.modifiers() & Config.SELECT_NOTE_SPAN_MODIFIER:
                    for note in self.selection_frame_notes:
                        if note not in self._selected_notes:
                            self._selected_notes.append(note)
                elif event.modifiers() & Config.SELECT_NOTE_REMOVE_MODIFIER:
                    for note in self.selection_frame_notes:
                        if note in self._selected_notes:
                            self._selected_notes.remove(note)
                else:
                    self._selected_notes = self.selection_frame_notes.copy()
            elif self._pressed_note == self._hover_note:
                if event.modifiers() & Config.SELECT_NOTE_ADD_MODIFIER:
                    if self._hover_note and self._hover_note not in self._selected_notes:
                        self._selected_notes.append(self._hover_note)
                elif event.modifiers() & Config.SELECT_NOTE_REMOVE_MODIFIER:
                    if self._hover_note and self._hover_note in self._selected_notes:
                        self._selected_notes.remove(self._hover_note)
                elif event.modifiers() & Config.SELECT_NOTE_SPAN_MODIFIER:
                    if self._hover_note and self._selected_notes:
                        first_note = self._selected_notes[0]
                        track = None
                        for t in self._song.tracks:
                            if first_note in t.notes:
                                track = t
                                break
                        if track and self._hover_note in track.notes:
                            first_index = track.notes.index(first_note)
                            hover_index = track.notes.index(self._hover_note)
                            start_index = min(first_index, hover_index)
                            end_index = max(first_index, hover_index)
                            self._selected_notes = track.notes[start_index:end_index + 1]
                else:
                    self._selected_notes = [self._hover_note] if self._hover_note else []
            if set(self._selected_notes) != last_selected:
                self.note_selection_changed.emit(self._selected_notes)
            self._selection_frame_start = None
        elif event.button() == Config.DRAG_MOUSE_BUTTON and self._dragging:
            self._dragging = False
            self.setCursor(Config.NORMAL_MOUSE_POINTER)
        self._pressed_note = None
        self.update()
        self._update_keys_status()

    def leaveEvent(self, event: QEvent) -> None:
        self._mouse_position = None
        if self._hover_track:
            self._hover_track = None
            self.hover_track_changed.emit(self._hover_track)
        if self._hover_note:
            self._hover_note = None
            self.hover_note_changed.emit(self._hover_note)
        self.update()
        return super().leaveEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        self._keyboard_modifiers.clear()
        for e in event.modifiers():
            self._keyboard_modifiers.add(e)
        self._update_keys_status()
        return super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        self._keyboard_modifiers.clear()
        for e in event.modifiers():
            self._keyboard_modifiers.add(e)
        self._update_keys_status()
        return super().keyReleaseEvent(event)

    def paintEvent(self, event):
        self._shift = QPointF(min(self._shift.x(), self._min_shift_x), min(self._shift.y(), 0))

        last_hover_track = self._hover_track
        last_hover_note = self._hover_note
        self._hover_track = None
        self._hover_note = None
        if self._selection_frame_start and self._mouse_position:
            x1 = self._selection_frame_start.x()
            y1 = self._selection_frame_start.y()
            x2 = self._mouse_position.x()
            y2 = self._mouse_position.y()
            self._selection_frame = QRectF(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        else:
            self._selection_frame = None

        self.selection_frame_notes = []

        p = QPainter(self)
        p.fillRect(self.rect(), Config.BACKGROUND_COLOR)
        p.save()
        y = self._pitch_height * 2 * self._zoom_y
        for i, track in enumerate(self._song.tracks):
            track_height = self._draw_track(p, i, y)
            track_end_y = y + track_height
            y = track_end_y + self._pitch_height * 4 * self._zoom_y
        p.restore()

        if last_hover_track != self._hover_track:
            self.hover_track_changed.emit(self._hover_track)
        if last_hover_note != self._hover_note:
            self.hover_note_changed.emit(self._hover_note)

        if self._selection_frame:
            selection_frame_distance = QLineF(self._selection_frame.topLeft(), self._selection_frame.bottomRight()).length()
            if selection_frame_distance > 2:
                p.setPen(QPen(Config.SELECTION_FRAME_BORDER_COLOR, 1, Qt.PenStyle.DashLine))
                p.fillRect(self._selection_frame, Config.SELECTION_FRAME_COLOR)
                p.drawRect(self._selection_frame)


    def time_to_x(self, tick: int) -> float:
        return float(tick) / 1000000. * self._second_width * self._zoom_x

    def _draw_track(self, p: QPainter, track_index: int, y_offset: float) -> float:
        track = self._song.tracks[track_index]
        height = (track.max_pitch - track.min_pitch) * self._pitch_height * self._zoom_y + self._pitch_height * self._zoom_y
        track_rect = QRectF(0, y_offset, self.time_to_x(track.duration), height)
        hovered = self._mouse_position is not None and track_rect.contains(self._mouse_position - self._shift)

        p.save()
        p.translate(self._shift)
        hover_pitch: int | None = None
        if hovered or self._highlighted_track == track:
            if hovered:
                self._hover_track = track
            p.fillRect(track_rect, Config.HOVER_TRACK_HIGHLIGHT_COLOR)
            p.setPen(QPen(Config.HOVER_TRACK_BORDER_COLOR, Config.HOVER_TRACK_BORDER_WIDTH))
            p.drawRect(track_rect)
            hover_pitch = int((y_offset + height - (self.mapFromGlobal(self.cursor().pos()).y() - self._shift.y())) // (self._pitch_height * self._zoom_y)) + track.min_pitch

        if self._pitch_height * self._zoom_y >= 3:
            for pitch in range(track.min_pitch - 1, track.max_pitch + 1):
                if (pitch + 1) % 12 == 0:
                    p.setPen(QPen(Config.GRID_COLOR_MAIN, 2))
                elif (pitch - track.min_pitch) % 2 == 1:
                    p.setPen(QPen(Config.GRID_COLOR_LIGHT, 1))
                else:
                    p.setPen(QPen(Config.GRID_COLOR_DARK, 1))
                y = y_offset + (track.pitch_range - pitch + track.min_pitch) * (self._pitch_height * self._zoom_y)
                p.drawLine(QPointF(0, y), QPointF(self.time_to_x(track.duration), y))
        else:
            for pitch in range((((track.min_pitch - 1) // 12) + 1) * 12 - 1, track.max_pitch + 1, 12):
                p.setPen(QPen(Config.GRID_COLOR_DARK, 1))
                y = y_offset + (track.pitch_range - pitch + track.min_pitch) * (self._pitch_height * self._zoom_y)
                p.drawLine(QPointF(0, y), QPointF(self.time_to_x(track.duration), y))

        for note in track.notes:
            x = self.time_to_x(note.start_tick)
            y = y_offset + (track.pitch_range - note.pitch + track.min_pitch) * (self._pitch_height * self._zoom_y)
            w = self.time_to_x(note.duration)
            h = self._pitch_height * self._zoom_y
            if w > 0 and h > 0:
                note_rect = QRectF(x, y, w, h)
                shifted_selection_frame = self._selection_frame.translated(-self._shift) if self._selection_frame else None
                note_hovered = hovered and self._mouse_position and note_rect.contains(self._mouse_position - self._shift)
                if note.buzzer in (Buzzer.BUZZER_1, Buzzer.BUZZER_2, Buzzer.BUZZER_3):
                    buzzer_index = note.buzzer.value - 1
                    fill_color = Config.NOTE_BUZZER_FILL_COLORS[buzzer_index]
                elif note in self._error_notes:
                    fill_color = Config.NOTE_ERROR_FILL_COLOR
                else:
                    fill_color = Config.NOTE_FILL_COLOR

                if shifted_selection_frame and shifted_selection_frame.intersects(note_rect):
                    frame_color = Config.SELECTION_FRAME_NOTE_BORDER_COLOR
                    frame_width = 2
                    self.selection_frame_notes.append(note)
                elif note_hovered or self._highlighted_note == note:
                    if note in self._selected_notes:
                        frame_color = Config.NOTE_HOVER_SELECTED_BORDER_COLOR
                        frame_width = 2
                    else:
                        frame_color = Config.NOTE_HOVER_BORDER_COLOR
                        frame_width = 1
                    if note_hovered:
                        self._hover_note = note
                elif note in self._selected_notes:
                    frame_color = Config.NOTE_SELECTED_BORDER_COLOR
                    frame_width = 2
                else:
                    frame_color = Config.NOTE_BORDER_COLOR
                    frame_width = 1
                if Config.INDICATE_VELOCITY and track.velocity_range > 0:
                    fill_color.setAlpha((note.velocity - track.min_velocity) * 255 // track.velocity_range)
                p.fillRect(note_rect, fill_color)
                p.setPen(QPen(frame_color, frame_width))
                p.drawRect(note_rect)
        p.restore()

        if self._zoom_y > 0.2:
            p.save()
            p.translate(QPointF(0, self._shift.y()))
            p.setPen(QPen(QColor.fromRgba(0xAAFFFFFF), 1))

            p.save()
            p.rotate(-90)
            p.setFont(create_font("Sans", self._pitch_height * self._zoom_y * 2))
            fm = p.fontMetrics()
            if hovered:
                p.setPen(QPen(Config.TRACK_TEXT_COLOR_HOVER))
            else:
                p.setPen(QPen(Config.TRACK_TEXT_COLOR))
            p.drawText(QPointF(-y_offset - (height + fm.horizontalAdvance(f'{track.name}')) / 2, fm.ascent() * 0.8), f'{track.name}')
            title_height = fm.height() * 0.6
            p.restore()

            p.setFont(create_font("Mono", self._pitch_height * self._zoom_y * 0.8))
            max_pitch_width = p.fontMetrics().horizontalAdvance('000')
            for pitch in range(track.min_pitch, track.max_pitch + 1):
                y = y_offset + (track.pitch_range - pitch + track.min_pitch) * (self._pitch_height * self._zoom_y)
                pitch_text = f'{pitch}'
                pitch_width = p.fontMetrics().horizontalAdvance(pitch_text)
                note_text = SongWidget.pitch_to_note_name(pitch)
                pitch_text = f'{pitch_text} {note_text}'
                if hover_pitch == pitch:
                    p.setPen(QPen(Config.TRACK_TEXT_COLOR_HOVER))
                else:
                    p.setPen(QPen(Config.TRACK_TEXT_COLOR))
                p.drawText(QPointF(title_height + max_pitch_width - pitch_width, y + self._pitch_height * self._zoom_y * 0.9), pitch_text)
                self._min_shift_x = title_height + p.fontMetrics().horizontalAdvance('000 C#4')
            p.restore()

        return height

    def wheelEvent(self, event):
        # Zoom in/out with mouse wheel, centered on mouse position
        delta = event.angleDelta().y()
        factor = 1.15 if delta > 0 else 1/1.15
        old_zoom_x = self._zoom_x
        old_zoom_y = self._zoom_y

        # Optionally: hold Ctrl for x-zoom, Shift for y-zoom, else both
        modifiers = event.modifiers()
        pos = event.position()
        if modifiers & Config.ZOOM_X_MODIFIER:
            self._zoom_x *= factor
        elif modifiers & Config.ZOOM_Y_MODIFIER:
            self._zoom_y *= factor
        else:
            self._zoom_x *= factor
            self._zoom_y *= factor

        # Clamp zoom
        self._zoom_x = max(Config.MIN_ZOOM_X, min(self._zoom_x, Config.MAX_ZOOM_X))
        self._zoom_y = max(Config.MIN_ZOOM_Y, min(self._zoom_y, Config.MAX_ZOOM_Y))

        # Optional: keep mouse position stable (zoom to cursor)
        # Calculate logical position before and after zoom, adjust shift accordingly
        rel = pos - self._shift
        if modifiers & Config.ZOOM_X_MODIFIER or modifiers & Config.ZOOM_Y_MODIFIER or True:
            # Always zoom to cursor for user-friendliness
            scale_x = self._zoom_x / old_zoom_x
            scale_y = self._zoom_y / old_zoom_y
            self._shift = pos - QPointF(rel.x() * scale_x, rel.y() * scale_y)

        self.update()

    def _update_keys_status(self):
        if self._selection_frame_start:
            if Config.SELECT_NOTE_ADD_MODIFIER in self._keyboard_modifiers or Config.SELECT_NOTE_SPAN_MODIFIER in self._keyboard_modifiers:
                status = KeysStatus.ADD
            elif Config.SELECT_NOTE_REMOVE_MODIFIER in self._keyboard_modifiers:
                status = KeysStatus.REMOVE
            else:
                status = KeysStatus.NONE
        elif self._dragging:
            if Config.ZOOM_X_MODIFIER in self._keyboard_modifiers:
                status = KeysStatus.SCALE_X
            elif Config.ZOOM_Y_MODIFIER in self._keyboard_modifiers:
                status = KeysStatus.SCALE_Y
            else:
                status = KeysStatus.NONE
        else:
            if Config.SELECT_NOTE_ADD_MODIFIER in self._keyboard_modifiers:
                status = KeysStatus.ADD
            elif Config.SELECT_NOTE_REMOVE_MODIFIER in self._keyboard_modifiers:
                status = KeysStatus.REMOVE
            elif Config.SELECT_NOTE_SPAN_MODIFIER in self._keyboard_modifiers:
                status = KeysStatus.SPAN
            else:
                status = KeysStatus.NONE
        if status != self._keys_status:
            self._keys_status = status
            self.key_status_update.emit(status)

    def move_track_up(self, track: Track):
        index = self._song.tracks.index(track)
        if index > 0:
            self._song.tracks[index], self._song.tracks[index - 1] = self._song.tracks[index - 1], self._song.tracks[index]
            self.update()

    def move_track_down(self, track: Track):
        index = self._song.tracks.index(track)
        if index < len(self._song.tracks) - 1:
            self._song.tracks[index], self._song.tracks[index + 1] = self._song.tracks[index + 1], self._song.tracks[index]
            self.update()

    def select_track(self, track: Track):
        if self._selected_notes != track.notes:
            self._selected_notes = track.notes
            self.note_selection_changed.emit(self._selected_notes)
            self.update()

    def set_highlighted_track(self, track: Track | None):
        if self._highlighted_track != track:
            self._highlighted_track = track
            self.update()

    def set_highlighted_note(self, note: Note | None):
        if self._highlighted_note != note:
            self._highlighted_note = note
            self.update()

    @staticmethod
    def pitch_to_note_name(pitch: int) -> str:
        names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (pitch // 12) - 1
        name = names[pitch % 12]
        return f'{name}{octave}'
