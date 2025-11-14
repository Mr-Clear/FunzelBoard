#include <vector>

namespace I2C {

constexpr int SPEED = 400000; // 400 kHz

void init();
std::vector<char> scan();

} // namespace I2C
