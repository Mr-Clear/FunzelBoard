#include "logic.h"

#include "data.h"
#include "config.h"
#include "color.h"
#include "leds.h"
#include "loudness.h"
#include "motor.h"
#include "music.h"
#include "noneState.h"
#include "octaves.h"
#include "panic.h"
#include "pixels.h"

#include <Arduino.h>

#include <array>
#include <bitset>
#include <list>
#include <map>
#include <memory>

namespace {
  enum class Mode {
    NONE,
    OCTAVES,
    MUSIC,
    LOUDNESS,
    PANIC
  };

  Mode lastMode = Mode::NONE;

  std::map<Mode, std::unique_ptr<State>> states;
} // namespace

void Logic::start()
{
  states[Mode::NONE] = std::make_unique<NoneState>();
  states[Mode::OCTAVES] = std::make_unique<OctavesState>();
  states[Mode::PANIC] = std::make_unique<PanicState>();
  states[Mode::MUSIC] = std::make_unique<MusicState>();
  states[Mode::LOUDNESS] = std::make_unique<LoudnessState>();
}

void Logic::loop(int loopCount)
{
  Mode currentMode = Mode::NONE;
  if (currentData.plug(0) + currentData.plug(1) + currentData.plug(2) > 1) {
    currentMode = Mode::PANIC;
  } else if (currentData.plug(0)) {
    currentMode = Mode::OCTAVES;
  } else if (currentData.plug(1)) {
    currentMode = Mode::MUSIC;
  } else if (currentData.plug(2)) {
    currentMode = Mode::LOUDNESS;
  }

  if (currentMode != Mode::PANIC) {
    leds();
  }

  if (currentMode != lastMode) {
    states[lastMode]->exit();
    lastMode = currentMode;
    states[currentMode]->enter();
  }
  states[currentMode]->update();

  Pixels::show();
}
