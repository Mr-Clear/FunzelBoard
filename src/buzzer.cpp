#include "buzzer.h"

#include "config.h"

#include <driver/ledc.h>

namespace {
    constexpr uint8_t BUZZER_RES_BITS = 10;
    constexpr uint32_t BUZZER_MAX_DUTY = (1u << BUZZER_RES_BITS) - 1;
}  // namespace

void Buzzer::init() {
      for (int i = 0; i < 2; ++i) {
    ledc_timer_config_t timer_cfg = {
      .speed_mode       = LEDC_LOW_SPEED_MODE,
      .duty_resolution  = static_cast<ledc_timer_bit_t>(BUZZER_RES_BITS),
      .timer_num        = static_cast<ledc_timer_t>(i),
      .freq_hz          = 1000 + i * 1000,
      .clk_cfg          = LEDC_AUTO_CLK
    };
    ledc_timer_config(&timer_cfg);

    ledc_channel_config_t chan_cfg = {
      .gpio_num   = BUZZER_PINS[i],
      .speed_mode = LEDC_LOW_SPEED_MODE,
      .channel    = static_cast<ledc_channel_t>(i),
      .intr_type  = LEDC_INTR_DISABLE,
      .timer_sel  = static_cast<ledc_timer_t>(i),
      .duty       = 0,
      .hpoint     = 0,
      .flags      = { .output_invert = 0 }
    };
    ledc_channel_config(&chan_cfg);
  }
}

void Buzzer::tone(uint8_t buzzer, uint32_t hz, float volume) {
  if (buzzer >= BUZZER_PINS.size() || hz == 0)
    return;
  const uint32_t duty = BUZZER_MAX_DUTY / 2;
  ledc_set_freq(LEDC_LOW_SPEED_MODE, static_cast<ledc_timer_t>(buzzer), hz);
  ledc_set_duty(LEDC_LOW_SPEED_MODE, static_cast<ledc_channel_t>(buzzer), duty);
  ledc_update_duty(LEDC_LOW_SPEED_MODE, static_cast<ledc_channel_t>(buzzer));
}

void Buzzer::off(uint8_t buzzer) {
  if (buzzer >= BUZZER_PINS.size())
    return;
  ledc_set_duty(LEDC_LOW_SPEED_MODE, static_cast<ledc_channel_t>(buzzer), 0);
  ledc_update_duty(LEDC_LOW_SPEED_MODE, static_cast<ledc_channel_t>(buzzer));
}