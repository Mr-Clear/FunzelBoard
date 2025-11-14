#include "i2c.h"

#include "config.h"

#include <Arduino.h>
#include <Wire.h>

void I2C::init() {
  Wire.begin(SDA_PIN, SCL_PIN, SPEED);
}

std::vector<char> I2C::scan() {
  std::vector<char> foundDevices;
  for (char address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    const auto error = Wire.endTransmission();
    if (error == 0)
      foundDevices.push_back(address);
  }

  return foundDevices;
}
