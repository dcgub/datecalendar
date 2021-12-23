import datecalendar as dc

import pytest

def test_dti():
	lower, upper = dc.uint256.get_int_bounds()

	# DTI works at upper and lower bounds
	# but breaks beyond that point
	dc.DateTokenIndex(lower)
	dc.DateTokenIndex(upper)

	with pytest.raises(OverflowError):
		dc.DateTokenIndex(lower - 1)

	with pytest.raises(OverflowError):
		dc.DateTokenIndex(upper + 1)


def test_jd():
	lower, upper = dc.int256.get_int_bounds()

	# DTI works at upper and lower bounds
	# but breaks beyond that point
	dc.JulianDate(lower, 5)
	dc.JulianDate(upper, 5)

	with pytest.raises(OverflowError):
		dc.JulianDate(lower - 1, 5)

	with pytest.raises(OverflowError):
		dc.JulianDate(upper + 1, 5)	


def test_dti_jd():
	ulower, uupper = dc.uint256.get_int_bounds()
	ilower, iupper = dc.int256.get_int_bounds()

	dti = dc.DateTokenIndex(ulower)
	assert dti.to_jd().to_dti() == dti
	assert dti.to_jd() == dc.JulianDate(ilower, 5)

	dti = dc.DateTokenIndex(uupper)
	assert dti.to_jd().to_dti() == dti
	assert dti.to_jd() == dc.JulianDate(iupper, 5)

	dti = dc.DateTokenIndex(dc.DateTokenIndex.MIDPOINT)
	assert dti.to_jd().to_dti() == dti
	assert dti.to_jd() == dc.JulianDate(dc.int256.get_midpoint_value(), 5)

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
	('15 October 1582', 'Friday 15 October 1582 CE'),
	('September 11, 2001', 'Tuesday 11 September 2001 CE'),
	('2021 12 22', 'Wednesday 22 December 2021 CE'),
	('2021 12 25', 'Saturday 25 December 2021 CE'),
	('2018 06 19', 'Tuesday 19 June 2018 CE'),
	('2016 02 29', 'Monday 29 February 2016 CE')
]

@pytest.mark.parametrize("gcal_str,expected", test_gcal_dow_data)
def test_gcal_day_of_week(gcal_str, expected):
	assert str(dc.GCalDate.from_string(gcal_str)) == expected

def test_gcal_additions():
	jd0 = dc.JulianDate(-1, 5)
	assert str(jd0.to_gcal_date()) == 'Monday 24 November 4714 BCE'
	jd1 = dc.JulianDate(0, 5)
	assert str(jd1.to_gcal_date()) == 'Tuesday 25 November 4714 BCE'
	jd2 = dc.JulianDate(1, 5)
	assert str(jd2.to_gcal_date()) == 'Wednesday 26 November 4714 BCE'
	jd3 = dc.JulianDate(2, 5)
	assert str(jd3.to_gcal_date()) == 'Thursday 27 November 4714 BCE'
	jd4 = dc.JulianDate(3, 5)
	assert str(jd4.to_gcal_date()) == 'Friday 28 November 4714 BCE'
	jd5 = dc.JulianDate(4, 5)
	assert str(jd5.to_gcal_date()) == 'Saturday 29 November 4714 BCE'
	jd6 = dc.JulianDate(5, 5)
	assert str(jd6.to_gcal_date()) == 'Sunday 30 November 4714 BCE'
	jd6 = dc.JulianDate(-24, 5)
	gcal = jd6.to_gcal_date()
	assert gcal.day == 1
	assert gcal.month == 11
	assert gcal.year == -4713

def test_gcal_bounds():
	ulower, uupper = dc.uint256.get_int_bounds()

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

	jd = dc.DateTokenIndex(ulower + 365).to_jd()
	gcal = jd.to_gcal_date()
	assert y + 1 == gcal.year

	jd = dc.DateTokenIndex(ulower + 365 * 10).to_jd()
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

	jd = dc.DateTokenIndex(uupper - 365).to_jd()
	gcal = jd.to_gcal_date()
	assert y - 1 == gcal.year

	jd = dc.DateTokenIndex(uupper - 365 * 10).to_jd()
	gcal = jd.to_gcal_date()
	assert y - 10 == gcal.year



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

# test_gcal_dow_data = [
# 	('15 October 1582', 'Friday 15 October 1582 CE'),
# 	('September 11, 2001', 'Tuesday 11 September 2001 CE'),
# 	('2021 12 22', 'Wednesday 22 December 2021 CE'),
# 	('2021 12 25', 'Saturday 25 December 2021 CE'),
# 	('2018 06 19', 'Tuesday 19 June 2018 CE'),
# 	('2016 02 29', 'Monday 29 February 2016 CE')
# ]

# @pytest.mark.parametrize("gcal_str,expected", test_gcal_dow_data)
# def test_gcal_day_of_week(gcal_str, expected):
# 	assert str(dc.GCalDate.from_string(gcal_str)) == expected

# def test_gcal_additions():
# 	jd0 = dc.JulianDate(-1, 5)
# 	assert str(jd0.to_gcal_date()) == 'Monday 24 November 4714 BCE'
# 	jd1 = dc.JulianDate(0, 5)
# 	assert str(jd1.to_gcal_date()) == 'Tuesday 25 November 4714 BCE'
# 	jd2 = dc.JulianDate(1, 5)
# 	assert str(jd2.to_gcal_date()) == 'Wednesday 26 November 4714 BCE'
# 	jd3 = dc.JulianDate(2, 5)
# 	assert str(jd3.to_gcal_date()) == 'Thursday 27 November 4714 BCE'
# 	jd4 = dc.JulianDate(3, 5)
# 	assert str(jd4.to_gcal_date()) == 'Friday 28 November 4714 BCE'
# 	jd5 = dc.JulianDate(4, 5)
# 	assert str(jd5.to_gcal_date()) == 'Saturday 29 November 4714 BCE'
# 	jd6 = dc.JulianDate(5, 5)
# 	assert str(jd6.to_gcal_date()) == 'Sunday 30 November 4714 BCE'
# 	jd6 = dc.JulianDate(-24, 5)
# 	gcal = jd6.to_gcal_date()
# 	assert gcal.day == 1
# 	assert gcal.month == 11
# 	assert gcal.year == -4713

# def test_gcal_bounds():
# 	ulower, uupper = dc.uint256.get_int_bounds()

# 	jdl = dc.DateTokenIndex(ulower).to_jd()
# 	gcall = jdl.to_gcal_date()
# 	y = gcall.year
# 	m = gcall.month
# 	d = gcall.day

# 	for i in range(1, 10):
# 		jd = dc.DateTokenIndex(ulower + i).to_jd()
# 		gcal = jd.to_gcal_date()
# 		assert y == gcal.year
# 		assert m == gcal.month
# 		assert d + i == gcal.day

# 	jd = dc.DateTokenIndex(ulower + 365).to_jd()
# 	gcal = jd.to_gcal_date()
# 	assert y + 1 == gcal.year

# 	jd = dc.DateTokenIndex(ulower + 365 * 10).to_jd()
# 	gcal = jd.to_gcal_date()
# 	assert y + 10 == gcal.year

# 	jdl = dc.DateTokenIndex(uupper).to_jd()
# 	gcall = jdl.to_gcal_date()
# 	y = gcall.year
# 	m = gcall.month
# 	d = gcall.day

# 	for i in range(1, 10):
# 		jd = dc.DateTokenIndex(uupper - i).to_jd()
# 		gcal = jd.to_gcal_date()
# 		assert y == gcal.year
# 		assert m == gcal.month
# 		assert d - i == gcal.day

# 	jd = dc.DateTokenIndex(uupper - 365).to_jd()
# 	gcal = jd.to_gcal_date()
# 	assert y - 1 == gcal.year

# 	jd = dc.DateTokenIndex(uupper - 365 * 10).to_jd()
# 	gcal = jd.to_gcal_date()
# 	assert y - 10 == gcal.year


#JCal
# test baum table
# test sample day of weeks
# test JD additions and subtractions
# test around dti bounds


#SLOW
# Create GCals from +- 1m years around 0, close to upper and lower bounds
# Make sure we have exact number of dates
# Make sure counting leap years worked

# Compare +- 10000 years against other from/tojd algos
# NASA
# Astronomical algorithms
# python jdcal pypi