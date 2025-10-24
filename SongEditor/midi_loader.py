from dataclasses import dataclass
from mido import MidiFile

@dataclass
class Note:
    start_tick: int
    duration: int
    pitch: int
    velocity: int


@dataclass
class Track:
    file_name: str
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

class MidiLoader:
    @staticmethod
    def load_midi_file(fname: str) -> list[Track]:
        f = True
        tracks = []
        file = MidiFile(fname, clip=True)
        file_name = file.filename if file.filename else "Unnamed"
        tempo_map = MidiLoader.get_tempo_map(file)
        ticks_per_beat = file.ticks_per_beat
        for midi_track in file.tracks:
            abs_time = 0
            last_time = 0
            tempo_index = 0
            tempo = tempo_map[tempo_index][1]
            on_notes = {}
            notes = []
            min_pitch = 127
            max_pitch = 0
            min_velocity = 127
            max_velocity = 0
            for msg in midi_track:
                time = msg.time * tempo // ticks_per_beat  # convert to µs
                abs_time += time
                if msg.type == 'note_on' or msg.type == 'note_off':
                    off = msg.velocity == 0 or msg.type == 'note_off'
                    t = abs_time - last_time
                    if not off:
                        if f:
                            print(msg)
                            f = False
                        on_notes[msg.note] = (abs_time, msg.velocity)
                        if msg.note < min_pitch:
                            min_pitch = msg.note
                        if msg.note > max_pitch:
                            max_pitch = msg.note
                        if msg.velocity < min_velocity:
                            min_velocity = msg.velocity
                        if msg.velocity > max_velocity:
                            max_velocity = msg.velocity
                    else:
                        if msg.note in on_notes:
                            start_tick, velocity = on_notes.pop(msg.note)
                            duration = abs_time - start_tick
                            note = Note(start_tick=start_tick, duration=duration, pitch=msg.note, velocity=velocity)
                            notes.append(note)

                last_time = abs_time
                while (tempo_index + 1 < len(tempo_map) and abs_time >= tempo_map[tempo_index + 1][0]):
                    tempo_index += 1
                tempo = tempo_map[tempo_index][1]
            if notes:
                tracks.append(Track(file_name=file_name, name=midi_track.name, notes=notes,
                                    duration=abs_time, ticks_per_beat=ticks_per_beat,
                                    min_pitch=min_pitch, max_pitch=max_pitch,
                                    min_velocity=min_velocity, max_velocity=max_velocity))
                print(f'Loaded track {midi_track.name} with {len(notes)} notes, pitch range: {min_pitch}-{max_pitch}')
        return tracks

    @staticmethod
    def get_tempo_map(file: MidiFile) -> list[tuple[int, int]]:
        tempo_map = []
        abs_time = 0
        tempo = 500000  # default tempo in µs per beat
        track = file.tracks[0]  # usually tempo changes are in the first track
        tempo_map.append((abs_time, tempo))
        for msg in track:
            time = msg.time * tempo // file.ticks_per_beat  # convert to µs
            abs_time += time
            if msg.type == 'set_tempo':
                tempo = msg.tempo
                tempo_map.append((abs_time, tempo))
        return tempo_map