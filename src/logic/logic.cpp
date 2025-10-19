#include "logic.h"

#include "actions.h"
#include "data.h"
#include "config.h"
#include "color.h"
#include "motor.h"
#include "octaves.h"
#include "pixels.h"

#include <Arduino.h>

#include <array>
#include <bitset>
#include <list>
#include <map>
#include <memory>

namespace {
  std::multimap<time_t, ScheduledAction> scheduledActions;

  uint16_t carouselPosition = 0;
  uint16_t carouselPixel(uint16_t pos) {
    const uint16_t p = pos < 8 ? pos : 23 - pos;
    return (p + 24) % NUM_PIXELS;
  }

  void carousel(time_t scheduledTime) {
    Pixels::setColor(carouselPixel(carouselPosition), BLACK);
    carouselPosition = (carouselPosition + 1) % 16;
    Pixels::setColor(carouselPixel(carouselPosition), WHITE);
    scheduledActions.emplace(scheduledTime + 100, &carousel);
  }
}

void Logic::start()
{
  scheduledActions.emplace(0, &carousel);
}

void Logic::loop(int loopCount)
{
  while (!scheduledActions.empty() && scheduledActions.begin()->first <= millis()) {
    const auto handle = scheduledActions.extract(scheduledActions.begin());
    handle.mapped()(handle.key());
  }

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
  Pixels::setColor(16, currentData.plug(0) ? BLUE : BLACK);
  Pixels::setColor(17, currentData.plug(1) ? RED : BLACK);
  Pixels::setColor(18, currentData.plug(2) ? YELLOW : BLACK);

  octaves();

  Motor::setSpeed(currentData.adcValue(POTI_MAP[3]));

  Pixels::show();
}
