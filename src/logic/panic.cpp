#include "panic.h"

#include "buzzer.h"
#include "color.h"
#include "config.h"
#include "data.h"
#include "motor.h"
#include "pixels.h"

void PanicState::enter() {
}

void PanicState::update() {
  const bool c = (currentData.now() / 313) % 2;
  const bool b = (currentData.now() / 427) % 2;
  const std::array<bool, 2> m = {(currentData.now() / 220) % 2 == 0, ((currentData.now() + 60) / 220) % 2 == 0};

  const Color color = c ? RED : BLACK;
  for (int i = 0; i < NUM_PIXELS; i++) {
    Pixels::setColor(i, color);
  }
  if (!c) {
    Pixels::setColor(16, currentData.plug(0) ? BLUE : color);
    Pixels::setColor(17, currentData.plug(1) ? GREEN : color);
    Pixels::setColor(18, currentData.plug(2) ? YELLOW : color);
  }

  const int rotation = (currentData.now() / 55) % PIXELS_RING_COUNT;
  for (int i = 0; i < PIXELS_RING_COUNT; i++) {
    const Color ringColor = (i < PIXELS_RING_COUNT / 2) ? (c ? RED : BLUE) : BLACK;
    Pixels::setColor(PIXELS_RING_OFFSET + (i + rotation) % PIXELS_RING_COUNT, ringColor);
  }

  for (int i = 0; i < MOTOR_PINS.size(); i++) {
    Motor::setSpeed(i, m[i] ? 1.0f : 0.0f);
  }

  for (int i = 0; i < BUZZER_PINS.size(); i++) {
    float f = 1 + i / 10.f;
    Buzzer::tone(i, b ? 1700 * f : 2100 * f);
  }
}

void PanicState::exit() {
  Motor::stop();
  Pixels::clear();
  Buzzer::off(0);
  Buzzer::off(1);
  Buzzer::off(2);
}
