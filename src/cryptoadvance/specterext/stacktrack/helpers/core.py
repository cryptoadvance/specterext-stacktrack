from enum import Enum


SATS_PER_BTC = 100_000_000


class Interval(Enum):
    HOUR = 1
    DAY = 2
    MONTH = 3
