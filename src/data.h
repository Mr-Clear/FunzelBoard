#pragma once

#include "config.h"

#include <array>
#include <cstdint>
#include <bitset>
#include <list>
#include <time.h>

class Data {
public:
  using ButtonSet = std::bitset<BUTTONS_MAP.size()>;

  void update(const std::array<float, 8>& adcValues, uint16_t pins);

  time_t now() const;
  std::array<float, 8> adcValues() const;
  uint16_t pins() const;
  ButtonSet pressedButtons() const;
  std::list<uint8_t> lastPressedButtons() const;
  std::list<uint8_t> buttonPressedOrder() const;
  ButtonSet buttonsDown() const;
  ButtonSet buttonsUp() const;

  float adcValue(uint8_t index) const;
  bool pin(uint8_t pinIndex) const;
  bool button(uint8_t buttonIndex) const;
  bool anyButton() const;
  bool switch2(uint8_t switchIndex) const;
  int8_t switch3() const;
  bool plug(uint8_t plugIndex) const;

private:
  time_t _now;
  std::array<float, 8> _adcValues;
  uint16_t _pins;
  ButtonSet _pressedButtons;
  std::list<uint8_t> _lastPressedButtons;
  std::list<uint8_t> _buttonPressedOrder;
  ButtonSet _buttonsDown;
  ButtonSet _buttonsUp;

};

extern Data currentData;
