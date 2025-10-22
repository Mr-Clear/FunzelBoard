#ifndef BUZZER_PLAYER_SYNC_H
#define BUZZER_PLAYER_SYNC_H

#include <Arduino.h>
#include "buzzer.h"
#include <string>
#include <vector>

struct NoteEvent {
  int freqHz;
  uint64_t durUs; // duration in microseconds
};

class Player {
public:
  // reserveEvents: optional capacity reservation
  Player(std::string_view songStr, int buzzer, uint64_t _songStartTimeUs = 0);

  // Non-blocking loop; call frequently from sketch loop().
  // Returns true when the song has completed playback.
  bool loop();

  // Restart playback from the beginning (non-blocking)
  void restart(int64_t _songStartTimeUs = 0);

  // Total song length in microseconds (sum of events parsed so far)
  uint64_t getSongLengthUs() const;

  // Current playback position in microseconds since the start of the song
  uint64_t getPositionUs() const;

  bool isFinished() const;
  size_t getEventCount() const;
  int getCurrentEventIndex() const;

  static uint64_t now();

private:
  std::string _song;
  int _buzzer;

  int _tempo;
  char _currentKey[16];

  std::vector<NoteEvent> _events;
  uint64_t _songLengthUs;

  // scheduling in microseconds
  uint64_t _songStartUs;        // absolute reference time (esp_timer)
  uint64_t _nextNoteStartUs;    // absolute time when next event should start
  uint64_t _noteEndUs;
  int _currentEventIndex;
  bool _finished;
  bool _playing;
  int _currentPlayingFreq;

  // helpers (same as previous)
  int baseSemitone(char letter) const;
  int keyAccidentalFor(const char *keyName, char pitchLetter) const;
  double midiToFreq(int midi) const;

  uint64_t durationUsFromDenominator(int denom) const;
  NoteEvent convertTokenToFreqDur(const std::string& tok);
  void parseSongIntoEvents();
  std::vector<std::string> tokenize(const std::string& s) const;
};

#endif // BUZZER_PLAYER_SYNC_H