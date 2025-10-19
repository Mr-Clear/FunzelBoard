#include "adc.h"
#include "buzzer.h"
#include "color.h"
#include "config.h"
#include "data.h"
#include "i2c.h"
#include "logic/logic.h"
#include "motor.h"
#include "pixels.h"

#include <ADS1115.h>
#include <Adafruit_MCP23X17.h>

#include <Arduino.h>

#include <array>

std::vector<String> setupErrors;
Adafruit_MCP23X17 mcp;

void handleSerial();

constexpr float MAX_BRIGHTNESS = 1.0f;
constexpr float MIN_BRIGHTNESS = 1.f / 255.f;

bool showPotis = true;
bool showButtons = true;
bool showSwitches = true;
bool showPlugs = true;
bool showAdcValues = false;
bool showPinValues = false;
bool showBrightness = false;
bool scanI2C = false;
bool blink = false;
int delayMs = 1;

void setup() {
  Serial.begin(115200);
  Serial.setTxTimeoutMs(0);
  Serial.println("Hello, world!");

  pinMode(BLINK_LED_PIN, OUTPUT);
  digitalWrite(BLINK_LED_PIN, HIGH);

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

  if (!Pixels::init()) {
    setupErrors.push_back("Failed to initialize NeoPixel");
  }

  Buzzer::init();
  Motor::init();

  if (!setupErrors.empty()) {
    blink = true;
    Serial.print("Errors during setup.. ");
    for (int i = 9; i > 0; i--) {
      Serial.print(i);
      delay(1000);
    }
    for (const auto& err : setupErrors) {
      Serial.println(err);
    }
  }

  Logic::start();
}

bool blinkOn = false;
int loopCount = 0;
void loop() {
  loopCount++;

  if (blink) {
    digitalWrite(BLINK_LED_PIN, blinkOn ? HIGH : LOW);
    blinkOn = !blinkOn;
  }

  handleSerial();
  const auto adcResults = ADC::readAll();
  if (!std::get<0>(adcResults).empty()) {
    for (const auto& err : std::get<0>(adcResults)) {
      Serial.println("ADC Error: " + err);
    }
  }
  currentData.update(std::get<1>(adcResults), mcp.readGPIOAB());
  const float brightness = std::clamp(currentData.adcValue(POTI_CONFIG_BRIGHTNESS) * currentData.adcValue(POTI_BRIGHTNESS), MIN_BRIGHTNESS, MAX_BRIGHTNESS);

  Serial.print(loopCount);
  Serial.print(": ");

  if (showPotis) {
    for(const auto index : POTI_MAP) {
      Serial.print(ADC::progress_bar(currentData.adcValue(index), 5));
      Serial.print(" ");
    }
  }

  if (showButtons) {
    for (const auto index : BUTTONS_MAP) {
      Serial.print(currentData.pin(index) ? "●" : "○");
      Serial.print(" ");
    }
    Serial.print(" ");
  }

  if (showSwitches) {
    for (const auto index : SWITCHES2_MAP) {
      Serial.print(currentData.pin(index) ? "▲" : "▼");
    }
    Serial.print(currentData.pin(SWITCHES3_MAP.first)
     ? (currentData.pin(SWITCHES3_MAP.second) ? "x" : "▼")
     : (currentData.pin(SWITCHES3_MAP.second) ? "▲" : "■"));
    Serial.print(" ");
  }

  if (showPlugs) {
    for (const auto index : PLUGS_MAP) {
      Serial.print(currentData.pin(index) ? "◎" : "○");
      Serial.print(" ");
    }
  }

  if (showAdcValues) {
    for (const auto& val : currentData.adcValues()) {
      Serial.print(val, 3);
      Serial.print(" ");
    }
  }

  if (showPinValues) {
    for (uint8_t pin = 0; pin < 16; pin++) {
      Serial.print(currentData.pin(pin) ? "0" : "1");
    }
    Serial.print(" ");
  }

  if (showBrightness) {
    Serial.print(String(brightness, 5));
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

  Pixels::setBrightness(brightness);
  Logic::loop(loopCount);

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
      case 'o':
        showPlugs = !showPlugs;
        break;
      case 'a':
        showAdcValues = !showAdcValues;
        break;
      case 'd':
        showPinValues = !showPinValues;
        break;
      case 'h':
        showBrightness = !showBrightness;
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
        }
        for (const auto& err : setupErrors) {
          Serial.println("Setup Error: " + err);
        }

        // Print SDK versions
        Serial.printf("Arduino-ESP32: %d.%d.%d\n",
                      ESP_ARDUINO_VERSION_MAJOR,
                      ESP_ARDUINO_VERSION_MINOR,
                      ESP_ARDUINO_VERSION_PATCH);
        Serial.printf("ESP-IDF: %s (%d.%d.%d)\n",
                      esp_get_idf_version(),
                      ESP_IDF_VERSION_MAJOR,
                      ESP_IDF_VERSION_MINOR,
                      ESP_IDF_VERSION_PATCH);
        break;
      case 'q':
        for (int i = 9; i > 0; i--) {
          Serial.print(i);
          delay(1000);
        }
        Serial.println();
        break;
      case 't':
        Buzzer::tone(0, 1000);
        break;
      case 'T':
        Buzzer::off(0);
        break;
      case 'z':
        Buzzer::tone(1, 2000);
        break;
      case 'Z':
        Buzzer::off(1);
        break;
      default:
        Serial.println("Unknown command: '" + String((char)cmd) + "' (" + String((int)cmd) + ")");
        break;
    }
  }
}
