import spiceypy as sp

from collections import defaultdict, OrderedDict

sp.furnsh('naif0012.tls')

def spice_date_to_date(spice_date):
	# Remove the concept of time
	date = ' '.join(spice_date.split(' ')[:-1])
	# Can replace B.C./A.D. with BCE and CE??
	return date


### ADD DATE CLASS FOR DATE IMPLEMENTATION


start_date = '4999 B.C. Jan 1'
end_date = '4999 A.D. Dec 31'

start_et = sp.str2et(start_date)
end_et = sp.str2et(end_date)

day_delta_in_seconds = 24 * 60 * 60 

all_dates = OrderedDict()
et = start_et
while et < end_et:
	spice_date = sp.etcal(et)
	date = spice_date_to_date(spice_date)
	all_dates[date] = None
	# Note we will increment
	# et by 1/2 a day just to 
	# be safe no gregorian dates
	# are missed due to leap seconds.
	et += day_delta_in_seconds / 2

all_dates = list(all_dates)

# Gregorian calendar tests
dates_by_year = defaultdict(list)
for date in all_dates:
	dsplit = date.split(' ')
	if len(dsplit) == 4:
		year, era, mon, day = dsplit
	else:
		year, mon, day = dsplit
		era = 'A.C.'
	year = int(year)
	if era == 'B.C.':
		year = -year
	dates_by_year[year].append(date)

# Gregorian calendar test checking leap years
# Source: https://docs.microsoft.com/en-us/office/troubleshoot/excel/determine-a-leap-year
for year, dates in dates_by_year.items():
	# For negative years, logic still applies
	# but year needs to be shifted by 1
	if year < 0:
		year = year + 1
	is_leap = False
	div_4 = not year % 4
	if div_4:
		div_100 = not year % 100
		if not div_100:
			is_leap = True
		else:
			div_400 = not year % 400
			if div_400:
				is_leap = True
	if is_leap:
		assert len(dates) == 366
	else:
		assert len(dates) == 365


# Good references 
# Source: https://exoplanetarchive.ipac.caltech.edu/docs/transit_algorithms.html
# Source: https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/FORTRAN/req/time.html#Julian%20Date
# Source: https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/FORTRAN/spicelib/index.html#A
# https://github.com/phn/jdcal
# https://adsabs.harvard.edu/pdf/1984QJRAS..25...53H
# http://www.iausofa.org/2021_0512_C/CompleteList.html
# http://www.iausofa.org/2021_0512_C/sofa/jd2cal.c
# https://archive.org/stream/131123ExplanatorySupplementAstronomicalAlmanac/131123-explanatory-supplement-astronomical-almanac_djvu.txt
# https://www.hermetic.ch/cal_stud/jdn.htm
# http://www.cs.otago.ac.nz/cosc345/resources/Fliegel.pdf
# http://www.agopax.it/Libri_astronomia/pdf/Astronomical%20Algorithms.pdf

# https://www.researchgate.net/publication/316558298_Date_Algorithms ### VERY GOOD

MJD_0 = 2400000.5
MJD_JD2000 = 51544.5


def is_leap(year):
    """Leap year or not in the Gregorian calendar."""
    x = year % 4
    y = year % 100
    z = year % 400

    # Divisible by 4 and,
    # either not divisible by 100 or divisible by 400.
    return not x and (y or not z)


def gcal2jd(year, month, day):
    """Gregorian calendar date to Julian date.
    The input and output are for the proleptic Gregorian calendar,
    i.e., no consideration of historical usage of the calendar is
    made.
    Parameters
    ----------
    year : int
        Year as an integer.
    month : int
        Month as an integer.
    day : int
        Day as an integer.
    Returns
    -------
    jd1, jd2: 2-element tuple of floats
        When added together, the numbers give the Julian date for the
        given Gregorian calendar date. The first number is always
        MJD_0 i.e., 2451545.5. So the second is the MJD.
    Examples
    --------
    >>> gcal2jd(2000,1,1)
    (2400000.5, 51544.0)
    >>> 2400000.5 + 51544.0 + 0.5
    2451545.0
    >>> year = [-4699, -2114, -1050, -123, -1, 0, 1, 123, 1678.0, 2000,
    ....: 2012, 2245]
    >>> month = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    >>> day = [1, 12, 23, 14, 25, 16, 27, 8, 9, 10, 11, 31]
    >>> x = [gcal2jd(y, m, d) for y, m, d in zip(year, month, day)]
    >>> for i in x: print i
    (2400000.5, -2395215.0)
    (2400000.5, -1451021.0)
    (2400000.5, -1062364.0)
    (2400000.5, -723762.0)
    (2400000.5, -679162.0)
    (2400000.5, -678774.0)
    (2400000.5, -678368.0)
    (2400000.5, -633797.0)
    (2400000.5, -65812.0)
    (2400000.5, 51827.0)
    (2400000.5, 56242.0)
    (2400000.5, 141393.0)
    Negative months and days are valid. For example, 2000/-2/-4 =>
    1999/+12-2/-4 => 1999/10/-4 => 1999/9/30-4 => 1999/9/26.
    >>> gcal2jd(2000, -2, -4)
    (2400000.5, 51447.0)
    >>> gcal2jd(1999, 9, 26)
    (2400000.5, 51447.0)
    >>> gcal2jd(2000, 2, -1)
    (2400000.5, 51573.0)
    >>> gcal2jd(2000, 1, 30)
    (2400000.5, 51573.0)
    >>> gcal2jd(2000, 3, -1)
    (2400000.5, 51602.0)
    >>> gcal2jd(2000, 2, 28)
    (2400000.5, 51602.0)
    Month 0 becomes previous month.
    >>> gcal2jd(2000, 0, 1)
    (2400000.5, 51513.0)
    >>> gcal2jd(1999, 12, 1)
    (2400000.5, 51513.0)
    Day number 0 becomes last day of previous month.
    >>> gcal2jd(2000, 3, 0)
    (2400000.5, 51603.0)
    >>> gcal2jd(2000, 2, 29)
    (2400000.5, 51603.0)
    If `day` is greater than the number of days in `month`, then it
    gets carried over to the next month.
    >>> gcal2jd(2000,2,30)
    (2400000.5, 51604.0)
    >>> gcal2jd(2000,3,1)
    (2400000.5, 51604.0)
    >>> gcal2jd(2001,2,30)
    (2400000.5, 51970.0)
    >>> gcal2jd(2001,3,2)
    (2400000.5, 51970.0)
    Notes
    -----
    The returned Julian date is for mid-night of the given date. To
    find the Julian date for any time of the day, simply add time as a
    fraction of a day. For example Julian date for mid-day can be
    obtained by adding 0.5 to either the first part or the second
    part. The latter is preferable, since it will give the MJD for the
    date and time.
    BC dates should be given as -(BC - 1) where BC is the year. For
    example 1 BC == 0, 2 BC == -1, and so on.
    Negative numbers can be used for `month` and `day`. For example
    2000, -1, 1 is the same as 1999, 11, 1.
    The Julian dates are proleptic Julian dates, i.e., values are
    returned without considering if Gregorian dates are valid for the
    given date.
    The input values are truncated to integers.
    """
    year = int(year)
    month = int(month)
    day = int(day)

    a = int((month - 14) / 12.0)
    jd = int((1461 * (year + 4800 + a)) / 4.0)
    jd += int((367 * (month - 2 - 12 * a)) / 12.0)
    x = int((year + 4900 + a) / 100.0)
    jd -= int((3 * x) / 4.0)
    jd += day - 2432075.5  # was 32075; add 2400000.5

    jd -= 0.5  # 0 hours; above JD is for midday, switch to midnight.

    return MJD_0, jd


def gcal2jd2(year, month, day):
	# https://adsabs.harvard.edu/full/1983IAPPP..13...16F
	p1 = 367 * year
	a = year + int((month + 9) / 12)
	p2 = -int(7 * a / 4)
	c = int((month - 9) / 7)
	b = int((year + c) / 100)
	p3 = -int(3 * (b + 1) / 4)
	p4 = int(275 * month / 9)
	p5 = 1721029
	return p1 + p2 + p3 + p4 + p5


def gcal2jd2(year, month, date):
	# https://www.hermetic.ch/cal_stud/jdn.htm
	if month 
	a = 







