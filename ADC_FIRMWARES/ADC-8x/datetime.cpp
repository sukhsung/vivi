/* Subroutines for manipulating dates and times */

#include <Arduino.h>
#include "datetime.h"

char Date_time::buffer[32];

unsigned int Date_time::get_seconds(void)
{
	unsigned int	v, y, z, m;

	y = year - EPOCH_YEAR;		// Number of years before this year
	m = month;
	if (m < 3) {			// Adjusted month and year...
		m += 12;
		--y;
	}
	m -= 3;				// ... starting on March 1

	v = (y * 1461) / 4;	// Number of Julian days before this year
	z = y / 100;		// Number of centuries before this year
	v -= (z * 3 + 3) / 4;	// Number of Gregorian days before this year
	v += (m * 153 + 2) / 5;		// Number of days before this month
	v += day - 1;			// Number of days before this date
	v = ((v * 24 + hour) * 60 + minute) * 60 + second;
	return v;
}

unsigned int Date_time::get_time_seconds(void)
{
	return ((hour * 60) + minute) * 60 + second;
}

void Date_time::set_seconds(unsigned int s)
{
	unsigned int	v;

	v = s / 60;			// Minutes
	second = s - v * 60;
	s = v;

	v = s / 60;			// Hours
	minute = s - v * 60;
	s = v;

	v = s / 24;			// Days
	hour = s - v * 24;
	s = v;

	v = (s * 4 + 3) / 146097;	// Number of centuries
	year = v * 100 + EPOCH_YEAR;
	s -= (v * 146097) / 4;

	v = (s * 4 + 3) / 1461;		// Number of years past the century
	year += v;
	s -= (v * 1461) / 4;

	v = (s * 5 + 2) / 153;		// Number of months past the year
	month = v + 3;
	s -= (v * 153 + 2) / 5;

	if (month > 12) {		// Un-adjust month and year
		month -= 12;
		++year;
	}

	day = s + 1;
}

void Date_time::format(char *buffer)
{
	char	tzbuf[8];

	if (tz_offset == NO_TZ)
		*tzbuf = 0;
	else
		sprintf(tzbuf, "%+05d", tz_offset);
	sprintf(buffer, "%4u-%02u-%02u %02u:%02u:%02u%s",
			year, month, day, hour, minute, second, tzbuf);
}

void Date_time::format_time(char *buffer)
{
	sprintf(buffer, "%02u:%02u:%02u", hour, minute, second);
}

#define DLDATE		1	// '-' delimiter
#define DLTZ		2	// '+' delimiter
#define DLTIME		4	// ':' delimiter
#define DLEOS		8	// end-of-string delimiter

static int find_next_delimiter(const char *dtbuf, int pos, int dltype)
{
	int	c, cnt;

	/* Count the digits */
	cnt = 0;
	do {
		c = (unsigned char) dtbuf[pos];
		if (!('0' <= c && c <= '9'))
			break;
		if (++cnt > 4)
			return -1;
		++pos;
	} while (true);

	if (c == '-')
		c = DLDATE;
	else if (c == '+')
		c = DLTZ;
	else if (c == ':')
		c = DLTIME;
	else if (!c)
		c = DLEOS;
	else
		c = 0;
	if (cnt > 0 && (c & dltype))
		return pos;
	return -1;
}

int Date_time::parse_date(const char *dtbuf)
{
	int		rc;
	int		d1, d2, d3;
	unsigned int	y, m, d;
	Date_time	dt2;

	rc = 1;
	d1 = find_next_delimiter(dtbuf, 0, DLDATE);
	if (d1 < 0)
		return rc;
	y = atoi(&dtbuf[0]);

	++d1;
	d2 = find_next_delimiter(dtbuf, d1, DLDATE);
	if (d2 < 0)
		return rc;
	m = atoi(&dtbuf[d1]);

	++d2;
	d3 = find_next_delimiter(dtbuf, d2, DLEOS);
	if (d3 < 0)
		return rc;
	d = atoi(&dtbuf[d2]);

	if (y < 100) {
		if (y <= 20)
			y += EPOCH_YEAR + 100;
		else
			y += EPOCH_YEAR;
	}
	if (y <= EPOCH_YEAR || y > EPOCH_YEAR + 130 ||
			m <= 0 || m > 12 || d <= 0 || d > 31)
		return rc;

	/* Check the result */
	dt2.year = y;
	dt2.month = m;
	dt2.day = d;
	dt2.hour = dt2.minute = dt2.second = 0;
	dt2.set_seconds(dt2.get_seconds());
	if (y == dt2.year && m == dt2.month && d == dt2.day) {
		year = y;
		month = m;
		day = d;
		rc = 0;
	}
	return rc;
}

int Date_time::parse_time(const char *dtbuf, bool allow_tz)
{
	int		rc;
	int		d1, d2, d3, d4;
	unsigned int	h, m, s;
	int		tz, tza;

	rc = 1;
	d1 = find_next_delimiter(dtbuf, 0, DLTIME);
	if (d1 < 0)
		return rc;
	h = atoi(&dtbuf[0]);

	++d1;
	d2 = find_next_delimiter(dtbuf, d1, DLTIME | DLEOS);
	if (d2 < 0)
		return rc;
	m = atoi(&dtbuf[d1]);

	tz = tz_offset;
	d3 = DLEOS;
	if (allow_tz)
		d3 = DLEOS | DLDATE | DLTZ;

	s = 0;
	if (dtbuf[d2] == ':') {
		++d2;
		d3 = find_next_delimiter(dtbuf, d2, d3);
		if (d3 < 0)
			return rc;
		s = atoi(&dtbuf[d2]);
	}

	if (dtbuf[d3]) {
		d4 = find_next_delimiter(dtbuf, d3 + 1, DLEOS);
		if (d4 < 0)
			return rc;
		tz = atoi(&dtbuf[d3]);
	}

	if (tz == NO_TZ)
		tza = 0;
	else
		tza = abs(tz);
	if (h >= 0 && h < 24 && m >= 0 && m < 60 &&
			s >= 0 && s < 60 && tza < 2500 && (tza % 100) < 60) {
		hour = h;
		minute = m;
		second = s;
		tz_offset = tz;
		rc = 0;
	}
	return rc;
}
