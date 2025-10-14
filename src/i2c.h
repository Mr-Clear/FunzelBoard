#include <vector>

namespace I2C {

constexpr int SPEED = 400000; // 400 kHz
constexpr int SDA = 6;
constexpr int SCL = 7;

void init();
std::vector<char> scan();

} // namespace I2C
