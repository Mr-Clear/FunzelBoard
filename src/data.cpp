#include "data.h"

#include <Arduino.h>

Data currentData;

void Data::update(const std::array<float, 8> &adcValues, uint16_t pins)
{
  const auto lastButtons = _pressedButtons;

  _now = millis();
  _adcValues = adcValues;
  _pins = pins;

  _pressedButtons.reset();
  for (uint8_t i = 0; i < BUTTONS_MAP.size(); i++) {
    if (button(i)) {
    _pressedButtons.set(i);
    }
  }

  _buttonsDown = currentData.pressedButtons() & ~lastButtons;
  _buttonsUp = lastButtons & ~currentData.pressedButtons();

  for (int i = 0; i < BUTTONS_MAP.size(); i++) {
    if (_buttonsUp.test(i) || _buttonsDown.test(i)) {
      _buttonPressedOrder.remove(i);
    }
  }
  for (int i = 0; i < BUTTONS_MAP.size(); i++) {
    if (_buttonsDown.test(i)) {
      _lastPressedButtons.push_back(i);
      _buttonPressedOrder.push_back(i);
    }
  }
  while (_lastPressedButtons.size() > 10) {
    _lastPressedButtons.pop_front();
  }
}

time_t Data::now() const {
  return _now;
}

std::array<float, 8> Data::adcValues() const
{
  return _adcValues;
}

uint16_t Data::pins() const {
  return _pins;
}

Data::ButtonSet Data::pressedButtons() const {
  return _pressedButtons;
}

std::list<uint8_t> Data::lastPressedButtons() const
{
  return _lastPressedButtons;
}

std::list<uint8_t> Data::buttonPressedOrder() const
{
  return _buttonPressedOrder;
}

Data::ButtonSet Data::buttonsDown() const
{
  return _buttonsDown;
}

Data::ButtonSet Data::buttonsUp() const
{
  return _buttonsUp;
}

float Data::adcValue(uint8_t index) const {
  if (index >= _adcValues.size())
    return 0.0f;
  return _adcValues[index];
}

bool Data::pin(uint8_t pinIndex) const {
    return (_pins & (1 << pinIndex)) == 0;
}

bool Data::button(uint8_t buttonIndex) const {
  if (buttonIndex >= BUTTONS_MAP.size())
      return false;
  return pin(BUTTONS_MAP[buttonIndex]);
}

bool Data::anyButton() const {
  return (_pins & BUTTON_MASK) != BUTTON_MASK;
}

bool Data::switch2(uint8_t switchIndex) const {
  if (switchIndex >= SWITCHES2_MAP.size())
    return false;
  return pin(SWITCHES2_MAP[switchIndex]);
}

int8_t Data::switch3() const {
  return (pin(SWITCHES3_MAP.first) ? 1 : 0) - (pin(SWITCHES3_MAP.second) ? 1 : 0);
}

bool Data::plug(uint8_t plugIndex) const {
  if (plugIndex >= PLUGS_MAP.size())
    return false;
  return pin(PLUGS_MAP[plugIndex]);
}