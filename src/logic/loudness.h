#pragma once

#include "state.h"

class LoudnessState : public State {
public:
  void enter() override;
  void update() override;
  void exit() override;
};
