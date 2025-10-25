from song import Note, Track, Song

import simpleaudio as sa
from sortedcontainers import SortedList
import multiprocessing

from dataclasses import dataclass
import time
import numpy as np

class Player:
    @dataclass
    class _Event:
        tick: int

    @dataclass
    class _NoteOnEvent(_Event):
        note: Note

    @dataclass
    class _NoteOffEvent(_Event):
        note: Note

    def __init__(self, song: Song):
        self.song = []
        self.is_playing = False
        self.current_tick = 0
        for track in song.tracks:
            for note in track.notes:
                self.song.append(self._NoteOnEvent(tick=note.start_tick, note=note))
        self.duration = song.duration
        self.queue = multiprocessing.Queue()

    def start(self):
        self._start_player_process()
        self.is_playing = True

    def stop(self):
        self.queue.put('stop')
        self.is_playing = False

    def _start_player_process(self):
        proc = multiprocessing.Process(target=self._player_process, args=(self.song, self.duration, self.queue))
        proc.start()
        return proc

    def _player_process(self, song_data, duration, queue):
        song = SortedList(song_data, key=lambda e: e.tick)
        is_playing = True
        start = time.time_ns() // 1000  # microseconds
        current_tick = 0
        while is_playing and current_tick < duration:
            current_tick = time.time_ns() // 1000 - start
            while not queue.empty():
                cmd = queue.get()
                if cmd == 'stop':
                    is_playing = False
            while song and song[0].tick <= current_tick:
                evt = song.pop(0)
                if isinstance(evt, self._NoteOnEvent):
                    self.play_note(evt.note)
                elif isinstance(evt, self._NoteOffEvent):
                    # Stop note
                    pass

    def play_note(self, note: Note):
        duration_us = note.duration
        frequency = note.frequency
        volume = note.velocity / 127
        sample_rate = 44100

        t = np.linspace(0, duration_us / 1000000, int(sample_rate * duration_us / 1000000), endpoint=False)
        wave = np.sign(np.sin(2 * np.pi * frequency * t)) * volume
        audio = np.int16(wave * 32767)
        sa.play_buffer(audio.tobytes(), 1, 2, sample_rate)
