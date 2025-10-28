#include "musicPlayer.h"
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include <ctype.h>
#include "esp_timer.h"

Player::Player(const Track &track, int buzzer, uint64_t _songStartTimeUs) :
  _track{track},
  _buzzer{buzzer},
  _songStartTimeUs{_songStartTimeUs == 0 ? now() : _songStartTimeUs},
  _currentIndex{0},
  _noteOn{false}
{
  if (track.length > 0) {
    _nextEventUs = _songStartTimeUs + track.notes[0].startUs;
    _finished = false;
  } else {
    _nextEventUs = _songStartTimeUs;
    _finished = true;
  }
  Serial.print("Player created for buzzer ");;
  Serial.print(buzzer);
  Serial.print(", duration: ");
  Serial.print(getSongLengthUs());
  Serial.println(" us");
}

Player::~Player() {
  Buzzer::off(_buzzer);
}

bool Player::loop() {
  const auto currentTimeUs = now();
  if (_finished) {
    return false;
  }

  while(_nextEventUs <= currentTimeUs) {
    if (_currentIndex >= _track.length) {
      _finished = true;
      Buzzer::off(_buzzer);
      return false;
    }
    const auto &note = _track.notes[_currentIndex];
    if (!_noteOn && currentTimeUs >= _songStartTimeUs + note.startUs) {
      // Note on
      const auto freqHz = static_cast<float>(440.0 * std::pow(2.0, (note.pitch - 69) / 12.0));
      Buzzer::tone(_buzzer, freqHz);
      _noteOn = true;
      _nextEventUs = _songStartTimeUs + note.endUs;
    } else if (_noteOn && currentTimeUs >= _songStartTimeUs + note.endUs) {
      // Note off
      Buzzer::off(_buzzer);
      _noteOn = false;
      _currentIndex++;
      if (_currentIndex < _track.length) {
        _nextEventUs = _songStartTimeUs + _track.notes[_currentIndex].startUs;
      }
    } else {
      break;
    }
  }
  return true;
}

uint32_t Player::getSongLengthUs() const {
  return _track.length > 0 ? _track.notes[_track.length - 1].endUs : 0;
}

uint32_t Player::getPositionUs() const {
  return now() - _songStartTimeUs;
}

bool Player::isFinished() const {
  return _finished;
}

uint64_t Player::now()
{
  return esp_timer_get_time();
}
