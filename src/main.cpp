#include "adc.h"
#include "i2c.h"

#include <Arduino.h>
#include <ADS1115.h>

#include <array>

struct Data {
  std::array<float, 8> adcValues;
};

std::vector<String> setupErrors;

void handleSerial();

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

bool showAdcValues = true;
int delayMs = 100;

int loopCount = 0;
void loop() {
  loopCount++;
  handleSerial();
  Data data;
  const auto adcResults = ADC::readAll();
  if (!std::get<0>(adcResults).empty()) {
    for (const auto& err : std::get<0>(adcResults)) {
      Serial.println("ADC Error: " + err);
    }
  }
  data.adcValues = std::get<1>(adcResults);

  Serial.print(loopCount);
  Serial.print(": ");
  if (showAdcValues) {
    for(const auto value : data.adcValues) {
      Serial.print(ADC::progress_bar(value, 5));
      Serial.print(" ");
    }
  }
  Serial.println();
  if (delayMs > 0)
    delay(delayMs);
}

void handleSerial() {
  while (Serial.available()) {
    const auto cmd = Serial.read();
    switch (cmd) {
      case 'a':
        showAdcValues = !showAdcValues;
        break;
      case '0':
        delayMs = 0;
        break;
      case '1':
        delayMs = 1;
        break;
      case '2':
        delayMs = 10;
        break;
      case '3':
        delayMs = 100;
        break;
      case '4':
        delayMs = 1000;
        break;
      case 'e':
        if (setupErrors.empty()) {
          Serial.println("No setup errors.");
          break;
        }
        for (const auto& err : setupErrors) {
          Serial.println("Setup Error: " + err);
        }
        break;
      case ' ':
        for (int i = 9; i > 0; i--) {
          Serial.print(i);
          delay(1000);
        }
        break;
      default:
        Serial.println("Unknown command: '" + String((char)cmd) + "' (" + String((int)cmd) + ")");
        break;
    }
  }
}
