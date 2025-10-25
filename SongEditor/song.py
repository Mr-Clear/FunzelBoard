from dataclasses import dataclass
import enum

class Buzzer(enum.Enum):
    NONE = 0
    BUZZER_1 = 1
    BUZZER_2 = 2
    BUZZER_3 = 4
    ANY = 7

@dataclass
class Note:
    start_tick: int
    duration: int
    pitch: int
    velocity: int
    buzzer: Buzzer = Buzzer.ANY
    @property
    def frequency(self) -> float:
        return 440.0 * (2 ** ((self.pitch - 69) / 12.0))


@dataclass
class Track:
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

@dataclass
class Song:
    name: str
    tracks: list[Track]
    @property
    def duration(self) -> int:
        if not self.tracks:
            return 0
        return max(track.duration for track in self.tracks)
