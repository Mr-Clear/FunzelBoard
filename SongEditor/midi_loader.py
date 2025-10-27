from mido import MidiFile

from song import Buzzer, Note, Track, Song
import os

class MidiLoader:
    @staticmethod
    def load_midi_file(fname: str) -> Song:
        tracks = []
        file = MidiFile(fname, clip=True)
        file_name = file.filename if file.filename else "Unnamed"
        file_name = os.path.basename(file_name)
        tempo_map = MidiLoader.get_tempo_map(file)
        ticks_per_beat = file.ticks_per_beat
        song = Song(name=file_name, tracks=[])

        for midi_track in file.tracks:
            abs_ticks = 0
            tempo_index = 0
            on_notes = {}
            notes = []
            track = Track(name=midi_track.name, notes=[], song=song)

            for msg in midi_track:
                abs_ticks += msg.time

                while (tempo_index + 1 < len(tempo_map) and
                       abs_ticks >= tempo_map[tempo_index + 1][0]):
                    tempo_index += 1

                abs_time_us = MidiLoader.ticks_to_microseconds(
                    abs_ticks, tempo_map, ticks_per_beat)

                if msg.type == 'note_on' or msg.type == 'note_off':
                    off = msg.velocity == 0 or msg.type == 'note_off'
                    if not off:
                        on_notes[msg.note] = (abs_time_us, msg.velocity)
                    else:
                        if msg.note in on_notes:
                            start_us, velocity = on_notes.pop(msg.note)
                            duration = abs_time_us - start_us
                            note = Note(start_us=start_us, duration_us=duration,
                                      pitch=msg.note, velocity=velocity,
                                      buzzer=Buzzer.NONE, track=track)
                            notes.append(note)

            if notes:
                track.notes = notes
                tracks.append(track)

        song.tracks = tracks
        return song

    @staticmethod
    def get_tempo_map(file: MidiFile) -> list[tuple[int, int]]:
        tempo_map = []
        abs_ticks = 0
        tempo = 500000
        track = file.tracks[0]
        tempo_map.append((abs_ticks, tempo))
        for msg in track:
            abs_ticks += msg.time
            if msg.type == 'set_tempo':
                tempo = msg.tempo
                tempo_map.append((abs_ticks, tempo))
        return tempo_map

    @staticmethod
    def ticks_to_microseconds(ticks: int, tempo_map: list[tuple[int, int]],
                             ticks_per_beat: int) -> int:
        us = 0
        last_tick = 0
        tempo = tempo_map[0][1]

        for tempo_tick, new_tempo in tempo_map:
            if tempo_tick >= ticks:
                remaining_ticks = ticks - last_tick
                us += remaining_ticks * tempo // ticks_per_beat
                break
            else:
                tick_delta = tempo_tick - last_tick
                us += tick_delta * tempo // ticks_per_beat
                last_tick = tempo_tick
                tempo = new_tempo
        else:
            remaining_ticks = ticks - last_tick
            us += remaining_ticks * tempo // ticks_per_beat

        return us
