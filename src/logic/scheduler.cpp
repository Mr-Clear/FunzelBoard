#include "scheduler.h"

#include "data.h"

#include <map>

namespace {
  std::multimap<time_t, Scheduler::ScheduledAction> scheduledActions;
}

void Scheduler::schedule(time_t scheduledTime, ScheduledAction action) {
  scheduledActions.emplace(scheduledTime, action);
}

void Scheduler::run() {
  while (!scheduledActions.empty() && scheduledActions.begin()->first <= currentData.now()) {
    const auto handle = scheduledActions.extract(scheduledActions.begin());
    handle.mapped()(handle.key());
  }
}
