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
#include <memory>
#include <set>

namespace {
  std::multiset<std::unique_ptr<DelayedAction>, ActionOrder> actions;

  class Carousel : public DelayedAction {
  public:
    Carousel(time_t timestamp, int position = 0) : DelayedAction(timestamp), _position(position) { }
    void run() override {
      Pixels::setColor(_position + 24, WHITE);
      actions.emplace(std::make_unique<Carousel>(timestamp() + 100, (_position + 1) % 16));
    }
  private:
    int _position;
  };

  Octaves octaves;
}

void Logic::start()
{
  actions.emplace(std::make_unique<Carousel>(0));
}

void Logic::loop(int loopCount)
{
  Pixels::clear();

  while (actions.size() && (*actions.begin())->timestamp() <= currentData.now()) {
    auto nextAction = std::move(actions.extract(actions.begin()).value());
    nextAction->run();
  }

  for (uint8_t button = 0; button < BUTTONS_MAP.size(); button++) {
    Pixels::setColor(button, currentData.pin(BUTTONS_MAP[button]) ? WHITE : BLACK);
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

  octaves.run();

  Motor::setSpeed(currentData.adcValue(POTI_MAP[3]));

  Pixels::show();
}
