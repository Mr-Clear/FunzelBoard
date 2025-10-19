#include "logic.h"

#include "data.h"
#include "buzzer.h"
#include "config.h"
#include "color.h"
#include "pixels.h"

#include <algorithm>
#include <array>
#include <bitset>
#include <cmath>
#include <list>
#include <iterator>

namespace {
  constexpr std::array<float, 5> tones{261.63f, 293.66f, 329.63f, 392.00f, 440.00f};
  // Patterns to detect octave up/down sequences
  constexpr std::array<uint8_t, 6> seq_up   {0, 1, 2, 3, 4, 0};
  constexpr std::array<uint8_t, 6> seq_down {4, 3, 2, 1, 0, 4};

  int octave = 4;
  float octaveMultiplier = 1.0f;
  std::bitset<BUTTONS_MAP.size()> lastButtons;
  std::list<uint8_t> lastPressedButtons;
  std::list<uint8_t> buttonPressedOrder;

  template <typename T, std::size_t N>
  bool ends_with(const std::list<T>& lst, const std::array<T, N>& pat) {
    if (lst.size() < N) return false;
    return std::equal(pat.rbegin(), pat.rend(), lst.rbegin());
  }
}

void Logic::loop(int loopCount, const Data& data) {
  const auto buttonsDown = data.pressedButtons() & ~lastButtons;
  const auto buttonsUp = lastButtons & ~data.pressedButtons();
  lastButtons = data.pressedButtons();

  for (int i = 0; i < BUTTONS_MAP.size(); i++) {
    if (buttonsUp.test(i) || buttonsDown.test(i)) {
      buttonPressedOrder.remove(i);
    }
  }
  for (int i = 0; i < BUTTONS_MAP.size(); i++) {
    if (buttonsDown.test(i)) {
      lastPressedButtons.push_back(i);
      buttonPressedOrder.push_back(i);
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

  if (buttonsDown.any()) {
    if (ends_with(lastPressedButtons, seq_up)) {
      octave = std::min(octave + 1, 8);
      octaveMultiplier = std::pow(2.0f, octave - 4);
    } else if (ends_with(lastPressedButtons, seq_down)) {
      octave = std::max(octave - 1, 1);
      octaveMultiplier = std::pow(2.0f, octave - 4);
    }
  }

  for (int i = 0; i < 12; i++) {
    Pixels::setColor(PIXELS_OCTAVE_OFFSET + i, RED);
  }

  for (int i = 0; i < 5; i++) {
    Pixels::setColor(PIXELS_OCTAVE_OFFSET + octave - 1 + i, GREEN / 2.f);
  }

  if (buttonPressedOrder.empty()) {
    Buzzer::off(0);
    Buzzer::off(1);
  } else {
    Buzzer::tone(0, tones[buttonPressedOrder.back() % tones.size()] * octaveMultiplier);
    Pixels::setColor(PIXELS_OCTAVE_OFFSET + octave - 1 + buttonPressedOrder.back(), WHITE);
    if (buttonPressedOrder.size() > 1) {
      auto secondLast = std::next(buttonPressedOrder.rbegin());
      Buzzer::tone(1, tones[*secondLast % tones.size()] * octaveMultiplier);
      Pixels::setColor(PIXELS_OCTAVE_OFFSET + octave - 1 + *secondLast, WHITE);
    } else {
      Buzzer::off(1);
    }
  }

  Pixels::show();
}
