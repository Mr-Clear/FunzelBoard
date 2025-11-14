#include "adc.h"
#include "buzzer.h"
#include "color.h"
#include "config.h"
#include "data.h"
#include "i2c.h"
#include "logic/logic.h"
#include "music/musicPlayer.h"
#include "motor.h"
#include "pixels.h"
#include "tools.h"

#include <Adafruit_MCP23X17.h>

#include <Arduino.h>

#include <array>

std::vector<String> setupErrors;
Adafruit_MCP23X17 mcp;

void handleSerial();
std::string readSerial(std::string_view endPattern, std::string_view prompt, bool echo);
Song readSongFromSerial();

constexpr float MAX_BRIGHTNESS = 1.0f;
constexpr float MIN_BRIGHTNESS = 1.f / 255.f;

bool serialOutput = true;
bool showPotis = true;
bool showButtons = true;
bool showSwitches = true;
bool showPlugs = true;
bool showAdcValues = false;
bool showPinValues = false;
bool showBrightness = false;
bool showMcpConfig = false;
bool scanI2C = false;
bool blink = false;
int delayMs = 0;

void setup() {
  if (!Pixels::init()) {
    setupErrors.push_back("Failed to initialize NeoPixel");
  }
  Serial.setRxBufferSize(1024 * 4);
  Serial.begin(115200);
  Serial.setTxTimeoutMs(0);
  Serial.println("Hello, world!");

  pinMode(BLINK_LED_PIN, OUTPUT);
  digitalWrite(BLINK_LED_PIN, HIGH);

  I2C::init();

  const auto adcError = ADC::init();
  if (adcError) {
    setupErrors.push_back(*adcError);
  }
  if (mcp.begin_I2C(0x20)) {
    for (uint8_t pin = 0; pin < 16; pin++) {
      mcp.pinMode(pin, INPUT_PULLUP);
    }
  } else {
    setupErrors.push_back("Failed to initialize MCP23017");
  }

  Buzzer::init();
  Motor::init();
  Pixels::setColor(0, Color{0, 255, 255});
  Pixels::show();

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
  Pixels::setColor(0, Color{255, 255, 0});
  Pixels::show();
  Logic::start();
  Pixels::setColor(0, Color{255, 0, 255});
  Pixels::show();
}

int loopCount = 1;
void loop() {
  loopCount++;
  Pixels::setColor(0, Color{0,  static_cast<uint8_t>(loopCount), 0});
  Pixels::show();

  if (blink) {
    const bool blinkOn = millis() % 200 < 100;
    digitalWrite(BLINK_LED_PIN, blinkOn ? HIGH : LOW);
  }

  handleSerial();
  const auto adcResults = ADC::readAll();

  currentData.update(adcResults, mcp.readGPIOAB());
  const float brightness = std::clamp(currentData.adcValue(POTI_CONFIG_BRIGHTNESS), MIN_BRIGHTNESS, MAX_BRIGHTNESS);

  if (serialOutput) {
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

    if (showMcpConfig) {
      Serial.print(" D:0x");
      Serial.print(mcp.getPinDirectionMask(), HEX);
      Serial.print(" P:0x");
      Serial.print(mcp.getPinPullupMask(), HEX);
    }

    Serial.println();
  }

  Pixels::setBrightness(brightness);
  Logic::loop(loopCount);

  if (delayMs > 0)
    delay(delayMs);
}

void handleSerial() {
  while (Serial.available()) {
    const auto cmd = Serial.read();
    switch (cmd) {
      case ' ':
        serialOutput = !serialOutput;
        break;
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
      case 'm':
        showMcpConfig = !showMcpConfig;
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
      case 'E': // Echo
      {
        const std::string s = readSerial("\n", "> ", true);
        Serial.print("Received: ");
        Serial.println(s.c_str());
        break;
      }
      case 'S':
      {
        const Song song = readSongFromSerial();

        const auto now = Player::now();
        std::vector<Player> players;
        for (int i = 0; i < song.tracks.size() && i < BUZZER_PINS.size(); ++i) {
          if (song.tracks[i].notes != nullptr) {
            players.emplace_back(song.tracks[i], i, now);
          }
        }
        bool anyPlaying = true;
        while (anyPlaying) {
          if (Serial.available()) {
            Serial.println("Stopping playback.");
            break;
          }
          anyPlaying = false;
          for (auto& player : players) {
            if (!player.isFinished()) {
              player.loop();
              anyPlaying = true;
            }
          }
        }

        for (int i = 0; i < song.tracks.size(); ++i) {
          delete[] song.tracks[i].notes;
        }

        break;
      }
      case '\n':
      case '\r':
        // Ignore
        break;
      default:
        Serial.println("Unknown command: '" + String((char)cmd) + "' (" + String((int)cmd) + ")");
        break;
    }
  }
}

constexpr size_t READ_SERIAL_BUFFER_SIZE = 1024 * 200;
char readSerialBuffer[READ_SERIAL_BUFFER_SIZE];
std::string readSerial(std::string_view endPattern, std::string_view prompt, bool echo) {
  if (prompt.length() > 0) {
    Serial.print(prompt.data());
  }
  std::string buffer;
  size_t index = 0;
  while (true) {
    while (Serial.available()) {
      char c = (char)Serial.read();
      if (echo) {
        Serial.print(c);
      }
      if (index >= READ_SERIAL_BUFFER_SIZE - 1) {
        Serial.println("Read buffer overflow");
        return std::string{readSerialBuffer, index};
      }
      readSerialBuffer[index] = c;
      if (index >= endPattern.length() - 1) {
        bool foundEnd = true;
        for (size_t i = 0; i < endPattern.length(); i++) {
          if (readSerialBuffer[index - i] != endPattern[endPattern.length() - 1 - i]) {
            foundEnd = false;
            break;
          }
        }
        if (foundEnd) {
          return std::string{readSerialBuffer, index + 1 - endPattern.length()};
        }
      }
      index++;
    }
  }
}

template<typename T>
size_t readBinaryFromSerial() {
  T value = 0;
  uint8_t buffer[sizeof(T)];
  while (Serial.available() < sizeof(T)); // Busy wait
  Serial.readBytes(reinterpret_cast<char*>(buffer), sizeof(T));
  memcpy(&value, buffer, sizeof(T));

  return value;
}

Song readSongFromSerial() {
  std::array<Track, 3> tracks;
  for (size_t i = 0; i < tracks.size(); i++) {
    Track track;
    track.length =  readBinaryFromSerial<size_t>();
    Note* notes;
    if (track.length == 0) {
      notes = nullptr;
      continue;
    }
    Serial.println("Reading track " + String(i) + " with " + String(track.length) + " notes.");
    notes = new Note[track.length];
    for (size_t j = 0; j < track.length; j++) {
      notes[j].startUs = readBinaryFromSerial<uint32_t>();
      notes[j].endUs = readBinaryFromSerial<uint32_t>();
      notes[j].pitch = readBinaryFromSerial<uint8_t>();
    }
    track.notes = notes;
    tracks[i] = track;
  }
  char loop = readBinaryFromSerial<char>();
  Serial.println("Reading loop flag: " + String(loop));
  return Song{tracks, loop != 0};
}
