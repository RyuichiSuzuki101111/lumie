// lumie/math/overflow_arithmetic/overflow_arithmetic.hpp - Unified interface
// for overflow traits
#pragma once

#include "fallback.hpp"
#include "forward.hpp"

#if defined(__GNUC__) || defined(__clang__)
#include "gnu.hpp"

namespace lumie::math::overflow_arithmetic {
template <typename T>
  requires std::is_integral_v<T> && std::is_signed_v<T>
using default_overflow_trait = overflow_trait<T, gnu::tag>;
} // namespace lumie::math::overflow_arithmetic

#elif defined(_MSC_VER)
#include "msvc.hpp"

namespace lumie::math::overflow_arithmetic {
template <typename T>
  requires std::same_as<T, std::int16_t> || std::same_as<T, std::int32_t>
using default_overflow_trait = overflow_trait<T, msvc::experimental_tag>;
} // namespace lumie::math::overflow_arithmetic

#else

namespace lumie::math::overflow_arithmetic {
template <typename T>
  requires std::same_as<T, std::int16_t> || std::same_as<T, std::int32_t>
using default_overflow_trait = overflow_trait<T, fallback::tag>;
} // namespace lumie::math::overflow_arithmetic

#endif