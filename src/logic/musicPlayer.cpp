#include "musicPlayer.h"
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include <ctype.h>
#include "esp_timer.h"

Player::Player(std::string_view song, int buzzer, uint64_t _songStartTimeUs) :
  _song{song},
  _buzzer{buzzer},
  _songStartTimeUs{_songStartTimeUs == 0 ? now() : _songStartTimeUs},
  _songLengthUs{calculateLengthUs(song)},
  _nextNoteStartUs{_songStartTimeUs},
  _currentIndex{0},
  _finished{false} {

}

Player::~Player() {
  Buzzer::off(_buzzer);
}

bool Player::loop() {
  const auto currentTimeUs = now();
  if (_finished) {
    return false;
  }

  const auto nextNoteTimeUs = _nextNoteStartUs;
  if (currentTimeUs >= nextNoteTimeUs) {
    const auto event = nextEvent(_song, _currentIndex);
    if (event.empty()) {
      _finished = true;
      Buzzer::off(_buzzer);
      return false;
    }
    const auto colonPos = event.find(':');
    if (colonPos == std::string_view::npos) {
      _finished = true;
      Buzzer::off(_buzzer);
      return false;
    }
    const auto noteStr = event.substr(0, colonPos);
    if (noteStr == "X") {
      Buzzer::off(_buzzer);
    } else {
      const auto noteNr = std::stoi(noteStr.data());
      const auto freqHz = static_cast<int>(440.0 * std::pow(2.0, (noteNr - 69) / 12.0));
      Buzzer::tone(_buzzer, freqHz);
    }
    const auto durStr = event.substr(colonPos + 1);
    const uint64_t durUs = std::stoull(durStr.data(), nullptr, 10);
    _nextNoteStartUs += durUs;
    _currentIndex += event.size() + 1;
  }

  return true;
}

uint64_t Player::getSongLengthUs() const {
  return _songLengthUs;
}

uint64_t Player::getPositionUs() const {
  return now() - _songStartTimeUs;
}

bool Player::isFinished() const {
  return _finished;
}

uint64_t Player::now()
{
  return esp_timer_get_time();
}

uint64_t Player::calculateLengthUs(std::string_view song) {
  uint64_t length = 0;
  size_t index = 0;
  while (index < song.size()) {
    const auto event = nextEvent(song, index);
    if (event.empty()) {
      break;
    }
    const auto colonPos = event.find(':');
    if (colonPos == std::string_view::npos) {
      break;
    }
    const auto durStr = event.substr(0, colonPos);
    const uint64_t durUs = std::strtoull(durStr.data(), nullptr, 10);
    length += durUs;
    index += event.size() + 1;
  }
  return length;
}

std::string_view Player::nextEvent(std::string_view song, int index) {
  for (auto i = 1; index + i < song.size(); ++i) {
    if (song[index + i] == '|') {
      return song.substr(index, i);
    }
  }
  return std::string_view();
}
