#include "adc.h"
#include "color.h"
#include "i2c.h"

#include <ADS1115.h>
#include <Adafruit_MCP23X17.h>
#include <Adafruit_NeoPixel.h>

#include <Arduino.h>

#include <array>

constexpr uint8_t BLINK_LED_PIN = 5;
constexpr int NUM_LEDS = 100;
constexpr uint8_t LED_PIN = 10;
std::vector<String> setupErrors;
Adafruit_MCP23X17 mcp;
Adafruit_NeoPixel pixels(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);

void handleSerial();

constexpr std::array<uint8_t, 8> POTI_MAP = {4, 7, 6, 5, 1, 2, 3, 0};
constexpr uint8_t POTI_CONFIG_BRIGHTNESS = POTI_MAP[0];
constexpr uint8_t POTI_BRIGHTNESS = POTI_MAP[2];
constexpr std::array<uint8_t, 5> BUTTONS_MAP = {4, 3, 2, 1, 0};
constexpr std::array<uint8_t, 6> SWITCHES2_MAP = {15, 14, 13, 12, 11, 10};
constexpr std::pair<uint8_t, uint8_t> SWITCHES3_MAP = {8, 9};
constexpr std::array<uint8_t, 3> PLUGSS_MAP = {7, 6, 5};

constexpr float MAX_BRIGHTNESS = 1.0f;
constexpr float MIN_BRIGHTNESS = 1.f / 255.f;

struct Data {
  std::array<float, 8> adcValues;
  uint16_t pins;

  bool pin(uint8_t pinIndex) {
    return (pins & (1 << pinIndex)) == 0;
  }

  bool button(uint8_t buttonIndex) {
    if (buttonIndex >= BUTTONS_MAP.size())
      return false;
    return pin(BUTTONS_MAP[buttonIndex]);
  }

  bool switch2(uint8_t switchIndex) {
    if (switchIndex >= SWITCHES2_MAP.size())
      return false;
    return pin(SWITCHES2_MAP[switchIndex]);
  }

  int8_t switch3() {
    return (pin(SWITCHES3_MAP.first) ? 1 : 0) - (pin(SWITCHES3_MAP.second) ? 1 : 0);
  }

  bool plug(uint8_t plugIndex) {
    if (plugIndex >= PLUGSS_MAP.size())
      return false;
    return pin(PLUGSS_MAP[plugIndex]);
  }
};

bool showPotis = true;
bool showButtons = true;
bool showSwitches = true;
bool showPlugs = true;
bool showAdcValues = false;
bool showPinValues = false;
bool showBrightness = false;
bool scanI2C = false;
bool blink = false;
int delayMs = 100;

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

  if (!pixels.begin()) {
    setupErrors.push_back("Failed to initialize NeoPixel");
  }

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
  Data data;
  const auto adcResults = ADC::readAll();
  if (!std::get<0>(adcResults).empty()) {
    for (const auto& err : std::get<0>(adcResults)) {
      Serial.println("ADC Error: " + err);
    }
  }
  data.adcValues = std::get<1>(adcResults);
  data.pins = mcp.readGPIOAB();

  float brightness = std::clamp(data.adcValues[POTI_CONFIG_BRIGHTNESS] * data.adcValues[POTI_BRIGHTNESS], MIN_BRIGHTNESS, MAX_BRIGHTNESS);

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

  if (showPlugs) {
    for (const auto index : PLUGSS_MAP) {
      Serial.print(data.pin(index) ? "◎" : "○");
      Serial.print(" ");
    }
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

  pixels.clear();
  constexpr Color off = BLACK;
  for (uint8_t button = 0; button < BUTTONS_MAP.size(); button++) {
    pixels.setPixelColor(button, data.pin(BUTTONS_MAP[button]) ? WHITE * brightness : off);
  }
  for (uint8_t swtch = 0; swtch < SWITCHES2_MAP.size(); swtch++) {
    pixels.setPixelColor(swtch + 5, data.pin(SWITCHES2_MAP[swtch]) ? WHITE * brightness : off);
  }
  pixels.setPixelColor(11, data.switch3() > 0
    ? RED * brightness
    : (data.switch3() < 0
      ? GREEN * brightness
      : off));
  pixels.setPixelColor(12, data.plug(0) ? BLUE * brightness : off);
  pixels.setPixelColor(13, data.plug(1) ? RED * brightness : off);
  pixels.setPixelColor(14, data.plug(2) ? YELLOW * brightness : off);
  pixels.show();

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
