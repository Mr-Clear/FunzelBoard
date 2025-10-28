from __future__ import annotations
from dataclasses import asdict, dataclass, field
import enum
import json
from typing import Callable

class Buzzer(enum.Enum):
    NONE = 0
    BUZZER_1 = 1
    BUZZER_2 = 2
    BUZZER_3 = 3

@dataclass
class Note:
    start_us: int
    duration_us: int
    pitch: int
    velocity: int
    buzzer: Buzzer

    track: Track = field(repr=False)

    _change_listeners: set[Callable[[], None]] = field(default_factory=set, init=False, repr=False)

    def add_change_listener(self, listener: Callable[[], None]):
        self._change_listeners.add(listener)

    def remove_change_listener(self, listener: Callable[[], None]):
        self._change_listeners.discard(listener)

    def _notify_change_listeners(self):
        if hasattr(self, '_change_listeners'):
            for listener in self._change_listeners:
                listener()

    @property
    def frequency(self) -> float:
        return 440.0 * (2 ** ((self.pitch - 69) / 12.0))

    @property
    def end_us(self) -> int:
        return self.start_us + self.duration_us

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self is other

    def __setattr__(self, name: str, value) -> None:
        super().__setattr__(name, value)
        if name in {'start_us', 'duration_us', 'pitch', 'velocity', 'buzzer'}:
            if hasattr(self, 'track'):
                self.track.invalidate_cache()
            self._notify_change_listeners()

    def to_dict(self) -> dict:
        return {
            'start_us': self.start_us,
            'duration_us': self.duration_us,
            'pitch': self.pitch,
            'velocity': self.velocity,
            'buzzer': self.buzzer.name
        }


@dataclass
class Track:
    name: str
    notes: list[Note]
    song: Song | None = field(repr=False)

    _duration_us: int | None = field(default=None, init=False, repr=False)
    _min_pitch: int | None = field(default=None, init=False, repr=False)
    _max_pitch: int | None = field(default=None, init=False, repr=False)
    _min_velocity: int | None = field(default=None, init=False, repr=False)
    _max_velocity: int | None = field(default=None, init=False, repr=False)
    _buzzers_usage: dict[Buzzer, int] | None = field(init=False, repr=False)
    _error_notes: set[Note] | None = field(default=None, init=False, repr=False)

    _change_listeners: set[Callable[[], None]] = field(default_factory=set, init=False, repr=False)

    def invalidate_cache(self):
        self._duration_us = None
        self._min_pitch = None
        self._max_pitch = None
        self._min_velocity = None
        self._max_velocity = None
        self._buzzers_usage = None
        self._error_notes = None
        if self.song:
            self.song.invalidate_cache()
        self._notify_change_listeners()

    def add_change_listener(self, listener: Callable[[], None]):
        self._change_listeners.add(listener)

    def remove_change_listener(self, listener: Callable[[], None]):
        self._change_listeners.discard(listener)

    def _notify_change_listeners(self):
        if hasattr(self, '_change_listeners'):
            for listener in self._change_listeners:
                listener()

    @property
    def duration_us(self) -> int:
        if self._duration_us is None:
            if not self.notes:
                self._duration_us = 0
            else:
                self._duration_us = max(note.start_us + note.duration_us for note in self.notes)
        return self._duration_us

    @property
    def min_pitch(self) -> int:
        if self._min_pitch is None:
            if not self.notes:
                self._min_pitch = 0
            else:
                self._min_pitch = min(note.pitch for note in self.notes)
        return self._min_pitch

    @property
    def max_pitch(self) -> int:
        if self._max_pitch is None:
            if not self.notes:
                self._max_pitch = 0
            else:
                self._max_pitch = max(note.pitch for note in self.notes)
        return self._max_pitch

    @property
    def min_velocity(self) -> int:
        if self._min_velocity is None:
            if not self.notes:
                self._min_velocity = 0
            else:
                self._min_velocity = min(note.velocity for note in self.notes)
        return self._min_velocity

    @property
    def max_velocity(self) -> int:
        if self._max_velocity is None:
            if not self.notes:
                self._max_velocity = 0
            else:
                self._max_velocity = max(note.velocity for note in self.notes)
        return self._max_velocity

    @property
    def pitch_range(self) -> int:
        return self.max_pitch - self.min_pitch

    @property
    def velocity_range(self) -> int:
        return self.max_velocity - self.min_velocity

    @property
    def notes_count(self) -> int:
        return len(self.notes)

    @property
    def buzzers_usage(self) -> dict[Buzzer, int]:
        if not hasattr(self, '_buzzers_usage'):
            return { buzzer: 0 for buzzer in Buzzer }
        if self._buzzers_usage is None:
            usage = {buzzer: 0 for buzzer in Buzzer}
            for note in self.notes:
                usage[note.buzzer] += 1
            self._buzzers_usage = usage
        return self._buzzers_usage

    @property
    def error_notes(self) -> set[Note]:
        if self._error_notes:
            return self._error_notes
        if self.song:
            self._error_notes = {note for note in self.song.error_notes if note.track is self}
        else:
            self._error_notes = set()
        return self._error_notes

    @property
    def error_notes_count(self) -> int:
        return len(self.error_notes)

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self is other

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'notes': [note.to_dict() for note in self.notes]
        }

@dataclass
class Song:
    name: str
    tracks: list[Track]

    _duration_us: int | None = field(default=None, init=False, repr=False)
    _pitch_range: tuple[int, int] | None = field(default=None, init=False, repr=False)
    _velocity_range: tuple[int, int] | None = field(default=None, init=False, repr=False)
    _notes_count: int | None = field(default=None, init=False, repr=False)
    _buzzer_usage: dict[Buzzer, int] | None = field(default=None, init=False, repr=False)
    _error_notes: set[Note] | None = field(default=None, init=False, repr=False)

    _change_listeners: set[Callable[[], None]] = field(default_factory=set, init=False, repr=False)

    def invalidate_cache(self):
        self._duration_us = None
        self._pitch_range = None
        self._velocity_range = None
        self._notes_count = None
        self._buzzer_usage = None
        self._error_notes = None
        self._notify_change_listeners()

    def add_change_listener(self, listener: Callable[[], None]):
        self._change_listeners.add(listener)

    def remove_change_listener(self, listener: Callable[[], None]):
        self._change_listeners.discard(listener)

    def _notify_change_listeners(self):
        if hasattr(self, '_change_listeners'):
            for listener in self._change_listeners:
                listener()

    @property
    def duration_us(self) -> int:
        if self._duration_us is None:
            if not self.tracks:
                self._duration_us = 0
            else:
                self._duration_us = max(track.duration_us for track in self.tracks)
        return self._duration_us

    @property
    def pitch_range(self) -> tuple[int, int]:
        if self._pitch_range is None:
            if not self.tracks:
                self._pitch_range = (0, 0)
            else:
                min_pitch = min(track.min_pitch for track in self.tracks)
                max_pitch = max(track.max_pitch for track in self.tracks)
                self._pitch_range = (min_pitch, max_pitch)
        return self._pitch_range

    @property
    def velocity_range(self) -> tuple[int, int]:
        if self._velocity_range is None:
            if not self.tracks:
                self._velocity_range = (0, 0)
            else:
                min_velocity = min(track.min_velocity for track in self.tracks)
                max_velocity = max(track.max_velocity for track in self.tracks)
                self._velocity_range = (min_velocity, max_velocity)
        return self._velocity_range

    @property
    def notes_count(self) -> int:
        if self._notes_count is None:
            self._notes_count = sum(len(track.notes) for track in self.tracks)
        return self._notes_count

    @property
    def buzzer_usage(self) -> dict[Buzzer, int]:
        if self._buzzer_usage is None:
            self._buzzer_usage = {buzzer: 0 for buzzer in Buzzer}
            for track in self.tracks:
                track_usage = track.buzzers_usage
                for buzzer, count in track_usage.items():
                    self._buzzer_usage[buzzer] += count
        return self._buzzer_usage

    @property
    def error_notes(self) -> set[Note]:
        if self._error_notes is None:
            self._error_notes = self._calculate_error_notes()
        return self._error_notes

    @property
    def all_notes(self) -> list[Note]:
        notes = []
        for track in self.tracks:
            notes.extend(track.notes)
        return sorted(notes, key=lambda n: (n.start_us, n.duration_us, n.pitch))

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'tracks': [track.to_dict() for track in self.tracks]
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), cls=SongEncoder, indent=2)

    @staticmethod
    def from_json(data: str) -> 'Song':
        try:
            obj = json.loads(data)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return Song(name="Invalid Song", tracks=[])

        song = Song(name=obj['name'], tracks=[])

        tracks = []
        for track_data in obj['tracks']:
            track = Track(
                name=track_data['name'],
                notes=[],
                song=song)
            notes = []
            for note_data in track_data['notes']:
                note = Note(
                    start_us=note_data['start_us'],
                    duration_us=note_data['duration_us'],
                    pitch=note_data['pitch'],
                    velocity=note_data['velocity'],
                    buzzer=Buzzer[note_data['buzzer']],
                    track=track
                )
                notes.append(note)
            track.notes = notes
            track.invalidate_cache()
            tracks.append(track)
        song.tracks = tracks
        song.invalidate_cache()

        return song

    def _calculate_error_notes(self) -> set[Note]:
        error_notes = set()
        for buzzer in {Buzzer.BUZZER_1, Buzzer.BUZZER_2, Buzzer.BUZZER_3}:
            buzzer_notes = []
            for track in self.tracks:
                for note in track.notes:
                    if note.buzzer == buzzer:
                        buzzer_notes.append(note)
            buzzer_notes.sort(key=lambda n: n.start_us)
            active_notes: set[Note] = set()
            for note in buzzer_notes:
                active_notes_copy = active_notes.copy()
                for active_note in active_notes_copy:
                    if note.start_us < active_note.end_us:
                        error_notes.add(note)
                        error_notes.add(active_note)
                    else:
                        active_notes.remove(active_note)
                active_notes.add(note)
        return error_notes

    def fix_overlaps(self):
        for buzzer in {Buzzer.BUZZER_1, Buzzer.BUZZER_2, Buzzer.BUZZER_3}:
            buzzer_notes = []
            for track in self.tracks:
                for note in track.notes:
                    if note.buzzer == buzzer:
                        buzzer_notes.append(note)
            buzzer_notes.sort(key=lambda n: n.start_us)
            active_notes: list[Note] = []
            for note in buzzer_notes:
                active_notes_copy = active_notes.copy()
                for active_note in active_notes_copy:
                    if note.start_us < active_note.end_us:
                        active_note.duration_us = note.start_us - active_note.start_us
                active_notes.append(note)
        self.invalidate_cache()

    def auto_assign_buzzers(self):
        buzzer_end_times = {
            Buzzer.BUZZER_1: 0,
            Buzzer.BUZZER_2: 0,
            Buzzer.BUZZER_3: 0
        }

        sorted_notes = sorted(self.all_notes, key=lambda n: n.start_us)

        for note in sorted_notes:
            earliest_buzzer = min(buzzer_end_times, key=lambda b: buzzer_end_times[b])
            note.buzzer = earliest_buzzer
            buzzer_end_times[earliest_buzzer] = note.end_us

    def to_buzzer_tracks(self) -> dict[Buzzer, list[Note]]:
        buzzer_tracks: dict[Buzzer, list[Note]] = {
            Buzzer.BUZZER_1: [],
            Buzzer.BUZZER_2: [],
            Buzzer.BUZZER_3: []
        }
        for note in self.all_notes:
            if note.buzzer in buzzer_tracks:
                buzzer_tracks[note.buzzer].append(note)
        for buzzer in buzzer_tracks:
            buzzer_tracks[buzzer].sort(key=lambda n: n.start_us)
        return buzzer_tracks

class SongEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, enum.Enum):
            return o.name
        return super().default(o)

