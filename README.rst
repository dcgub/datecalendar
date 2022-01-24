`Date Calendar <https://github.com/dcgub/datecalendar>`__
=========================================================

Date Calendar is a uniquely generated calendar where each date's proof of ownership is stored on the Ethereum blockchain. This `repo <https://github.com/dcgub/datecalendar>`__ contains 

#. The DateCalendar.sol smart contract
#. The datecalendar Python package that replicates the smart contract algorithms responsible for storing each date's proof of ownership.

How Date Calendar Proves Ownership
----------------------------------

The DateCalendar.sol smart contract implements the `ERC721 Non-Fungible Token (NFT) Standard <https://eips.ethereum.org/EIPS/eip-721>`__. Whenever a token gets minted or transferred, this standard assigns the new owner's address to the token's index. I.e. the 10th token is owned by Bob. 

Most NFT projects, such as those whose tokens represent a digital image, will save the order of the images on the smart contract so that token holders can independently verify that the image they own is in the same position as the index. This can be done by saving a hash of all images in the proper order on the smart contract or by providing the hash of the image to the smart contract when it gets minted. Of course, there should be no way to tamper with the order of the images on the smart contract otherwise token holders might lose faith in the project.

Date Calendar proves ownership in a slightly different way. When a Date Token Index (DTI) gets minted and assigned to an owner, the smart contract simultaneously generates the unique date that is represented by the DTI and saves it to the ledger. In this way, the project does not need to pre-create and store all possible dates in the calendar since the proof of ownership occurs as date tokens get minted. Token holders can independently verify the dates they own by calling the smart contract and checking that their dates (day of week, day, month, year) have been assigned to their token indices.

Converting Between Indices and Dates
------------------------------------

When a Date Token is minted, Date Calendar converts the token index to a calendar date. The following describes how this conversion happens.

Dates in the calendar are as of 00:00 UT (Universal Time). The Date Token Index (DTI) is the unique identifier used to keep track of the date tokens in the smart contract and represents the relative positioning of all possible dates in the calendar.

==================== ==================== ====================
DTI
--------------------------------------------------------------
Start                Middle               End
==================== ==================== ====================
0                    20*10**9*365.25      40*10**9*365.25
==================== ==================== ====================


Since the difference between two date token indices represents the number of times an entire day has passed in UT, all potential dates in the calendar span over 40 billion years (40*10**9). For context, the age of the universe is assumed to be roughly 14 billion years (14*10**9).

Astronomers use a similar concept for calculating the elapsed days between two events: a Julian day number (JDN). The JDN for a given day is an integer describing the number of solar days between the given day and a fixed day in history starting from 12:00 UT (noon). This fixed day in history is referred to as the Julian epoch and it has a JDN value of 0.

The Julian date (JD) of any instant is the JDN plus the fraction of a day since the preceding 12:00 UT. Since all dates in Date Calendar are as of 00:00 UT, then their corresponding JDs will have a fixed day fraction of +0.5.

Date Calendar links date token indices to JDs by setting the midpoint of the index to the JD of 0.5 (JDN of 0 and day fraction of 0.5).

==================== ==================== ====================
DTI
--------------------------------------------------------------
Start                Middle               End
==================== ==================== ====================
0                    20*10**9*365.25      40*10**9*365.25
==================== ==================== ====================

======================= ======================= =======================
JD=(JDN, day fraction)
-----------------------------------------------------------------------
Start                   Middle                  End
======================= ======================= =======================
(-20*10**9*365.25, 0.5) (0, 0.5)                (20*10**9*365.25, 0.5)
======================= ======================= =======================


Finally, Date Calendar converts the JD to a calendar date (day of week, day, month, year) using a date conversion algorithm developed by `Peter Baum <https://www.researchgate.net/publication/316558298_Date_Algorithms>`__. This date represents a date in the Greogrian calendar, which is the calendar in common use today. For example, the JD of 37.5 has a Gregorian calendar date of Thursday 1 January 4713 BC.


Date Calendar Uses Gregorian Calendar Dates
-------------------------------------------

Calendars in popular use have changed throughout history and are likely to continue changing. The Gregorian calendar was first introduced on Friday 15 October 1582 as a modification to the Julian calendar in order to remove the "drift" in the solar year. These 2 calendar systems can have
different dates for a given JD. For example, the day before the Gregorian calendar was implemented was Thursday 4 October 1582 in the Julian calendar. 

In Date Calendar, all historical dates, even those prior to the invention of the Gregorian calendar, will be represented as a date in the Gregorian calendar, formally known as a proleptic calendar. Some historians report events using the common calendar at the time, meaning users should
take special care in converting those dates to the equivalent Gregorian calendar dates or JDs in order to determine the correct date tokens to mint.

The datecalendar Python Package
-------------------------------

This package replicates the Date Calendar smart contract algorithms responsible for storing each date's proof of ownership. It contains various utilities to convert to and from the various date representations: date token index, Julian Date, Julian calendar date, Gregorian calendar date. Many of these utilities were created using the algorithmns outlined and developed by `Peter Baum <https://www.researchgate.net/publication/316558298_Date_Algorithms>`__.

Usage
-----

.. code-block:: bash

    $ pip install datecalendar

.. code-block:: python

	import datecalendar as dc

	# What is the date for this index?
	dti = dc.DateTokenIndex(20*10**9*365.25)
	jd = dti.to_jd()
	date = jd.to_gcal_date()
	print(date)

	# Ethereum was created on this day
	date = dc.GCalDate.from_string('July 30, 2015')
	# Date Token Index of this date
	print(date.to_dti())