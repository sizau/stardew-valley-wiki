import math
import time

INT_MIN = -2147483648
INT_MAX = 2147483647
MBIG = INT_MAX
MSEED = 161803398


def to_int32(n):
  n = n & 0xFFFFFFFF
  return n if n < 0x80000000 else n - 0x100000000


class CSRandom:
  def __init__(self, seed=None):
    if seed is None:
      seed = int(time.time() * 1000)

    seed = to_int32(seed)

    self.inext = 0
    self.inextp = 0
    self.SeedArray = [0] * 56

    subtraction = INT_MAX if seed == INT_MIN else abs(seed)
    mj = MSEED - subtraction
    self.SeedArray[55] = mj
    mk = 1
    for i in range(1, 55):
      ii = (21 * i) % 55
      self.SeedArray[ii] = mk
      mk = mj - mk
      if mk < 0:
        mk += MBIG
      mj = self.SeedArray[ii]

    for k in range(1, 5):
      for i in range(1, 56):
        self.SeedArray[i] -= self.SeedArray[1 + (i + 30) % 55]
        if self.SeedArray[i] > INT_MAX:
          self.SeedArray[i] -= 4294967296
        elif self.SeedArray[i] < INT_MIN:
          self.SeedArray[i] += 4294967296

        if self.SeedArray[i] < 0:
          self.SeedArray[i] += MBIG

    self.inext = 0
    self.inextp = 21

  def internal_sample(self):
    locINext = self.inext + 1
    if locINext >= 56:
      locINext = 1

    locINextp = self.inextp + 1
    if locINextp >= 56:
      locINextp = 1

    retVal = self.SeedArray[locINext] - self.SeedArray[locINextp]
    if retVal == MBIG:
      retVal -= 1
    if retVal < 0:
      retVal += MBIG

    self.SeedArray[locINext] = retVal
    self.inext = locINext
    self.inextp = locINextp
    return int(retVal)

  def sample(self):
    return float(self.internal_sample()) * (1.0 / MBIG)

  def get_sample_for_large_range(self):
    result = self.internal_sample()
    if self.internal_sample() % 2 == 0:
      result = -result
    d = float(result)
    d += INT_MAX - 1
    d /= 2 * INT_MAX - 1
    return d

  def next(self, a=None, b=None):
    min_val = 0
    max_val = INT_MAX

    if b is not None:
      max_val = b
      min_val = a if a is not None else 0
      if min_val > max_val:
        raise ValueError(f"Argument out of range - min ({min_val}) should be smaller than max ({max_val})")

      range_val = max_val - min_val
      if range_val <= INT_MAX:
        return math.floor(self.sample() * range_val) + min_val
      else:
        return math.floor(self.get_sample_for_large_range() * range_val) + min_val
    elif a is not None:
      max_val = a
      if max_val < 0:
        raise ValueError(f"Argument out of range - max ({max_val}) must be positive")
      return math.floor(self.sample() * max_val)
    else:
      return self.internal_sample()

  def next_double(self):
    return self.sample()
