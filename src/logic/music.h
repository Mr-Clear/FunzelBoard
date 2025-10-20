#pragma once

#include "state.h"

class MusicState : public State {
public:
  void enter() override;
  void update() override;
  void exit() override;
};
