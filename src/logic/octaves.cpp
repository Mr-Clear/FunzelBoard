#include "octaves.h"

#include "buzzer.h"
#include "color.h"
#include "data.h"
#include "pixels.h"

#include <cmath>
#include <iterator>

#include <Arduino.h>

namespace {
  constexpr std::array<float, 5> tones{261.63f, 293.66f, 329.63f, 392.00f, 440.00f};
  // Patterns to detect octave up/down sequences
  constexpr std::array<uint8_t, 6> seq_up   {0, 1, 2, 3, 4, 0};
  constexpr std::array<uint8_t, 6> seq_down {4, 3, 2, 1, 0, 4};

  int octave = 4;
  float octaveMultiplier = 1.0f;
  time_t stateEntered = 0;

  template <typename T, std::size_t N>
  bool ends_with(const std::list<T>& lst, const std::array<T, N>& pat) {
    if (lst.size() < N) return false;
    return std::equal(pat.rbegin(), pat.rend(), lst.rbegin());
  }
}

void OctavesState::enter() {
  stateEntered = currentData.now();
}

void OctavesState::update() {
  if (currentData.buttonsDown().any())
  {
    if (ends_with(currentData.lastPressedButtons(), seq_up)) {
      octave = std::min(octave + 1, 8);
      octaveMultiplier = std::pow(2.0f, octave - 4);
    } else if (ends_with(currentData.lastPressedButtons(), seq_down)) {
      octave = std::max(octave - 1, 1);
      octaveMultiplier = std::pow(2.0f, octave - 4);
    }
  }

  const float pitch = currentData.adcValue(POTI_R) + 0.5f;

  const int pixelShift = static_cast<int>((pitch - 1.0f) * 8.0f);

  auto pi = [pixelShift] (int i) { return PIXELS_RING_OFFSET  + (PIXELS_RING_COUNT  + i + pixelShift) % PIXELS_RING_COUNT; };

  for (const int i : {0, 1, 14, 15}) {
    Pixels::setColor(pi(i), BLACK);
  }

  for (int i = 0; i < 12; i++) {
    Pixels::setColor(pi(i + 2), RED);
  }

  for (int i = 0; i < 5; i++) {
    Pixels::setColor(pi(octave - 1 + i + 2), GREEN);
  }

  for (int i = 0; i < BUZZER_PINS.size(); i++) {
    if (i >= currentData.buttonPressedOrder().size()) {
      Buzzer::off(i);
    } else {
      const auto btn = *std::next(currentData.buttonPressedOrder().rbegin(), i);
      Buzzer::tone(i, tones[btn] * octaveMultiplier * pitch);
      Pixels::setColor(pi(octave - 1 + btn + 2), WHITE);
    }
  }
}

void OctavesState::exit() {
  Buzzer::off(0);
  Buzzer::off(1);
  for (int i = 0; i < PIXELS_RING_COUNT; i++) {
    Pixels::setColor(PIXELS_RING_OFFSET + i, BLACK);
  }
}
