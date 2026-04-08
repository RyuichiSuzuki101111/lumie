// lumie/math/overflow_arithmetic/overflow_arithmetic.hpp - Unified interface
// for overflow traits
#pragma once

#include "forward.hpp"

#if defined(__GNUC__) || defined(__clang__)
#include "gnu.hpp"
#endif

#if defined(_MSC_VER)
#include "msvc.hpp"
#endif

#include "fallback.hpp"
