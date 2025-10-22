#include "leds.h"

#include "color.h"
#include "config.h"
#include "data.h"
#include "pixels.h"

#include <Arduino.h>

void leds() {
  for (uint8_t button = 0; button < BUTTONS_MAP.size(); button++) {
    Pixels::setColor(button + 3, currentData.pin(BUTTONS_MAP[button]) ? WHITE : BLACK);
  }
  for (uint8_t swtch = 0; swtch < SWITCHES2_MAP.size(); swtch++) {
    Pixels::setColor(swtch + 8, currentData.pin(SWITCHES2_MAP[swtch]) ? WHITE : BLACK);
  }
  Pixels::setColor(14, currentData.switch3() > 0
                            ? RED
                            : (currentData.switch3() < 0
                                  ? GREEN
                                  : BLACK));

  Pixels::setColor(32, RED * currentData.adcValue(POTI_R));
  Pixels::setColor(33, GREEN * currentData.adcValue(POTI_G));
  Pixels::setColor(34, BLUE * currentData.adcValue(POTI_B));
  const Color c = Color{static_cast<uint8_t>(255.f * currentData.adcValue(POTI_R)),
                        static_cast<uint8_t>(255.f * currentData.adcValue(POTI_G)),
                        static_cast<uint8_t>(255.f * currentData.adcValue(POTI_B))};
  for(int i = 24; i <= 26; i++) {
    Pixels::setColor(i, c);
  }

  Pixels::setColor(16, currentData.plug(0) ? BLUE : BLACK);
  Pixels::setColor(17, currentData.plug(1) ? GREEN : BLACK);
  Pixels::setColor(18, currentData.plug(2) ? YELLOW : BLACK);
}
