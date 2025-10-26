from typing import Callable, Iterable
import serial
import time
from serial.tools import list_ports
from song import Song, Note, Buzzer

class FunzlBoard:
    @staticmethod
    def send(command: str, progress_callback: Callable[[str], None] | None = None) -> str:
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
                    progress_callback(f'Sending {sent / length * 100:.2f} %')
                    t = time.time()
                ser.write(char.encode('utf-8'))
                sent += 1
                time.sleep(0.001)  # Small delay to allow ESP32 to process
            return f'Sent to {candidates[0]}.'

    @staticmethod
    def serialize_notes(notes: Iterable[Note], buzzer: Buzzer, start: int = 0) -> str:
        if not notes:
            return 'Nothing to send.'
        sorted_notes = sorted(notes, key=lambda n: n.start_us)
        result = 'X:'
        last_event = start
        for note in sorted_notes:
            if note.buzzer == buzzer:
                if note.start_us < start:
                    continue
                result += f'{note.start_us - last_event}|{note.pitch}:'
                result += f'{note.duration_us}|X:'
                last_event = note.end_us
        result += '0|'
        return result

    @staticmethod
    def send_notes(notes: Iterable[Note], start: int = -1, progress_callback: Callable[[str], None] | None = None) -> str:
        if start == -1:
            start = min(note.start_us for note in notes)
        to_send = 'S'
        for buzzer in [Buzzer.BUZZER_1, Buzzer.BUZZER_2, Buzzer.BUZZER_3]:
            buzzer_notes = [note for note in notes if note.buzzer == buzzer]
            if buzzer_notes:
                to_send += FunzlBoard.serialize_notes(buzzer_notes, buzzer, start) + "\n"
        to_send += '\n'
        print(to_send)
        FunzlBoard.send(to_send, progress_callback)
        return 'Notes sent.'
