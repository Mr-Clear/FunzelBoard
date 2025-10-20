#pragma once

#include "state.h"

class NoneState : public State {
public:
  void enter() override;
  void update() override;
  void exit() override;
};
