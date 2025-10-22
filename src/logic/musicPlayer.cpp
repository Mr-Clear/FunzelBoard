#include "musicPlayer.h"
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include <ctype.h>
#include "esp_timer.h" // for esp_timer_get_time()

// small silence inserted between identical notes (microseconds)
static const uint64_t MIN_SILENCE_US = 10ULL * 1000ULL; // 10 ms

// ----------------- Constructor -----------------
Player::Player(std::string_view songStr, int buzzer, uint64_t _songStartTimeUs)
  : _song(songStr), _buzzer(buzzer), _songStartUs(_songStartTimeUs == 0 ? esp_timer_get_time() : _songStartTimeUs)
{
  _tempo = 120;
  strncpy(_currentKey, "C", sizeof(_currentKey)-1);
  _currentKey[sizeof(_currentKey)-1] = '\0';

  _currentEventIndex = 0;
  _finished = false;
  _playing = false;
  _currentPlayingFreq = 0;
  _songLengthUs = 0;

  parseSongIntoEvents();

  _nextNoteStartUs = _songStartUs;
  _noteEndUs = 0;
  if (_events.empty()) _finished = true;
}

bool Player::loop() {
  if (_finished) return true;

  uint64_t nowUs = esp_timer_get_time();

  if (_playing && nowUs >= _noteEndUs) {
    Buzzer::tone(_buzzer, 0);
    _playing = false;
    _currentPlayingFreq = 0;
    _nextNoteStartUs = nowUs;
  }

  if (nowUs < _nextNoteStartUs)
    return false;

  if (_currentEventIndex >= (int)_events.size()) {
    _finished = true;
    return true;
  }

  NoteEvent ev = _events[_currentEventIndex];
  uint64_t startNow = nowUs;

  if (ev.freqHz > 0 && ev.durUs > 0) {
    Buzzer::tone(_buzzer, ev.freqHz);
    _playing = true;
    _currentPlayingFreq = ev.freqHz;
  } else {
    if (_playing) {
      Buzzer::tone(_buzzer, 0);
      _playing = false;
      _currentPlayingFreq = 0;
    }
  }

  _noteEndUs = startNow + ev.durUs;
  _nextNoteStartUs = _noteEndUs;
  _currentEventIndex++;

  return false;
}

void Player::restart(int64_t _songStartTimeUs) {
  _songStartUs = _songStartTimeUs == 0 ? esp_timer_get_time() : _songStartTimeUs;
  _nextNoteStartUs = _songStartUs;
  _noteEndUs = 0;
  _currentEventIndex = 0;
  _finished = _events.empty();
  _playing = false;
  _currentPlayingFreq = 0;
  Buzzer::tone(_buzzer, 0);
}

uint64_t Player::getSongLengthUs() const {
  return _songLengthUs;
}

uint64_t Player::getPositionUs() const {
  if (_finished) return _songLengthUs;
  uint64_t now = esp_timer_get_time();
  if (now < _songStartUs) return 0;
  uint64_t pos = now - _songStartUs;
  if (pos > _songLengthUs) pos = _songLengthUs;
  return pos;
}

bool Player::isFinished() const { return _finished; }
size_t Player::getEventCount() const { return _events.size(); }
int Player::getCurrentEventIndex() const { return _currentEventIndex; }

uint64_t Player::now() {
  return esp_timer_get_time();
}

int Player::baseSemitone(char letter) const {
  switch (letter) {
    case 'C': return 0;
    case 'D': return 2;
    case 'E': return 4;
    case 'F': return 5;
    case 'G': return 7;
    case 'A': return 9;
    case 'B': return 11;
  }
  return 0;
}

int Player::keyAccidentalFor(const char *keyName, char pitchLetter) const {
  struct KeyInfo {
    const char* name;
    int sharps; // positive = sharps, negative = flats
  };
  static const KeyInfo keyTable[] = {
    {"C", 0}, {"G", 1}, {"D", 2}, {"A", 3}, {"E", 4}, {"B", 5}, {"F#", 6}, {"C#", 7},
    {"F", -1}, {"Bb", -2}, {"Eb", -3}, {"Ab", -4}, {"Db", -5}, {"Gb", -6}, {"Cb", -7}
  };

  int acc = 0;
  for (const auto& ki : keyTable) {
    if (strcmp(ki.name, keyName) == 0) {
      acc = ki.sharps;
      break;
    }
  }

  // Determine if pitchLetter is affected by key signature
  const char orderOfSharps[] = {'F', 'C', 'G', 'D', 'A', 'E', 'B'};
  const char orderOfFlats[] = {'B', 'E', 'A', 'D', 'G', 'C', 'F'};

  if (acc > 0) {
    for (int i = 0; i < acc; ++i) {
      if (pitchLetter == orderOfSharps[i]) return 1;
    }
  } else if (acc < 0) {
    for (int i = 0; i < -acc; ++i) {
      if (pitchLetter == orderOfFlats[i]) return -1;
    }
  }

  return 0;
}

double Player::midiToFreq(int midi) const {
  return 440.0 * pow(2.0, (midi - 69) / 12.0);
}

// duration calculation in microseconds
uint64_t Player::durationUsFromDenominator(int denom) const {
  // quarter note in microseconds
  uint64_t quarterUs = (60000000ULL) / (uint64_t)_tempo; // integer division is fine
  uint64_t durUs = (quarterUs * 4ULL) / (uint64_t)denom;
  return durUs;
}

NoteEvent Player::convertTokenToFreqDur(const std::string& tok) {
  NoteEvent ev;
  ev.freqHz = 0;
  ev.durUs = 0;
  if (tok.empty()) return ev;
  if (tok == "|") return ev;

  if (tok.size() >= 3 && tok[0] == 'T' && tok[1] == ':') {
    _tempo = atoi(tok.c_str() + 2);
    return ev;
  }
  if (tok.size() >= 3 && tok[0] == 'K' && tok[1] == ':') {
    strncpy(_currentKey, tok.c_str() + 2, sizeof(_currentKey)-1);
    _currentKey[sizeof(_currentKey)-1] = '\0';
    return ev;
  }

  if (tok[0] == 'R') {
    auto slash = tok.find('/');
    if (slash == std::string::npos) return ev;
    int denom = atoi(tok.c_str() + (slash + 1));
    bool dotted = (tok.find('.') != std::string::npos);
    uint64_t dur = durationUsFromDenominator(denom);
    if (dotted) dur = (dur * 3ULL) / 2ULL;
    ev.freqHz = 0;
    ev.durUs = dur;
    return ev;
  }

  const char* p = tok.c_str();
  char pitch = p[0];
  int pos = 1;
  int explicitAcc = 0;
  if (p[pos] == '#' || p[pos] == 'b' || p[pos] == 'n') {
    if (p[pos] == '#') explicitAcc = 1;
    else if (p[pos] == 'b') explicitAcc = -1;
    else explicitAcc = 2;
    pos++;
  }

  int octave = 4;
  if (p[pos] >= '0' && p[pos] <= '9') {
    octave = 0;
    while (p[pos] >= '0' && p[pos] <= '9') {
      octave = octave*10 + (p[pos]-'0');
      pos++;
    }
  }

  auto slash = tok.find('/');
  if (slash == std::string::npos) return ev;
  int denom = atoi(tok.c_str() + (slash + 1));
  bool dotted = (tok.find('.') != std::string::npos);
  uint64_t dur = durationUsFromDenominator(denom);
  if (dotted) dur = (dur * 3ULL) / 2ULL;
  ev.durUs = dur;

  int acc = 0;
  if (explicitAcc == 1) acc = 1;
  else if (explicitAcc == -1) acc = -1;
  else if (explicitAcc == 2) acc = 0;
  else acc = keyAccidentalFor(_currentKey, pitch);

  int sem = baseSemitone(pitch) + acc;
  while (sem < 0) { sem += 12; octave -= 1; }
  while (sem > 11) { sem -= 12; octave += 1; }

  int midi = 12 * (octave + 1) + sem;
  double freq = midiToFreq(midi);
  ev.freqHz = int(freq + 0.5);
  return ev;
}

std::vector<std::string> Player::tokenize(const std::string& s) const {
  std::vector<std::string> toks;
  std::string cur;
  for (size_t i = 0; i < s.size(); ++i) {
    char c = s[i];
    if (c == '|' ) {
      if (!cur.empty()) { toks.push_back(cur); cur.clear(); }
      toks.push_back(std::string("|"));
    } else if (c == ' ' || c == '\t' || c == '\r' || c == '\n') {
      if (!cur.empty()) { toks.push_back(cur); cur.clear(); }
    } else {
      cur.push_back(c);
    }
  }
  if (!cur.empty()) toks.push_back(cur);
  return toks;
}

void Player::parseSongIntoEvents() {
  _events.clear();
  _songLengthUs = 0;
  auto tokens = tokenize(_song);
  for (const auto& tok : tokens) {
    NoteEvent ev = convertTokenToFreqDur(tok);
    if (ev.durUs > 0) {
      _events.push_back(ev);
    }
  }

  // Insert short silence between identical consecutive notes — but subtract from previous note to keep overall length
  for (size_t i = 1; i < _events.size(); ++i) {
    NoteEvent& prev = _events[i-1];
    NoteEvent& cur  = _events[i];
    if (prev.freqHz > 0 && cur.freqHz > 0 && prev.freqHz == cur.freqHz) {
      uint64_t restUs = MIN_SILENCE_US;
      uint64_t origPrev = prev.durUs;
      if (origPrev > restUs + 1000ULL) { // keep at least 1 ms
        prev.durUs = origPrev - restUs;
      } else {
        if (origPrev > 1000ULL) {
          restUs = restUs - (origPrev - 1000ULL);
          prev.durUs = 1000ULL;
        } else {
          prev.durUs = origPrev;
        }
      }
      NoteEvent restEv; restEv.freqHz = 0; restEv.durUs = restUs;
      _events.insert(_events.begin() + i, restEv);
      ++i;
    }
  }

  // recompute total length
  _songLengthUs = 0;
  for (const auto& e : _events) _songLengthUs += e.durUs;
}
