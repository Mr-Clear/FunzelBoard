#include "adc.h"
#include "i2c.h"

#include <Arduino.h>
#include <ADS1115.h>

#include <array>

std::vector<String> setupErrors;

void setup() {
  Serial.begin(115200);
  Serial.println("Hello, world!");

  I2C::init();
  const auto errors = ADC::init();
  setupErrors.insert(setupErrors.end(), errors.begin(), errors.end());

  if (!setupErrors.empty()) {
    Serial.print("Errors during setup.. ");
    for (int i = 9; i > 0; i--) {
      Serial.print(i);
      delay(1000);
    }
    for (const auto& err : setupErrors) {
      Serial.println(err);
    }
  }
}

int loopCount = 0;
void loop() {
  loopCount++;
  Serial.print(loopCount);
  Serial.print(": ");
  const auto adcResults = ADC::readAll();
  if (!std::get<0>(adcResults).empty()) {
    for (const auto& err : std::get<0>(adcResults)) {
      Serial.println("ADC Error: " + err);
    }
  }
  for(const auto value : std::get<1>(adcResults)) {
    Serial.print(ADC::progress_bar(value, 5));
    Serial.print(" ");
  }
  Serial.println();
}
