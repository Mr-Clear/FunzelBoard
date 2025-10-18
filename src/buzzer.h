#pragma once

#include <cstdint>

namespace Buzzer {
    void init();
    void tone(uint8_t buzzer, uint32_t hz, float volume = 0.5f);
    void off(uint8_t buzzer);
}  // namespace Buzzer