import datecalendar as dc

import pytest
import jdcal
import spiceypy as sp

from collections import defaultdict

def test_dti():
	lower, upper = dc.DateTokenIndex.get_int_bounds()

	# DTI works at upper and lower bounds
	# but breaks beyond that point
	dc.DateTokenIndex(lower)
	dc.DateTokenIndex(upper)

	with pytest.raises(OverflowError):
		dc.DateTokenIndex(lower - 1)

	with pytest.raises(OverflowError):
		dc.DateTokenIndex(upper + 1)


def test_jd():
	lower, upper = dc.JDN.get_int_bounds()

	# DTI works at upper and lower bounds
	# but breaks beyond that point
	dc.JulianDate(lower, 5)
	dc.JulianDate(upper, 5)

	with pytest.raises(OverflowError):
		dc.JulianDate(lower - 1, 5)

	with pytest.raises(OverflowError):
		dc.JulianDate(upper + 1, 5)	


def test_dti_jd():
	ulower, uupper = dc.DateTokenIndex.get_int_bounds()
	ilower, iupper = dc.JDN.get_int_bounds()

	dti = dc.DateTokenIndex(ulower)
	assert dti.to_jd().to_dti() == dti
	assert dti.to_jd() == dc.JulianDate(ilower, 5)

	dti = dc.DateTokenIndex(uupper)
	assert dti.to_jd().to_dti() == dti
	assert dti.to_jd() == dc.JulianDate(iupper, 5)

	dti = dc.DateTokenIndex(dc.DateTokenIndex.MIDPOINT)
	assert dti.to_jd().to_dti() == dti
	assert dti.to_jd() == dc.JulianDate(dc.JDN.get_midpoint_value(), 5)

	dti_mid = dc.DateTokenIndex(dc.DateTokenIndex.MIDPOINT)
	for i in range(-10, 10):
		dti = dc.DateTokenIndex(dc.DateTokenIndex.MIDPOINT + i)
		assert dti.to_jd() == dc.JulianDate(dti_mid.to_jd().jdn + i, 5)
		assert dti == dc.JulianDate(dti_mid.to_jd().jdn + i, 5).to_dti()

test_gcal_data = [
	((-1, 5), (-4713, 11, 24)),
	((0, 5), (-4713, 11, 25)),
	((37, 5), (-4712, 1, 1)),
	((38, 5), (-4712, 1, 2)),
	((1721059, 5), (0, 1, 1)),
	((1721118, 5), (0, 2, 29)),
	((1721119, 5), (0, 3, 1)),
	((1721424, 5), (0, 12, 31)),
	((1721425, 5), (1, 1, 1)),
	((2299149, 5), (1582, 10, 4)),
	((2299160, 5), (1582, 10, 15)),
	((2393470, 5), (1840, 12, 31)),
	((2400000, 5), (1858, 11, 17)),
	((2415020, 5), (1900, 1, 1)),
	((2415385, 5), (1901, 1, 1)),
	((2440587, 5), (1970, 1, 1)),
	((2444239, 5), (1980, 1, 1)),
]

@pytest.mark.parametrize("jd_data,gcal_data", test_gcal_data)
def test_jd_gcal(jd_data, gcal_data):
	jd = dc.JulianDate(*jd_data)
	gcal = jd.to_gcal_date()
	assert gcal.to_jd() == jd
	assert gcal.to_jd().to_gcal_date() == gcal

	assert gcal.year == gcal_data[0]
	assert gcal.month == gcal_data[1]
	assert gcal.day == gcal_data[2]

test_gcal_dow_data = [
	('15 October 1582', 'Friday 15 October 1582'),
	('September 11, 2001', 'Tuesday 11 September 2001'),
	('2021 12 22', 'Wednesday 22 December 2021'),
	('2021 12 25', 'Saturday 25 December 2021'),
	('2018 06 19', 'Tuesday 19 June 2018'),
	('2016 02 29', 'Monday 29 February 2016')
]

@pytest.mark.parametrize("gcal_str,expected", test_gcal_dow_data)
def test_gcal_day_of_week(gcal_str, expected):
	assert str(dc.GCalDate.from_string(gcal_str)) == expected

def test_gcal_additions():
	jd0 = dc.JulianDate(-1, 5)
	assert str(jd0.to_gcal_date()) == 'Monday 24 November 4714 BC'
	jd1 = dc.JulianDate(0, 5)
	assert str(jd1.to_gcal_date()) == 'Tuesday 25 November 4714 BC'
	jd2 = dc.JulianDate(1, 5)
	assert str(jd2.to_gcal_date()) == 'Wednesday 26 November 4714 BC'
	jd3 = dc.JulianDate(2, 5)
	assert str(jd3.to_gcal_date()) == 'Thursday 27 November 4714 BC'
	jd4 = dc.JulianDate(3, 5)
	assert str(jd4.to_gcal_date()) == 'Friday 28 November 4714 BC'
	jd5 = dc.JulianDate(4, 5)
	assert str(jd5.to_gcal_date()) == 'Saturday 29 November 4714 BC'
	jd6 = dc.JulianDate(5, 5)
	assert str(jd6.to_gcal_date()) == 'Sunday 30 November 4714 BC'
	jd6 = dc.JulianDate(-24, 5)
	gcal = jd6.to_gcal_date()
	assert gcal.day == 1
	assert gcal.month == 11
	assert gcal.year == -4713

def test_gcal_bounds():
	ulower, uupper = dc.DateTokenIndex.get_int_bounds()

	jdl = dc.DateTokenIndex(ulower).to_jd()
	gcall = jdl.to_gcal_date()
	y = gcall.year
	m = gcall.month
	d = gcall.day

	for i in range(1, 10):
		jd = dc.DateTokenIndex(ulower + i).to_jd()
		gcal = jd.to_gcal_date()
		assert y == gcal.year
		assert m == gcal.month
		assert d + i == gcal.day

	jd = dc.DateTokenIndex(ulower + 365.25).to_jd()
	gcal = jd.to_gcal_date()
	assert y + 1 == gcal.year

	jd = dc.DateTokenIndex(ulower + 365.25 * 10).to_jd()
	gcal = jd.to_gcal_date()
	assert y + 10 == gcal.year

	jdl = dc.DateTokenIndex(uupper).to_jd()
	gcall = jdl.to_gcal_date()
	y = gcall.year
	m = gcall.month
	d = gcall.day

	for i in range(1, 10):
		jd = dc.DateTokenIndex(uupper - i).to_jd()
		gcal = jd.to_gcal_date()
		assert y == gcal.year
		assert m == gcal.month
		assert d - i == gcal.day

	jd = dc.DateTokenIndex(uupper - 365.25).to_jd()
	gcal = jd.to_gcal_date()
	assert y - 1 == gcal.year

	jd = dc.DateTokenIndex(uupper - 365.25 * 10).to_jd()
	gcal = jd.to_gcal_date()
	assert y - 10 == gcal.year


test_valid_data = [
	((1, 1, 2020), True),
	((5, 5, 2020), True),
	((7, 8, 2020), True),
	((12, 8, 2020), True),
	((19, 11, 2020), True),
	((25, 12, 2020), True),
	((31, 1, 2000), True),
	((28, 2, 2000), True),
	((29, 2, 2000), True),
	((31, 3, 2000), True),
	((30, 4, 2000), True),
	((31, 5, 2015), True),
	((30, 6, 2015), True),
	((31, 7, 2015), True),
	((31, 8, 2015), True),
	((30, 9, 2021), True),
	((31, 10, 2021), True),
	((30, 11, 2021), True),
	((31, 12, 2021), True),

	((32, 1, 2000), False),
	((30, 2, 2000), False),
	((32, 3, 2000), False),
	((31, 4, 2000), False),
	((32, 5, 2015), False),
	((31, 6, 2015), False),
	((32, 7, 2015), False),
	((32, 8, 2015), False),
	((31, 9, 2021), False),
	((32, 10, 2021), False),
	((31, 11, 2021), False),
	((32, 12, 2021), False),

	((40, 1, 2021), False),
	((60, 12, 2021), False),
]

@pytest.mark.parametrize("dmy,valid", test_valid_data)
def test_gcal_valid(dmy, valid):
	return dc.GCalDate.from_dmy(*dmy).valid == valid

test_jcal_data = [
	((-39, 5), (-4713, 11, 24)),
	((-38, 5), (-4713, 11, 25)),
	((-1, 5), (-4712, 1, 1)),
	((0, 5), (-4712, 1, 2)),
	((1721057, 5), (0, 1, 1)),
	((1721116, 5), (0, 2, 29)),
	((1721117, 5), (0, 3, 1)),
	((1721422, 5), (0, 12, 31)),
	((1721423, 5), (1, 1, 1)),
	((2299159, 5), (1582, 10, 4)),
	((2299170, 5), (1582, 10, 15)),
	((2393482, 5), (1840, 12, 31)),
	((2400012, 5), (1858, 11, 17)),
	((2415032, 5), (1900, 1, 1)),
	((2415398, 5), (1901, 1, 1)),
	((2440600, 5), (1970, 1, 1)),
	((2444252, 5), (1980, 1, 1)),
]

@pytest.mark.parametrize("jd_data,jcal_data", test_jcal_data)
def test_jd_gcal(jd_data, jcal_data):
	jd = dc.JulianDate(*jd_data)
	jcal = jd.to_jcal_date()
	assert jcal.to_jd() == jd
	assert jcal.to_jd().to_jcal_date() == jcal

	assert jcal.year == jcal_data[0]
	assert jcal.month == jcal_data[1]
	assert jcal.day == jcal_data[2]

@pytest.mark.parametrize("gcal_str,ignore", test_gcal_dow_data)
def test_jcal_day_of_week(gcal_str, ignore):
	# DOW is the same for GCal and JCal given the same
	# JD
	gcal = dc.GCalDate.from_string(gcal_str)
	jcal = gcal.to_jd().to_jcal_date()
	assert gcal.day_of_week == jcal.day_of_week
	assert gcal != jcal

def test_jcal_additions():
	jd0 = dc.JulianDate(-1, 5)
	assert str(jd0.to_jcal_date()) == 'Monday 1 January 4713 BC'
	jd1 = dc.JulianDate(0, 5)
	assert str(jd1.to_jcal_date()) == 'Tuesday 2 January 4713 BC'
	jd2 = dc.JulianDate(1, 5)
	assert str(jd2.to_jcal_date()) == 'Wednesday 3 January 4713 BC'
	jd3 = dc.JulianDate(2, 5)
	assert str(jd3.to_jcal_date()) == 'Thursday 4 January 4713 BC'
	jd4 = dc.JulianDate(3, 5)
	assert str(jd4.to_jcal_date()) == 'Friday 5 January 4713 BC'
	jd5 = dc.JulianDate(4, 5)
	assert str(jd5.to_jcal_date()) == 'Saturday 6 January 4713 BC'
	jd6 = dc.JulianDate(5, 5)
	assert str(jd6.to_jcal_date()) == 'Sunday 7 January 4713 BC'
	jd6 = dc.JulianDate(29, 5)
	jcal = jd6.to_jcal_date()
	assert jcal.day == 31
	assert jcal.month == 1
	assert jcal.year == -4712

def test_jcal_bounds():
	ulower, uupper = dc.DateTokenIndex.get_int_bounds()

	jdl = dc.DateTokenIndex(ulower).to_jd()
	jcall = jdl.to_jcal_date()
	y = jcall.year
	m = jcall.month
	d = jcall.day

	for i in range(1, 10):
		jd = dc.DateTokenIndex(ulower + i).to_jd()
		jcal = jd.to_jcal_date()
		assert y == jcal.year
		assert m == jcal.month
		assert d + i == jcal.day

	jd = dc.DateTokenIndex(ulower + 365.25).to_jd()
	jcal = jd.to_jcal_date()
	assert y + 1 == jcal.year

	jd = dc.DateTokenIndex(ulower + 365.25 * 10).to_jd()
	jcal = jd.to_jcal_date()
	assert y + 10 == jcal.year


	# Date at uupper in jan 2, so we will subtract
	# 3 days for this test
	uupper -= 3
	jdl = dc.DateTokenIndex(uupper).to_jd()
	jcall = jdl.to_jcal_date()
	y = jcall.year
	m = jcall.month
	d = jcall.day

	for i in range(1, 10):
		jd = dc.DateTokenIndex(uupper - i).to_jd()
		jcal = jd.to_jcal_date()
		assert y == jcal.year
		assert m == jcal.month
		assert d - i == jcal.day

	jd = dc.DateTokenIndex(uupper - 365.25).to_jd()
	jcal = jd.to_jcal_date()
	assert y - 1 == jcal.year

	jd = dc.DateTokenIndex(uupper - 365.25 * 10).to_jd()
	jcal = jd.to_jcal_date()
	assert y - 10 == jcal.year


@pytest.mark.parametrize("dmy,valid", test_valid_data)
def test_jcal_valid(dmy, valid):
	return dc.JCalDate.from_dmy(*dmy).valid == valid


ulower, uupper = dc.DateTokenIndex.get_int_bounds()
ylower = dc.DateTokenIndex(ulower).to_jd().to_gcal_date().year
yupper = dc.DateTokenIndex(uupper).to_jd().to_gcal_date().year
test_gcal_generation_data = [
	(-10000, 10000),
	(-1*10**6 - 5000, -1*10**6 + 5000),
	(1*10**6 - 5000, 1*10**6 + 5000),
	(-1*10**10 - 5000, -1*10**10 + 5000),
	(1*10**10 - 5000, 1*10**10 + 5000),
	(ylower + 1, ylower + 5000),
	(yupper - 5000, yupper - 1),
]

@pytest.mark.slow
@pytest.mark.parametrize("upper_year,lower_year", test_gcal_generation_data)
def test_large_gcal_generation(upper_year, lower_year):

	all_dates = set()
	dates_by_year = defaultdict(list)
	start_idx = dc.GCalDate(0, 1, 1, upper_year).to_jd().to_dti()
	end_idx = dc.GCalDate(0, 1, 1, lower_year).to_jd().to_dti()
	rng = range(start_idx, end_idx)
	for i in rng:
		dti = dc.DateTokenIndex(i)
		jd = dti.to_jd()
		dt = jd.to_gcal_date()
		all_dates.add(tuple(dt))
		dates_by_year[dt.year].append(dt)

	assert len(all_dates) == sum(len(v) for v in dates_by_year.values())
	assert len(all_dates) == len(rng)
	for y, vs in dates_by_year.items():
		v0 = vs[0]
		feb28 = dc.GCalDate(0, 28, 2, y).to_jd().to_gcal_date()
		feb29 = dc.GCalDate((feb28.day_of_week + 1) % 7, 29, 2, y)
		if v0.leap_year:
			assert len(vs) == 366
			assert feb29 in vs
		else:
			assert len(vs) == 365
			assert feb29 not in vs


@pytest.mark.slow
def test_gcal_vs_nasa():
	# We are going to test datecalendar
	# Gregorian calendar dates and make sure
	# they match exactly what NASA SPICE functions
	# report. For documentation on NASA SPICE, see
	# https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/FORTRAN/spicelib/
	sp.furnsh('tests/data/naif0012.tls')

	# Make sure all dates match from 4999 B.C. to 4999 A.D.
	start_date = '4999 B.C. Jan 1'
	end_date = '4999 A.D. Dec 31'
	day_delta_in_seconds = 24 * 60 * 60 

	nasa_jd2000 = sp.j2000()
	assert dc.GCalDate.from_string('2000 1 1').to_jd().to_float() == nasa_jd2000 - 0.5
	nasa_cal_month_formats = ('JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
							  'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC')

	start_et = sp.str2et(start_date)
	end_et = sp.str2et(end_date)
	et = start_et
	while et < end_et:
		
		nasa_dt = sp.etcal(et)
		s = nasa_dt.split(' ')
		if len(s) > 4:
			y = int(s[0])
			era = s[1]
			if era == 'B.C.':
				y = -y + 1
			d = int(s[3])
			m_idx = nasa_cal_month_formats.index(s[2])
		else:
			y = int(s[0])
			m_idx = nasa_cal_month_formats.index(s[1])
			d = int(s[2])
			
		m = m_idx + 1

		nasa_jd = et / day_delta_in_seconds + nasa_jd2000
		dc_jd = dc.JulianDate(nasa_jd // 1, 5)
		dc_date = dc_jd.to_gcal_date()
		assert dc_date.day == d
		assert dc_date.month == m
		assert dc_date.year == y
		
		et += day_delta_in_seconds


@pytest.mark.slow
def test_gcal_vs_sofa():
	# The python module `jdcal` has
	# algorithms converting from a Gregorian
	# calendar to a Julian Date. This implementation
	# uses the same algorithm found in the SOFA 
	# (Standards of Fundamental Astronomy) calendar software.
	# http://www.iausofa.org/2021_0512_C/Calendars.html
	# http://www.iausofa.org/2021_0512_C/sofa/jd2cal.c
	# This algorithm was developed by Fliegel and Van Flandern.
	# Ref: Explanatory Supplement to the Astronomical Almanac,
	# P. Kenneth Seidelmann (ed), University Science Books (1992),
	# Section 12.92 (p604).
	# Unfortunately, this algorithm is only valid after
	# November 23, -4713
	start_jd = sum(jdcal.gcal2jd(-4713, 11, 24))
	end_jd = sum(jdcal.gcal2jd(4999, 12, 31))
	ref_jd = 2400000.5

	jd = start_jd
	while jd < end_jd:
		
		dc_date = dc.JulianDate(jd // 1, 5).to_gcal_date()
		sofa_date = jdcal.jd2gcal(ref_jd, jd - ref_jd)
		
		assert dc_date.year == sofa_date[0]
		assert dc_date.month == sofa_date[1]
		assert dc_date.day == sofa_date[2]
		
		jd += 1