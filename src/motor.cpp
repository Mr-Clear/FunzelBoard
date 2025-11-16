#include "motor.h"

#include "config.h"

#include <driver/ledc.h>

#include <algorithm>
#include <cmath>

void Motor::init() {
  ledc_timer_config_t timer_cfg = {
      .speed_mode       = LEDC_LOW_SPEED_MODE,
      .duty_resolution  = LEDC_TIMER_8_BIT,
      .timer_num        = static_cast<ledc_timer_t>(MOTOR_TIMER),
      .freq_hz          = 25000,
      .clk_cfg          = LEDC_AUTO_CLK
  };
  ledc_timer_config(&timer_cfg);

  for (size_t i = 0; i < MOTOR_PINS.size(); ++i) {
    uint8_t pin = MOTOR_PINS[i];
    uint8_t channel = MOTOR_CHANNELS[i];
    ledc_channel_config_t chan_cfg = {
        .gpio_num   = pin,
        .speed_mode = LEDC_LOW_SPEED_MODE,
        .channel    = static_cast<ledc_channel_t>(channel),
        .intr_type  = LEDC_INTR_DISABLE,
        .timer_sel  = static_cast<ledc_timer_t>(MOTOR_TIMER),
        .duty       = 0,
        .hpoint     = 0,
        .flags      = { .output_invert = 0 }
    };
    ledc_channel_config(&chan_cfg);
  }
}

void Motor::setSpeed(int channel, float speed) {
    speed = std::clamp(speed, 0.0f, 1.0f);
    uint32_t duty = static_cast<uint32_t>(std::round(speed * 255.0f));
    ledc_set_duty(LEDC_LOW_SPEED_MODE, static_cast<ledc_channel_t>(MOTOR_CHANNELS[channel]), duty);
    ledc_update_duty(LEDC_LOW_SPEED_MODE, static_cast<ledc_channel_t>(MOTOR_CHANNELS[channel]));
}

void Motor::stop() {
    for (uint8_t channel = 0; channel < MOTOR_CHANNELS.size(); ++channel) {
        setSpeed(channel, 0.0f);
    }
}
