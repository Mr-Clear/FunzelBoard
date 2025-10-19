#include "octaves.h"

#include "buzzer.h"
#include "color.h"
#include "data.h"
#include "pixels.h"

#include <cmath>
#include <iterator>

namespace {
  constexpr std::array<float, 5> tones{261.63f, 293.66f, 329.63f, 392.00f, 440.00f};
  // Patterns to detect octave up/down sequences
  constexpr std::array<uint8_t, 6> seq_up   {0, 1, 2, 3, 4, 0};
  constexpr std::array<uint8_t, 6> seq_down {4, 3, 2, 1, 0, 4};

  int octave = 4;
  float octaveMultiplier = 1.0f;

  template <typename T, std::size_t N>
  bool ends_with(const std::list<T>& lst, const std::array<T, N>& pat) {
    if (lst.size() < N) return false;
    return std::equal(pat.rbegin(), pat.rend(), lst.rbegin());
  }
}

void octaves()
{

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

  for (int i = 0; i < 12; i++) {
    Pixels::setColor(PIXELS_OCTAVE_OFFSET + i, RED);
  }

  for (int i = 0; i < 5; i++) {
    Pixels::setColor(PIXELS_OCTAVE_OFFSET + octave - 1 + i, GREEN);
  }

  if (currentData.buttonPressedOrder().empty()) {
    Buzzer::off(0);
    Buzzer::off(1);
  } else {
    Buzzer::tone(0, tones[currentData.buttonPressedOrder().back()] * octaveMultiplier);
    Pixels::setColor(PIXELS_OCTAVE_OFFSET + octave - 1 + currentData.buttonPressedOrder().back(), WHITE);
    if (currentData.buttonPressedOrder().size() > 1) {
      const auto secondLast = *std::next(currentData.buttonPressedOrder().rbegin());
      Buzzer::tone(1, tones[secondLast] * octaveMultiplier);
      Pixels::setColor(PIXELS_OCTAVE_OFFSET + octave - 1 + secondLast, WHITE);
    } else {
      Buzzer::off(1);
    }
  }
}