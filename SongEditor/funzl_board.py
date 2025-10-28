from typing import Callable, Iterable
import serial
import time
from serial.tools import list_ports
from song import Song, Note, Buzzer
import re

class FunzlBoard:
    @staticmethod
    def send(command: bytes, progress_callback: Callable[[str], None] | None = None) -> str:
        ports = list_ports.comports()
        candidates = [p.device for p in ports if p.device and ('ttyACM' in p.device or 'ttyUSB' in p.device)]
        if not candidates:
            return 'No serial USB device found.'

        with serial.Serial(str(candidates[0]), 115200, timeout=1) as ser:
            t = 0
            length = len(command)
            sent = 0
            for char in command:
                if progress_callback and t < time.time() - 0.1:
                    progress_callback(f'Sending {length} bytes: {sent / length * 100:.2f} %')
                    t = time.time()
                ser.write(bytes([char]))
                sent += 1
            return f'Sent to {candidates[0]}.'

    @staticmethod
    def send_song(song: Song, progress_callback: Callable[[str], None] | None = None) -> str:
        result = b'\nS'
        notes = song.to_buzzer_tracks()
        for buzzer in [Buzzer.BUZZER_1, Buzzer.BUZZER_2, Buzzer.BUZZER_3]:
            buzzer_notes = notes[buzzer]
            result += len(buzzer_notes).to_bytes(4, 'little')
            for note in buzzer_notes:
                result += note.start_us.to_bytes(4, 'little')
                result += (note.start_us + note.duration_us).to_bytes(4, 'little')
                result += note.pitch.to_bytes(1, 'little')
        result += 0x00.to_bytes(1, 'little')
        return FunzlBoard.send(result, progress_callback=progress_callback)

    @staticmethod
    def send_stop() -> str:
        result = FunzlBoard.send(b'\n')
        return result

    @staticmethod
    def export(song: Song) -> str:
        namespace = ''.join(p.capitalize() for p in [p for p in re.split(r'[^0-9A-Za-z]+', song.name) if p]) or 'Song'
        variable = namespace[0].lower() + namespace[1:]
        if namespace and namespace[0].isdigit():
            namespace = '_' + namespace

        buzzer_tracks: list[list[Note]] = []
        for buzzer in [Buzzer.BUZZER_1, Buzzer.BUZZER_2, Buzzer.BUZZER_3]:
            notes = [note for note in song.all_notes if note.buzzer == buzzer]
            if not notes:
                continue
            sorted_notes = sorted(notes, key=lambda n: n.start_us)
            buzzer_tracks.append(sorted_notes)

        s  = '#pragma once\n\n'
        s += '#include "music/song.h"\n\n'
        s += 'namespace Songs {\n'
        s += f'  namespace {namespace} {{\n'
        for i, notes in enumerate(buzzer_tracks):
            if notes:
                s += f'    inline constexpr Note track{i+1}[] = {{\n'
                for note in notes:
                    s += f'      {{{note.start_us}, {note.start_us + note.duration_us}, {note.pitch}}},\n'
                s += '    };\n\n'
        s += '  }\n\n'

        s += f'  inline constexpr Song {variable} = {{{{{{\n'
        for i, notes in enumerate(buzzer_tracks):
            if notes:
                s += f'      {{{namespace}::track{i+1}, {len(notes)}}},\n'
            else:
                s += '      {nullptr, 0},\n'
        s += '    }},\n'
        s += '    false\n'
        s += '  };\n'
        s += '}\n'
        return s
