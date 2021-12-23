"""
This module implements the core concepts of the
DateCalendar.sol smart contract.

Dates in the calendar are as of 00:00 UT (Universal Time).
The Date Token Index (DTI) is the unique identifier used to keep 
track of the date tokens in the smart contract and 
represents the relative positioning of all possible dates 
in the calendar.

DTI

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
JD of 0.5 (JDN of 0 and day fraction of 0.5).

DTI 

0                2**255            2**256-1
|----------------|-----------------|

JD=(JDN, day fraction)

(-2**255, 0.5 )  (0, 0.5)         (2**255-1, 0.5)
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
Many of these utilities were created using the
algorithmns outlined and developed by Peter Baum.
"""
from __future__ import annotations

from collections import namedtuple
from typing import Any, Tuple
import datetime

from dateutil.parser import parse as parse_dt_string

class SolidityInt(int):

    SOLIDITY_TYPE = 'int'

    def __new__(cls, value: Any) -> int:
        inst = super().__new__(cls, value)
        lower, upper = cls.get_int_bounds()
        if inst < lower or inst > upper:
            raise OverflowError(f"{value} is outside allowable range for {cls.SOLIDITY_TYPE}")

        return inst

    @classmethod
    def get_int_bounds(cls) -> Tuple[int, int]:
        """
        Returns the lower and upper bound for an integer type.

        References
        ----------
        [1] https://pypi.org/project/eth-brownie/ `brownie.convert.utils`
        """
        type_str = cls.SOLIDITY_TYPE
        size = int(type_str.strip('uint') or 256)
        if size < 8 or size > 256 or size % 8:
            raise ValueError(f'Invalid type: {type_str}')

        if type_str.startswith('u'):
            return 0, 2 ** size - 1

        return -(2 ** (size - 1)), 2 ** (size - 1) - 1

    @classmethod
    def get_midpoint_value(cls) -> int:
        """
        Retrieve the value of this type that sits
        at the midpoint between the upper
        and lower integer bounds. If there is
        a tie, the value returned is to the right
        of the midpoint.
        """
        lower, upper = cls.get_int_bounds()
        return ((upper - lower) + 1) // 2 + lower

class uint8(SolidityInt):
    SOLIDITY_TYPE = 'uint8'

class uint16(SolidityInt):
    SOLIDITY_TYPE = 'uint16'

class uint256(SolidityInt):
    SOLIDITY_TYPE = 'uint256'

class int256(SolidityInt):
    SOLIDITY_TYPE = 'int256'

class DateTokenIndex(uint256):
    """
    The date token index is the unique identifier used to keep 
    track of the date tokens in the smart contract and 
    represents the relative positioning of all possible dates 
    in the calendar.
    """
    # Store at class level to avoid recalculating
    MIDPOINT = uint256.get_midpoint_value()

    @classmethod
    def from_jd(cls, jd: JulianDate) -> DateTokenIndex:
        """
        Create a Date Token Index from a Julian date.

        The `day_fraction` of the Julian date will be
        ignored.
        """
        dti_mid = cls.MIDPOINT
        return DateTokenIndex(jd.jdn + dti_mid)

    def to_jd(self) -> JulianDate:
        """
        Convert a DTI to a Julian date.
        """
        return JulianDate.from_dti(self)


_JulianDate = namedtuple('JulianDate', ['jdn' ,'day_fraction'])

class JulianDate(_JulianDate):
    """
    A Julian Date (JD) is composed
    of two pieces, the Julian Day Number (JDN)
    and day fraction.

    Attributes
    ----------
    jdn: :obj:`int256`
        Julian Day Number. Integer describing the number of solar days
        between the given day and a fixed day in history starting
        from 12:00 UT (noon).
    day_fraction: :obj:`uint16`
        Integer describing the value the day faction.
        Since the day fraction is between 0 and 1,
        `day_fracion` should be interpreted as the
        number after the decimal point. I.e.
        5 means 0.5. 51 mean 0.51.

    """

    def __new__(cls, jdn: int256, day_fraction: uint16):
        return super(JulianDate, cls).__new__(cls, 
                                              jdn=int256(jdn), 
                                              day_fraction=uint16(day_fraction))

    @classmethod
    def from_dti(cls, dti: DateTokenIndex) -> JulianDate:
        """
        Create a Julian date from a Date Token Index.
        """
        dti_mid = DateTokenIndex.MIDPOINT
        return JulianDate(jdn=dti - dti_mid,
                          day_fraction=5)

    
    def to_dti(self) -> DateTokenIndex:
        """
        Convert the JD to a Date Token Index.
        """
        return DateTokenIndex.from_jd(self)
    
    def to_float(self) -> float:
        """
        Convert the JD to a floating
        point. This will run into floating point
        representation issues for large
        `jdn` values.
        """
        jdn = self.jdn
        df = self.day_fraction

        num_digits = len(str(df))
        df /= (10 ** num_digits)

        return jdn + df

    def to_gcal_date(self) -> GCalDate:
        return GCalDate.from_jd(self)

    def to_jcal_date(self) -> GCalDate:
        return JCalDate.from_jd(self)


_CalendarDate = namedtuple('CalendarDate', ['day_of_week' ,'day',
                                            'month', 'year'])

class CalendarDate(_CalendarDate):
    """
    Representation of a date in
    a modern calendar.

    Attributes
    ----------
    day_of_week: :obj:`uint8`
        Integer from 0 to 6 indicating
        the day of the week, with 0 being Sunday,
        1 being Monday, etc.
    day: :obj:`uint8`
        Integer from 1 to 31 indicating the
        day of the month.
    month: :obj:`uint8`
        Integer from 1 to 12 indicating the
        month of the year.
    year: :obj:`int256`
        Signed integer for the year. The year
        before 1 is 0, and the year before 0 is -1, etc.
        A year of 1 is 1 CE, a year of 0 is 1 BCE, 
        a year of -1 is 2 BCE, etc.
    """

    DAYS_OF_WEEK = (
        'Sunday',
        'Monday', 'Tuesday', 'Wednesday',
        'Thursday', 'Friday', 'Saturday', 
    )

    MONTHS = (
        'January', 'February', 'March',
        'April', 'May', 'June',
        'July', 'August', 'September',
        'October', 'November', 'December'
    )

    def __new__(cls, day_of_week: uint8, day: uint8,
                month: uint8, year: int256):
        return super(CalendarDate, cls).__new__(cls, 
                                                day_of_week=uint8(day_of_week), 
                                                day=uint8(day),
                                                month=uint8(month),
                                                year=int256(year))

    def __str__(self):
        dow = self.DAYS_OF_WEEK[self.day_of_week]
        d = self.day
        m = self.MONTHS[self.month - 1]
        y = self.year
        era = ''
        if y <= 0:
            era = 'BCE'
            y = -y + 1
        else:
            era = 'CE'
        return f'{dow} {d} {m} {y} {era}'

    def __repr__(self):
        return self.__str__()

    @classmethod
    def from_string(cls, value: str) -> CalendarDate:
        """
        Create a calendar date from a string.
        """
        dt = parse_dt_string(value)
        return cls.from_datetime(dt)

    @classmethod
    def from_datetime(cls, dt: datetime.datetime) -> CalendarDate:
        """
        Create a calendar date from a Python datetime.
        """
        _cd = cls(day_of_week=0, #dummy placeholder
                  day=dt.day,
                  month=dt.month,
                  year=dt.year)
        dow = cls.day_of_week_from_jd(_cd.to_jd())
        return cls(day_of_week=dow,
                   day=dt.day,
                   month=dt.month,
                   year=dt.year)

class GCalDate(CalendarDate):

    _FROM_JD_HELPER = (
        0, 31, 61, 92, 
        122, 153, 184, 214, 
        245, 275, 306, 337
    )

    _TO_JD_HELPER = (
        306, 337, 0, 31, 
        61, 92, 122, 153, 
        184, 214, 245, 275
    )

    @classmethod
    def from_jd(cls, jd: JulianDate) -> GCalDate:
        """
        Create a Gregorian calendar date
        from a Julian Date.

        References
        ----------
        [1] P. Baum, "Date Algorithms", 2020.
        """
        z = jd.jdn - 1721118
        k = 25
        a = (z*100 - k) // 3652425
        y = (z*100 - k + a*100 - a // 4 * 100) // 36525
        c = z + a - a // 4 - (36525 * y) // 100
        m = int((5 * c +456) / 153)
        f = cls._FROM_JD_HELPER[m-3]
        d = c - f 
        if m > 12:
            y += 1
            m -= 12
        dow = cls.day_of_week_from_jd(jd)
        return cls(day_of_week=dow,
                   day=d,
                   month=m,
                   year=y)

    @classmethod
    def day_of_week_from_jd(cls, jd: JulianDate) -> uint8:
        """
        Calculate the day of week for a given
        JD.

        References
        ----------
        [1] P. Baum, "Date Algorithms", 2020.
        [2] J. Meeus, "Astronomical Algorithms", pp. 65, 1998.        
        """
        return int((jd.jdn + 2) % 7)


    def to_jd(self) -> JulianDate:
        """
        Convert the Gregorian calendar date
        to a Julian Date.

        References
        ----------
        [1] P. Baum, "Date Algorithms", 2020.
        """
        d = self.day
        m = self.month
        y = self.year
        if m < 3:
            z = y - 1
        else:
            z = y
        f = self._TO_JD_HELPER[m-1]
        p1 = z // 4
        p2 = z // 100
        p3 = z // 400
        jdn = d + f + 365 * z + p1 - p2 + p3 + 1721118
        return JulianDate(jdn=jdn,
                          day_fraction=5)

    @property
    def leap_year(self) -> bool:
        """
        Flag indicating whether the year
        is a leap year for the Gregorian calendar
        date.
        """
        # Divisible by 4 and,
        # either not divisible by 100 or divisible by 400.
        a = self.year % 4
        b = self.year % 100
        c = self.year % 400
        return not a and (b or not c)

class JCalDate(CalendarDate):

    @classmethod
    def from_jd(cls, jd: JulianDate) -> JCalDate:
        """
        Create a Julian calendar date
        from a Julian Date.

        References
        ----------
        [1] P. Baum, "Date Algorithms", 2020.
        """
        z = jd.jdn - 1721116
        k = 25
        a = (z*100 - k) // 3652425
        y = (z*100 - k) // 36525
        c = z - (36525 * y) // 100
        m = int((5 * c +456) / 153)
        f = GCalDate._FROM_JD_HELPER[m-3]
        d = c - f 
        if m > 12:
            y += 1
            m -= 12
        dow = cls.day_of_week_from_jd(jd)
        return cls(day_of_week=dow,
                   day=d,
                   month=m,
                   year=y)

    @classmethod
    def day_of_week_from_jd(cls, jd: JulianDate) -> uint8:
        """
        Calculate the day of week for a given
        JD.

        References
        ----------
        [1] P. Baum, "Date Algorithms", 2020.
        [2] J. Meeus, "Astronomical Algorithms", pp. 65, 1998.        
        """
        return GCalDate.day_of_week_from_jd(jd)

    def to_jd(self) -> JulianDate:
        """
        Convert the Julian calendar date
        to a Julian Date.

        References
        ----------
        [1] P. Baum, "Date Algorithms", 2020.
        """
        d = self.day
        m = self.month
        y = self.year
        if m < 3:
            z = y - 1
        else:
            z = y
        f = GCalDate._TO_JD_HELPER[m-1]
        p1 = z // 4
        p2 = z // 100
        p3 = z // 400
        jdn = d + f + 365 * z + p1 + 1721116
        return JulianDate(jdn=jdn,
                          day_fraction=5)

    @property
    def leap_year(self) -> bool:
        """
        Flag indicating whether the year
        is a leap year for the Gregorian calendar
        date.
        """
        # Divisible by 4
        a = self.year % 4
        return not a

