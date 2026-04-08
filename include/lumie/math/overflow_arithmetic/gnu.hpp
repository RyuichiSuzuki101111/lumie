// lumie/math/overflow_arithmetic/gnu.hpp - GNU/Clang-specific overflow traits
#pragma once

#include <type_traits>

#include "forward.hpp"

namespace lumie::math::overflow_arithmetic {

// GNU/Clang-specific specialization using compiler builtins for checked
// arithmetic.

template <typename T>
  requires std::is_integral_v<T> && std::is_signed_v<T>
struct overflow_trait<T, gnu::tag> {
  [[nodiscard("overflow result must be checked")]]
  static bool add_overflow(T a, T b, T *result) {
    return __builtin_add_overflow(a, b, result);
  }
  [[nodiscard("overflow result must be checked")]]
  static bool sub_overflow(T a, T b, T *result) {
    return __builtin_sub_overflow(a, b, result);
  }
  [[nodiscard("overflow result must be checked")]]
  static bool mul_overflow(T a, T b, T *result) {
    return __builtin_mul_overflow(a, b, result);
  }
};

static_assert(
    OverflowTrait<overflow_trait<std::int16_t, gnu::tag>, std::int16_t>);
static_assert(
    OverflowTrait<overflow_trait<std::int32_t, gnu::tag>, std::int32_t>);

} // namespace lumie::math::overflow_arithmetic