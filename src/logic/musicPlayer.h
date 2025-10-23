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
  Player(std::string_view song, int buzzer, uint64_t _songStartTimeUs = 0);
  ~Player();
  bool loop();
  uint64_t getSongLengthUs() const;
  uint64_t getPositionUs() const;
  bool isFinished() const;

  static uint64_t now();
  static uint64_t calculateLengthUs(std::string_view song);
  static std::string_view nextEvent(std::string_view song, int index);

private:
  std::string _song;
  int _buzzer;
  uint64_t _songStartTimeUs;

  uint64_t _songLengthUs;
  uint64_t _nextNoteStartUs;

  size_t _currentIndex;
  bool _finished;
};

#endif // BUZZER_PLAYER_SYNC_H