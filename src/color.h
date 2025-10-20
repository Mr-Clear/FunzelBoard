#pragma once

#include <algorithm>
#include <cmath>
#include <cstdint>

struct Color {
  constexpr Color(uint8_t r, uint8_t g, uint8_t b) : r(r), g(g), b(b)
  { }
  constexpr Color(uint8_t r, uint8_t g, uint8_t b, float brightness) : Color(
      static_cast<uint8_t>(std::round(static_cast<float>(r) * brightness)),
      static_cast<uint8_t>(std::round(static_cast<float>(g) * brightness)),
      static_cast<uint8_t>(std::round(static_cast<float>(b) * brightness)))
  { }

  constexpr operator uint32_t() const {
    return (static_cast<uint32_t>(r) << 16) | (static_cast<uint32_t>(g) << 8) | static_cast<uint32_t>(b);
  }

  constexpr Color operator*(float brightness) const {
    return Color{r, g, b, brightness};
  }

  constexpr Color operator/(float divisor) const {
    return Color{
      static_cast<uint8_t>(std::min(static_cast<int>(static_cast<float>(r) / divisor), 255)),
      static_cast<uint8_t>(std::min(static_cast<int>(static_cast<float>(g) / divisor), 255)),
      static_cast<uint8_t>(std::min(static_cast<int>(static_cast<float>(b) / divisor), 255))
    };
  }

  constexpr Color operator+(const Color& other) const {
    return Color{
      static_cast<uint8_t>(std::min(static_cast<int>(r) + static_cast<int>(other.r), 255)),
      static_cast<uint8_t>(std::min(static_cast<int>(g) + static_cast<int>(other.g), 255)),
      static_cast<uint8_t>(std::min(static_cast<int>(b) + static_cast<int>(other.b), 255))
    };
  }

  constexpr Color operator-(const Color& other) const {
    return Color{
      static_cast<uint8_t>(std::max(static_cast<int>(r) - static_cast<int>(other.r), 0)),
      static_cast<uint8_t>(std::max(static_cast<int>(g) - static_cast<int>(other.g), 0)),
      static_cast<uint8_t>(std::max(static_cast<int>(b) - static_cast<int>(other.b), 0))
    };
  }

  constexpr Color operator*(const Color& other) const {
    return Color{
      static_cast<uint8_t>(std::round((static_cast<float>(r) * static_cast<float>(other.r)) / 255)),
      static_cast<uint8_t>(std::round((static_cast<float>(g) * static_cast<float>(other.g)) / 255)),
      static_cast<uint8_t>(std::round((static_cast<float>(b) * static_cast<float>(other.b)) / 255))
    };
  }

  uint8_t r, g, b;
};

constexpr Color RED = Color{255, 0, 0};
constexpr Color GREEN = Color{0, 255, 0};
constexpr Color BLUE = Color{0, 0, 255};
constexpr Color YELLOW = Color{255, 255, 0};
constexpr Color CYAN = Color{0, 255, 255};
constexpr Color MAGENTA = Color{255, 0, 255};
constexpr Color WHITE = Color{255, 255, 255};
constexpr Color BLACK = Color{0, 0, 0};
