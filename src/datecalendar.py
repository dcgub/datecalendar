"""
This module implements the core concepts of the
DateCalendar.sol smart contract.

Dates in the calendar are as of 00:00 UT (Universal Time).
The date token index is the unique identifier used to keep 
track of the date tokens in the smart contract and 
represents the relative positioning of all possible dates 
in the calendar.

Date token index 

0                                 2**256 -1
|---------------------------------|

Since the difference between two date token indices
represents the number of times an entire day has passed
in UT, all potential dates in the calendar span over
Vigintillion years (>> 10**63). For context, the
age of the universe is assumed to be roughly
14 billion years (14*10**9).

Astronomers use a similar concept for calculating
the elapsed days between two events: a Julian day number (JDN).
The JDN for a given day is an integer describing the number of solar days
between the given day and a fixed day in history starting
from 12:00 UT (noon). This fixed day in history is referred to
as the Julian epoch and it has a JDN value of 0.

The Julian date (JD) of any instant is the JDN plus
the fraction of a day since the preceding 12:00 UT.
Since all dates in DateCalendar are as of 00:00 UT,
then their corresponding JDs will have a fixed
day fraction of +0.5.

DateCalendar links date token indices to JDs
by setting the midpoint of the index to the
JD of -0.5 (JDN of -1 and day fraction of 0.5).

Date token index 

0                2**255            2**256-1
|----------------|-----------------|

JD=(JDN, day fraction)

(-2**255, 0.5 )  (-1, 0.5)         (2**255, 0.5)
|----------------|-----------------|

When a token is minted, the DateCalendar
smart contract simultaneously assigns
a date string to the date token index
as a verifiable proof of the date that is owned by
a token holder. This date string represents a date 
in the Greogrian calendar, which is the calendar
in common use today. The date string is formatted
in the following way:

{Day of Week} {Day of Month} {Month} {Year} {Era}

For example, the JD of -0.5 has a Gregorian
calendar date string of Monday 1 January 4713 BCE.

Calendars in popular use have changed throughout 
history and are likely to continue changing.
The Gregorian calendar was first introduced
on Friday 15 October 1582 CE as a modification to
the Julian calendar in order to remove the "drift"
in the solar year. These 2 calendar systems can have
different dates for a given JD. For example,
the day before the Gregorian calendar was implemented
was Thursday 4 October 1582 CE in the Julian calendar.

In the DateCalendar, all historical dates,
even those prior to the invention of the Gregorian 
calendar, will be represented as a date in the
Gregorian calendar, formally known as a proleptic
calendar. Some historians report events using the
common calendar at the time, meaning users should
take special care in converting those dates to the
equivalent Gregorian calendar dates or JDs in
order to determine the correct date tokens to mint.

This module contains various utilities
to convert to and from the various date
representations: date token index, Julian Date, 
Julian calendar date, Gregorian calendar date.
"""
from typing import Any, Tuple

def get_int_bounds(type_str: str) -> Tuple[int, int]:
    """
    Returns the lower and upper bound for an integer type.

    References
    ----------
    [1] https://pypi.org/project/eth-brownie/ `brownie.convert.utils`
    """
    size = int(type_str.strip("uint") or 256)
    if size < 8 or size > 256 or size % 8:
        raise ValueError(f"Invalid type: {type_str}")

    if type_str.startswith("u"):
        return 0, 2 ** size - 1

    return -(2 ** (size - 1)), 2 ** (size - 1) - 1


class AbstractSolidityInt(int):

    def __new__(cls, value: Any) -> int:
        dti = super().__new__(cls, value)
        lower, upper = get_int_bounds(cls.SOLIDITY_TYPE)
        if dti < lower or dti > upper:
            raise OverflowError(f"{value} is outside allowable range for DateTokenIndex")

        return dti

class uint16(AbstractSolidityInt):
    SOLIDITY_TYPE = 'uint16'

class uint256(AbstractSolidityInt):
    SOLIDITY_TYPE = 'uint256'

class int256(AbstractSolidityInt):
    SOLIDITY_TYPE = 'int256'

class DateTokenIndex(uint256):
    """
    The date token index is the unique identifier used to keep 
    track of the date tokens in the smart contract and 
    represents the relative positioning of all possible dates 
    in the calendar.
    """
    pass

class JulianDate(namedtuple('JulianDate', ['julian_day_number' ,'day_fraction'])):
    """
    A Julian Date (JD) is composed
    of two pieces, the Julian Day Number (JDN)
    and day fraction.

    Attributes
    ----------
    julian_day_number: :obj:`int256`
        Integer describing the number of solar days
        between the given day and a fixed day in history starting
        from 12:00 UT (noon)
    day_fraction: :obj:`uint16`
        Integer describing the value the day faction.
        Since the day fraction is between 0 and 1,
        `day_fracion` should be interpreted as the
        number after the decimal point. I.e.
        5 means 0.5. 51 mean 0.51

    """

    @classmethod
    def from_dti(self, dti: DateTokenIndex):
        pass
    
    def to_float(self):
        """
        Convert the JD to a floating
        point. This will run into floating point
        representation issues for large
        `julian_day_number` values.
        """
        jdn = self.julian_day_number
        df = self.day_fraction

        num_digits = len(str(df))
        df /= (10 ** num_digits)

        return jdn + df


from collections import namedtuple
import math

INT256_MAX = 2**255 - 1

# Furthest number of days we can
# lookback in time
MAX_LOOKBACK = INT256_MAX

# This DCI is the index of
# '4713-01-01 BCE JCal' @00:00 UT.
# This index is the starting point
# for Julian Calendar Dates. Prior
# to this, dates are presented as Julian Dates.
# '4713-01-01 BCE JCal' @12:00 UT (noon) has
# a Julian Date equal to 0.0.
JCAL_START_DCI = MAX_LOOKBACK

class JulianDate(namedtuple('JulianDate', 'jdn day_fraction')):
    # The amount to subtract from a Julian Date
    # to aconvert it from 12:00 UT to 00:00 UT.
    HALF_DAY = 0.5

def dci_to_jd(dci):
    return JulianDate(dci - JCAL_START_DCI, -JulianDate.HALF_DAY)

def jd_to_dci(jd):
    return jd.jdn + JCAL_START_DCI

TO_JD_HELPER = tuple([
    306, 337, 0, 31, 
    61, 92, 122, 153, 
    184, 214, 245, 275
])

def gcal_to_jd(y, m, d):
    if m < 3:
        z = y - 1
    else:
        z = y
    f = TO_JD_HELPER[m-1]
    p1 = math.floor(z / 4)
    p2 = math.floor(z / 100)
    p3 = math.floor(z / 400)
    jdn = d + f + 365 * z + p1 - p2 + p3 + 1721119
    return JulianDate(jdn, -JulianDate.HALF_DAY)

def gcal_to_jd(Y,M,D):
    """Gregorian to Julian Day Number Calculation"""
    if M<3:
        M+=12
        Y-=1
    return(D + int((153 * M - 457) / 5) + 365 * Y + Y // 4 - Y // 100 + Y // 400 + 1721118.5)

TO_GCAL_HELPER = tuple([
    0, 31, 61, 92, 
    122, 153, 184, 214, 
    245, 275, 306, 337
])

def jd_to_gcal(jd):
    z = jd.jdn - 1721119
    r =  0
    k1 = k2 = 25
    a = (z*100 - k1) // 3652425
    y = (z*100 - k2 + a*100 - a // 4 * 100) // 36525
    c = z + a - a // 4 - (36525 * y) // 100
    m = int((5 * c +456) / 153)
    f = TO_GCAL_HELPER[m-3]
    d = c - f + r
    if m > 12:
        y += 1
        m -= 12
    return y, m, d


def jd_to_gcal(jd):
    JDN = jd.jdn + jd.day_fraction
    """Julian Day Number to Gregorian Date"""
    T=JDN - 1721118.5
    Z = T//1
    R = T - Z
    G = Z - .25
    A = G // 36524.25
    B = A - A // 4
    year = int((B+G) // 365.25)
    C = B + Z - (365.25 * year)//1
    month = int((5 * C + 456) / 153)
    day = C - int((153 * month - 457) // 5) + R
    if month > 12:
        year+=1
        month-=12
    return year, month, day

