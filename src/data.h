#pragma once

#include "config.h"

#include <array>
#include <cstdint>
#include <bitset>

struct Data {
  std::array<float, 8> adcValues;
  uint16_t pins;

  bool pin(uint8_t pinIndex) const {
    return (pins & (1 << pinIndex)) == 0;
  }

  bool button(uint8_t buttonIndex) const {
    if (buttonIndex >= BUTTONS_MAP.size())
      return false;
    return pin(BUTTONS_MAP[buttonIndex]);
  }

  bool anyButton() const {
    return (pins & BUTTON_MASK) != BUTTON_MASK;
  }

  std::bitset<BUTTONS_MAP.size()> pressedButtons() const {
    std::bitset<BUTTONS_MAP.size()> result;
    for (uint8_t i = 0; i < BUTTONS_MAP.size(); i++) {
      if (button(i)) {
        result.set(i);
      }
    }
    return result;
  }

  bool switch2(uint8_t switchIndex) const {
    if (switchIndex >= SWITCHES2_MAP.size())
      return false;
    return pin(SWITCHES2_MAP[switchIndex]);
  }

  int8_t switch3() const {
    return (pin(SWITCHES3_MAP.first) ? 1 : 0) - (pin(SWITCHES3_MAP.second) ? 1 : 0);
  }

  bool plug(uint8_t plugIndex) const {
    if (plugIndex >= PLUGS_MAP.size())
      return false;
    return pin(PLUGS_MAP[plugIndex]);
  }
};
