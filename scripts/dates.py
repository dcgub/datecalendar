import spiceypy as sp

from collections import defaultdict, OrderedDict

sp.furnsh('naif0012.tls')

def spice_date_to_date(spice_date):
	# Remove the concept of time
	date = ' '.join(spice_date.split(' ')[:-1])
	# Can replace B.C./A.D. with BCE and CE??
	return date


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

# Add a Date class for our dates with str implementation
# Make sure to run gregorian calendar tests

