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

