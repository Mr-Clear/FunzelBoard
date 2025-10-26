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
            abs_time = 0
            last_time = 0
            tempo_index = 0
            tempo = tempo_map[tempo_index][1]
            on_notes = {}
            notes = []
            track = Track(name=midi_track.name, notes=[], song=song)
            for msg in midi_track:
                time = msg.time * tempo // ticks_per_beat  # convert to µs
                abs_time += time
                if msg.type == 'note_on' or msg.type == 'note_off':
                    off = msg.velocity == 0 or msg.type == 'note_off'
                    t = abs_time - last_time
                    if not off:
                        on_notes[msg.note] = (abs_time, msg.velocity)
                    else:
                        if msg.note in on_notes:
                            start_tick, velocity = on_notes.pop(msg.note)
                            duration = abs_time - start_tick
                            note = Note(start_tick=start_tick, duration=duration, pitch=msg.note, velocity=velocity, buzzer=Buzzer.NONE, track=track)
                            notes.append(note)

                last_time = abs_time
                while (tempo_index + 1 < len(tempo_map) and abs_time >= tempo_map[tempo_index + 1][0]):
                    tempo_index += 1
                tempo = tempo_map[tempo_index][1]
            if notes:
                track.notes = notes
                tracks.append(track)
        song.tracks = tracks
        return song

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
