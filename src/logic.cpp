#include "logic.h"

#include "data.h"
#include "buzzer.h"
#include "config.h"
#include "color.h"
#include "pixels.h"

#include <algorithm>
#include <array>
#include <bitset>
#include <list>
#include <iterator>

namespace {
  constexpr std::array<float, 5> tones{261.63f, 293.66f, 329.63f, 392.00f, 440.00f};
  float octave = 1.0f;
  std::bitset<BUTTONS_MAP.size()> lastButtons;
  std::list<uint8_t> lastPressedButtons;

  template <typename T, std::size_t N>
  bool ends_with(const std::list<T>& lst, const std::array<T, N>& pat) {
    if (lst.size() < N) return false;
    return std::equal(pat.rbegin(), pat.rend(), lst.rbegin());
  }

  // Patterns to detect octave up/down sequences
  constexpr std::array<uint8_t, 6> seq_up   {0, 1, 2, 3, 4, 0};
  constexpr std::array<uint8_t, 6> seq_down {4, 3, 2, 1, 0, 4};
}

void Logic::loop(int loopCount, const Data& data) {
  const auto buttonsDown = data.pressedButtons() & ~lastButtons;
  const auto buttonsUp = lastButtons & ~data.pressedButtons();
  lastButtons = data.pressedButtons();

  for (int i = 0; i < BUTTONS_MAP.size(); i++) {
    if (buttonsDown.test(i)) {
      lastPressedButtons.push_back(i);
    }
  }
  while (lastPressedButtons.size() > 10) {
    lastPressedButtons.pop_front();
  }

  Pixels::clear();
  constexpr Color off = BLACK;

  for (uint8_t button = 0; button < BUTTONS_MAP.size(); button++) {
    Pixels::setColor(button, data.pin(BUTTONS_MAP[button]) ? WHITE : off);
  }
  for (uint8_t swtch = 0; swtch < SWITCHES2_MAP.size(); swtch++) {
    Pixels::setColor(swtch + 8, data.pin(SWITCHES2_MAP[swtch]) ? WHITE : off);
  }
  Pixels::setColor(14, data.switch3() > 0
    ? RED
    : (data.switch3() < 0
      ? GREEN
      : off));
  Pixels::setColor(16, data.plug(0) ? BLUE : off);
  Pixels::setColor(17, data.plug(1) ? RED : off);
  Pixels::setColor(18, data.plug(2) ? YELLOW : off);
  Pixels::show();

  if (buttonsDown.any()) {
    if (ends_with(lastPressedButtons, seq_up)) {
      octave = std::min(octave * 2.0f, 32.0f);
    } else if (ends_with(lastPressedButtons, seq_down)) {
      octave = std::max(octave / 2.0f, 1.f / 4.f);
    }
  }

  for (int i = 0; i < BUTTONS_MAP.size(); i++) {
    if (buttonsDown.test(i)) {
      Buzzer::tone(0, tones[i % tones.size()] * octave);
      return;
    }
  }
  if (data.pressedButtons().none()) {
    Buzzer::off(0);
  }
}