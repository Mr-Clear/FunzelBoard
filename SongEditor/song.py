from dataclasses import dataclass
import enum

class Buzzer(enum.Enum):
    NONE = 0
    BUZZER_1 = 1
    BUZZER_2 = 2
    BUZZER_3 = 3
    ANY = 4

@dataclass
class Note:
    start_tick: int
    duration: int
    pitch: int
    velocity: int
    buzzer: Buzzer = Buzzer.NONE
    @property
    def frequency(self) -> float:
        return 440.0 * (2 ** ((self.pitch - 69) / 12.0))

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self is other


@dataclass
class Track:
    index: int
    name: str
    notes: list[Note]
    duration: int
    ticks_per_beat: float
    min_pitch: int
    max_pitch: int
    min_velocity: int
    max_velocity: int

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
        usage = {buzzer: 0 for buzzer in Buzzer}
        for note in self.notes:
            usage[note.buzzer] += 1
        return usage

    @property
    def error_notes_count(self) -> int:
        return 0

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self is other

@dataclass
class Song:
    name: str
    tracks: list[Track]

    @property
    def duration(self) -> int:
        if not self.tracks:
            return 0
        return max(track.duration for track in self.tracks)

    @property
    def pitch_range(self) -> tuple[int, int]:
        if not self.tracks:
            return (0, 0)
        min_pitch = min(track.min_pitch for track in self.tracks)
        max_pitch = max(track.max_pitch for track in self.tracks)
        return (min_pitch, max_pitch)

    @property
    def velocity_range(self) -> tuple[int, int]:
        if not self.tracks:
            return (0, 0)
        min_velocity = min(track.min_velocity for track in self.tracks)
        max_velocity = max(track.max_velocity for track in self.tracks)
        return (min_velocity, max_velocity)

    @property
    def notes_count(self) -> int:
        return sum(len(track.notes) for track in self.tracks)

    @property
    def buzzer_usage(self) -> dict[Buzzer, int]:
        usage = {buzzer: 0 for buzzer in Buzzer}
        for track in self.tracks:
            track_usage = track.buzzers_usage
            for buzzer, count in track_usage.items():
                usage[buzzer] += count
        return usage

    @property
    def error_notes_count(self) -> int:
        return sum(track.error_notes_count for track in self.tracks)
