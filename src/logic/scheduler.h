#pragma once

#include <functional>
#include <time.h>

namespace Scheduler {
  using ScheduledAction = std::function<void(time_t scheduledTime)>;
  void schedule(time_t scheduledTime, ScheduledAction action);
  void run();
}
