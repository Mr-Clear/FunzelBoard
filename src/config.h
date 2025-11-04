#pragma once

#include <array>
#include <cstdint>

constexpr uint8_t BLINK_LED_PIN = 5;
constexpr int NUM_PIXELS = 100;
constexpr uint8_t PIXELS_PIN = 10;
constexpr std::array<uint8_t, 3> BUZZER_PINS = {4, 3, 2};
constexpr std::array<uint8_t, 3> BUZZER_TIMERS = {0, 1, 2};
constexpr std::array<uint8_t, 3> BUZZER_CHANNELS = {0, 1, 2};
constexpr int PIXELS_RING_OFFSET = 64;
constexpr int PIXELS_RING_COUNT = 16;
constexpr uint8_t MOTOR_PIN  = 1;
constexpr uint8_t MOTOR_TIMER = 3;
constexpr uint8_t MOTOR_CHANNEL = 3;

constexpr std::array<uint8_t, 8> POTI_MAP = {0, 1, 2, 3, 4, 5, 6, 7};
constexpr uint8_t POTI_REF_LO = POTI_MAP[0];
constexpr uint8_t POTI_REF_HI = POTI_MAP[1];
constexpr uint8_t POTI_CONFIG_BRIGHTNESS = POTI_MAP[2];
constexpr uint8_t POTI_MAIN = POTI_MAP[4];
constexpr uint8_t POTI_R = POTI_MAP[5];
constexpr uint8_t POTI_G = POTI_MAP[6];
constexpr uint8_t POTI_B = POTI_MAP[7];
constexpr std::array<uint8_t, 5> BUTTONS_MAP = {4, 3, 2, 1, 0};
constexpr uint16_t BUTTON_MASK = 0b0000000000011111;
constexpr std::array<uint8_t, 6> SWITCHES2_MAP = {15, 14, 13, 12, 11, 10};
constexpr std::pair<uint8_t, uint8_t> SWITCHES3_MAP = {8, 9};
constexpr std::array<uint8_t, 3> PLUGS_MAP = {7, 6, 5};
