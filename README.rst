`DateCalendar <https://github.com/dcgub/datecalendar>`__
========================================================

This module implements the core concepts of the
DateCalendar.sol smart contract.

Dates in the calendar are as of 00:00 UT (Universal Time).
The Date Token Index (DTI) is the unique identifier used to keep 
track of the date tokens in the smart contract and 
represents the relative positioning of all possible dates 
in the calendar.

DTI

0                                                40*10**9*365.25
|------------------------------------------------|

Since the difference between two date token indices
represents the number of times an entire day has passed
in UT, all potential dates in the calendar span over
40 billion years (40*10**9). For context, the
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

0                       20*10**9*365.25          40*10**9*365.25
|-----------------------|------------------------|

JD=(JDN, day fraction)

(-20*10**9*365.25, 0.5 ) (0, 0.5)                (20*10**9*365.25, 0.5)
|-----------------------|------------------------|

When a token is minted, the DateCalendar
smart contract simultaneously assigns
a date to the date token index
as a verifiable proof of the date that is owned by
a token holder. This date represents a date 
in the Greogrian calendar, which is the calendar
in common use today. 

For example, the JD of -0.5 has a Gregorian
calendar date of Monday 1 January 4713 BC.

Calendars in popular use have changed throughout 
history and are likely to continue changing.
The Gregorian calendar was first introduced
on Friday 15 October 1582 as a modification to
the Julian calendar in order to remove the "drift"
in the solar year. These 2 calendar systems can have
different dates for a given JD. For example,
the day before the Gregorian calendar was implemented
was Thursday 4 October 1582 in the Julian calendar.

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