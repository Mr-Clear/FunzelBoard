#include "buzzer.h"

#include "config.h"

#include <driver/ledc.h>

#include <cmath>

namespace {
  constexpr uint8_t BUZZER_RES_BITS = 13;
  constexpr uint32_t BUZZER_MAX_DUTY = (1u << BUZZER_RES_BITS) - 1;
  constexpr uint32_t BUZZER_DUTY = BUZZER_MAX_DUTY / 2;
  std::array<uint32_t, 2> currentFrequencies = {0, 0};
}  // namespace

void Buzzer::init() {
  for (int i = 0; i < BUZZER_TIMERS.size(); ++i) {
    ledc_timer_config_t timer_cfg = {
      .speed_mode       = LEDC_LOW_SPEED_MODE,
      .duty_resolution  = static_cast<ledc_timer_bit_t>(BUZZER_RES_BITS),
      .timer_num        = static_cast<ledc_timer_t>(BUZZER_TIMERS[i]),
      .freq_hz          = static_cast<uint32_t>(1000 + i * 1000),
      .clk_cfg          = LEDC_AUTO_CLK
    };
    ledc_timer_config(&timer_cfg);

    ledc_channel_config_t chan_cfg = {
      .gpio_num   = BUZZER_PINS[i],
      .speed_mode = LEDC_LOW_SPEED_MODE,
      .channel    = static_cast<ledc_channel_t>(BUZZER_CHANNELS[i]),
      .intr_type  = LEDC_INTR_DISABLE,
      .timer_sel  = static_cast<ledc_timer_t>(BUZZER_TIMERS[i]),
      .duty       = 0,
      .hpoint     = 0,
      .flags      = { .output_invert = 0 }
    };
    ledc_channel_config(&chan_cfg);
  }
}

void Buzzer::tone(uint8_t buzzer, float hz) {
  if (hz <= 0.0f) {
    off(buzzer);
    return;
  }
  if (buzzer >= BUZZER_PINS.size())
    return;
  const uint32_t freq = static_cast<uint32_t>(std::round(hz));
  if (currentFrequencies[buzzer] == freq)
    return;
  currentFrequencies[buzzer] = freq;
  ledc_set_freq(LEDC_LOW_SPEED_MODE, static_cast<ledc_timer_t>(buzzer), freq);
  ledc_set_duty(LEDC_LOW_SPEED_MODE, static_cast<ledc_channel_t>(buzzer), BUZZER_DUTY);
  ledc_update_duty(LEDC_LOW_SPEED_MODE, static_cast<ledc_channel_t>(buzzer));
}

void Buzzer::off(uint8_t buzzer) {
  if (buzzer >= BUZZER_PINS.size())
    return;
  currentFrequencies[buzzer] = 0;
  ledc_set_duty(LEDC_LOW_SPEED_MODE, static_cast<ledc_channel_t>(buzzer), 0);
  ledc_update_duty(LEDC_LOW_SPEED_MODE, static_cast<ledc_channel_t>(buzzer));
}