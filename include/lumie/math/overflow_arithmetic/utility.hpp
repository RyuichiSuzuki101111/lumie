// lumie/math/overflow_arithmetic/utility.hpp - Utility functions for overflow
// arithmetic
#pragma once

#include <numeric> // for std::gcd

#include "forward.hpp"

namespace lumie::math::overflow_arithmetic {

template <typename Trait, typename T>
  requires OverflowTrait<Trait, T> &&
           (std::same_as<T, std::int16_t> || std::same_as<T, std::int32_t>)
struct lcm_overflow {
  [[nodiscard("overflow result must be checked")]]
  static bool compute(T a, T b, T &result) {
    // Returns true if overflow occurred.
    assert(a > 0 && b > 0); // precondition

    T gcd = std::gcd(a, b);
    return Trait::mul_overflow(a / gcd, b, &result);
  }
};

} // namespace lumie::math::overflow_arithmetic