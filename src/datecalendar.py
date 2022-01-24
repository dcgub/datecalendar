from __future__ import annotations

from dateutil.parser import parse as parse_dt_string

from collections import namedtuple
from typing import Any, Tuple
import datetime
import math

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
    MIDPOINT = 20*10**9*365.25

    @classmethod
    def get_int_bounds(cls) -> Tuple[int, int]:
        return (0, 40*10**9*365.25)

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


class JDN(int256):

    @classmethod
    def get_int_bounds(cls) -> Tuple[int, int]:
        return (-20*10**9*365.25, 20*10**9*365.25)    


_JulianDate = namedtuple('JulianDate', ['jdn' ,'day_fraction'])

class JulianDate(_JulianDate):
    """
    A Julian Date (JD) is composed
    of two pieces, the Julian Day Number (JDN)
    and day fraction.

    Attributes
    ----------
    jdn: :obj:`JDN`
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

    def __new__(cls, jdn: JDN, day_fraction: uint16):
        return super(JulianDate, cls).__new__(cls, 
                                              jdn=JDN(jdn), 
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

class ComparableMixin:
    """
    Mixin for only needing to implement
    `__lt__` to get the entire comparison
    suite.

    Source: https://stackoverflow.com/questions/1061283/lt-instead-of-cmp
    """

    def __eq__(self, other):
        return not self<other and not other<self

    def __ne__(self, other):
        return self<other or other<self

    def __gt__(self, other):
        return other<self

    def __ge__(self, other):
        return not self<other

    def __le__(self, other):
        return not other<self

class CalendarDate(ComparableMixin, _CalendarDate):
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
        A year of 1 is 1 AD, a year of 0 is 1 BC, 
        a year of -1 is 2 BC, etc.
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

    AD_ERAS = ('AD', 'CE', 'A.D.', 'C.E.')

    DEFAULT_AD = 'AD'

    BC_ERAS = ('BC', 'BCE', 'B.C.', 'B.C.E.')

    DEFULT_BC = 'BC'

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
        y_, era = self.convert_signed_year(y)
        if era in self.BC_ERAS:
            return f'{dow} {d} {m} {y_} {era}'
        else:
            return f'{dow} {d} {m} {y}'
        

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other):
        if not isinstance(other, CalendarDate):
            raise NotImplementedError

        if self.year > other.year:
            return False

        if self.year < other.year:
            return True

        if self.month > other.month:
            return False

        if self.month < other.month:
            return True

        if self.day > other.day:
            return False

        if self.day < other.day:
            return True

        return False

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
        return cls.from_dmy(day=dt.day,
                            month=dt.month,
                            year=dt.year)

    @classmethod
    def from_dmy(cls, day: uint8, month: uint8, year: int256) -> CalendarDate:
        """
        Create a calendar date by providing only the day,
        month and year.
        """
        _cd = cls(day_of_week=0, #dummy placeholder
                  day=day,
                  month=month,
                  year=year)
        dow = cls.day_of_week_from_jd(_cd.to_jd())
        return cls(day_of_week=dow,
                   day=day,
                   month=month,
                   year=year)  

    @classmethod
    def from_unix_timestamp(cls, ts: uint256) -> CalendarDate:
        """
        Create a calendar date by providing a unix
        timestamp.
        """
        return cls.from_datetime(datetime.datetime.utcfromtimestamp(ts))

    @classmethod
    def convert_signed_year(cls, year: int256) -> Tuple[uint256, str]:
        """
        Converts a signed year to a tuple of (positive year, era)
        which is the convention used in calendars.
        """
        if year <= 0:
            year = -year + 1
            return (year, cls.DEFULT_BC)

        return (year, cls.DEFAULT_AD)


    @classmethod
    def convert_unsigned_year(cls, year: uint256, era: str=DEFULT_BC) -> int256:
        """
        Converts an usigned year and era combination
        to a signed year.
        """
        if era in cls.BC_ERAS:
            year = -(year - 1)

        return year

    @classmethod
    def get_century_of_signed_year(cls, year: int256) -> Tuple[uint256, str]:
        """
        Get the (century, era) for a given signed year.
        """
        uns_y, era = cls.convert_signed_year(year)
        return (math.ceil(uns_y / 100), era)

    @classmethod
    def get_signed_bounds_of_century(cls, century: uint256, era: str=DEFULT_BC) -> Tuple[int256, int256]:
        """
        Get the starting and ending signed years of a given
        (century, era) combination.
        """
        if era in cls.BC_ERAS:
            # -99-0, -399--300, etc.
            start = -century * 100 + 1;
            end = (-century + 1) * 100
        else:
            # 1-100, 1901-2000, etc.
            start = (century - 1) * 100 + 1
            end = century * 100
        return (start, end)
        

    @property
    def valid(self) -> bool:
        """
        Determines whether the Calendar date is valid.

        A date is valid if it matches the inferred
        date from its JD.
        """
        cls = self.__class__
        d_from_jd = cls.from_jd(self.to_jd())
        return self == d_from_jd

    def to_jd(self) -> JulianDate:
        raise NotImplementedError

    def to_dti(self) -> DateTokenIndex:
        """
        Convert a Calendar date to a
        date token index>
        """
        return self.to_jd().to_dti()


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

    def to_jcal_date(self) -> JCalDate:
        """
        Convert the Gregorian calendar date
        to the equivalent Julian
        calendar date. They both have
        the same Julian Date.
        """
        return self.to_jd().to_jcal_date()

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

    def to_gcal_date(self) -> GCalDate:
        """
        Convert the Julian calendar date
        to the equivalent Gregorian
        calendar date. They both have
        the same Julian Date.
        """
        return self.to_jd().to_gcal_date()

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

