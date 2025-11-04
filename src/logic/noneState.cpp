#include "noneState.h"

#include "color.h"
#include "config.h"
#include "data.h"
#include "pixels.h"

#include <Arduino.h>

#include <array>
#include <cmath>

namespace {

  constexpr auto speed =          5.0f;
  constexpr auto driftFactor =    0.30f;
  constexpr auto dimFactor =      0.10f;
  constexpr auto dimFactorBoost = 0.50f;
  constexpr auto fillFactor =     0.50f;

  class ColorF {
  public:
    float r, g, b;
    ColorF(float red, float green, float blue) : r{red}, g{green}, b{blue} { }
    ColorF() : ColorF{0.0f, 0.0f, 0.0f} { }
    ColorF operator*(float factor) const {
      return {r * factor, g * factor, b * factor};
    }
    ColorF operator+(const ColorF& other) const {
      return {r + other.r, g + other.g, b + other.b};
    }
    ColorF& operator+=(const ColorF& other) {
      r += other.r;
      g += other.g;
      b += other.b;
      return *this;
    }
    operator Color() const {
      return {
        static_cast<uint8_t>(std::clamp(static_cast<int>(std::round(r * 255)), 0, 255)),
        static_cast<uint8_t>(std::clamp(static_cast<int>(std::round(g * 255)), 0, 255)),
        static_cast<uint8_t>(std::clamp(static_cast<int>(std::round(b * 255)), 0, 255))
      };
    }
  };

  std::array<ColorF, PIXELS_RING_COUNT> ringColors;
  std::array<std::tuple<int, int, ColorF>, 4> buttons = { std::tuple<int, int, ColorF>
    {0, 0, ColorF{1, 0, 0}},
    {1, 2, ColorF{.5, .5, 0}},
    {2, 4, ColorF{0, 1, 0}},
    {3, 6, ColorF{0, 0, 1}},
  };
  unsigned long lastTime = 0;
}

void NoneState::enter() {
}

void NoneState::update() {
  const auto time = millis();
  const auto timeDiff = time - lastTime;
  lastTime = time;
  if (lastTime == 0 || timeDiff == 0)
    return;
  const auto timeFactor = static_cast<float>(timeDiff) / 1000.0f * speed;

  auto drift = driftFactor * timeFactor;
  auto dim = (currentData.button(0) ? dimFactorBoost : dimFactor) * timeFactor;
  const auto fill = fillFactor * timeFactor;

  if (2.0f * drift + dim > 1.0f) {
    const float scale = 1.0f / (2.0f * drift + dim);
    drift *= scale;
    dim   *= scale;
  }

  const auto lastColors = ringColors;
  for (int i = 0; i < PIXELS_RING_COUNT; i++) {
    const int leftNeighbour = (i - 1 + PIXELS_RING_COUNT) % PIXELS_RING_COUNT;
    const int rightNeighbour = (i + 1) % PIXELS_RING_COUNT;
    ringColors[i] = (
      lastColors[i] * (1.0f - 2.0f * drift - dim) +
      lastColors[leftNeighbour] * drift +
      lastColors[rightNeighbour] * drift
    );
  }

  for (int i = 0; i < PIXELS_RING_COUNT; i++)
    Pixels::setColor(PIXELS_RING_OFFSET + i, ringColors[i]);

  for (const auto& [buttonIndex, ledIndex, color] : buttons)
    if (currentData.button(buttonIndex))
      ringColors[ledIndex] += color * fill;

  for (int i = 0; i < PIXELS_RING_COUNT; i++)
    Pixels::setColor(PIXELS_RING_OFFSET + i, ringColors[i]);
}

void NoneState::exit() {
  for (int i = 0; i < PIXELS_RING_COUNT; i++) {
    Pixels::setColor(PIXELS_RING_OFFSET + i, BLACK);
  }
}
