#include "adc.h"
#include "i2c.h"

#include <ADS1115.h>
#include <Adafruit_MCP23X17.h>

#include <Arduino.h>

#include <array>

struct Data {
  std::array<float, 8> adcValues;
  uint16_t pins;
  bool pin(uint8_t pin) {
    return (pins & (1 << pin)) == 0;
  }
};

std::vector<String> setupErrors;

void handleSerial();

Adafruit_MCP23X17 mcp;

const std::array<uint8_t, 8> POTI_MAP = {4, 7, 6, 5, 1, 2, 3, 0};
const std::array<uint8_t, 5> BUTTONS_MAP = {4, 3, 2, 1, 0};
const std::array<uint8_t, 6> SWITCHES2_MAP = {15, 14, 13, 12, 11, 10};
const std::pair<uint8_t, uint8_t> SWITCHES3_MAP = {8, 9};

void setup() {
  Serial.begin(115200);
  Serial.println("Hello, world!");

  I2C::init();
  const auto errors = ADC::init();
  setupErrors.insert(setupErrors.end(), errors.begin(), errors.end());
  if (mcp.begin_I2C(0x20)) {
    for (uint8_t pin = 0; pin < 16; pin++) {
      mcp.pinMode(pin, INPUT_PULLUP);
    }
  } else {
    setupErrors.push_back("Failed to initialize MCP23017");
  }

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

bool showPotis = true;
bool showButtons = true;
bool showSwitches = true;
bool showAdcValues = false;
bool showPinValues = false;
bool scanI2C = false;
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
  data.pins = mcp.readGPIOAB();

  Serial.print(loopCount);
  Serial.print(": ");

  if (showPotis) {
    for(const auto index : POTI_MAP) {
      Serial.print(ADC::progress_bar(data.adcValues[index], 5));
      Serial.print(" ");
    }
  }

  if (showButtons) {
    for (const auto index : BUTTONS_MAP) {
      Serial.print(data.pin(index) ? "●" : "○");
      Serial.print(" ");
    }
    Serial.print(" ");
  }

  if (showSwitches) {
    for (const auto index : SWITCHES2_MAP) {
      Serial.print(data.pin(index) ? "▲" : "▼");
    }
    Serial.print(data.pin(SWITCHES3_MAP.first)
     ? (data.pin(SWITCHES3_MAP.second) ? "x" : "▼")
     : (data.pin(SWITCHES3_MAP.second) ? "▲" : "■"));
    Serial.print(" ");
  }

  if (showAdcValues) {
    for (const auto& val : data.adcValues) {
      Serial.print(val, 3);
      Serial.print(" ");
    }
  }

  if (showPinValues) {
    for (uint8_t pin = 0; pin < 16; pin++) {
      Serial.print(data.pin(pin) ? "0" : "1");
    }
    Serial.print(" ");
  }

  if (scanI2C) {
    const auto devices = I2C::scan();
    if (devices.empty()) {
      Serial.print("NoI2C devices found ");
    } else {
      for (const auto addr : devices) {
        Serial.print("0x");
        if (addr < 16)
          Serial.print("0");
        Serial.print(addr, HEX);
        Serial.print(" ");
      }
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
      case 'p':
        showPotis = !showPotis;
        break;
      case 'b':
        showButtons = !showButtons;
        break;
      case 's':
        showSwitches = !showSwitches;
        break;
      case 'a':
        showAdcValues = !showAdcValues;
        break;
      case 'd':
        showPinValues = !showPinValues;
        break;
      case 'i':
        scanI2C = !scanI2C;
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
      case 'u':
        if (mcp.begin_I2C(0x20)) {
          for (uint8_t pin = 0; pin < 16; pin++) {
            mcp.pinMode(pin, INPUT_PULLUP);
          }
        } else {
          Serial.println("Failed to initialize MCP23017");
        }
        break;
      case 'r':
        if (mcp.begin_I2C(0x20)) {
          for (uint8_t pin = 0; pin < 16; pin++) {
            mcp.pinMode(pin, INPUT_PULLDOWN);
          }
        } else {
          Serial.println("Failed to initialize MCP23017");
        }
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
      case 'q':
        for (int i = 9; i > 0; i--) {
          Serial.print(i);
          delay(1000);
        }
        Serial.println();
        break;
      default:
        Serial.println("Unknown command: '" + String((char)cmd) + "' (" + String((int)cmd) + ")");
        break;
    }
  }
}
