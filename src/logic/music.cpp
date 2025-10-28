#include "music.h"

#include "config.h"
#include "music/musicPlayer.h"
#include "music/songs/testSong.h"
#include "music/songs/dukeNukem.h"
#include "music/songs/tetrisB.h"
#include "pixels.h"

#include <array>
#include <cmath>
#include <ctime>
#include <cctype>
#include <cstring>
#include <memory>

namespace {
  std::array<std::unique_ptr<Player>, BUZZER_PINS.size()> players;

  void play(const Song& song) {
    const auto now = Player::now();
    for(int i = 0; i < BUZZER_PINS.size() && i < song.tracks.size(); ++i) {
      players[i] = std::make_unique<Player>(song.tracks[i], i, now);
    }
  }
} // namespace

void MusicState::enter() {
  play(Songs::tetrisB);
}

void MusicState::update() {
  for(auto &player : players) {
    if(player) {
      player->loop();
    }
  }
}

void MusicState::exit() {
  for(auto &player : players) {
    player.reset();
  }
  for (int i = 0; i < BUZZER_PINS.size(); ++i) {
    Buzzer::off(i);
  }
  Pixels::clear();
}
