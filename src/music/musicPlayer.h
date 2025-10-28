#pragma once

#include "buzzer.h"
#include "song.h"

#include <Arduino.h>

#include <array>
#include <vector>

class Player {
public:
  Player(const Track &track, int buzzer, uint64_t _songStartTimeUs = 0);
  ~Player();
  bool loop();
  uint32_t getSongLengthUs() const;
  uint32_t getPositionUs() const;
  bool isFinished() const;

  static uint64_t now();

private:
  const Track &_track;

  int _buzzer;
  uint64_t _songStartTimeUs;

  uint64_t _nextEventUs;

  size_t _currentIndex;
  bool _noteOn;
  bool _finished;
};
