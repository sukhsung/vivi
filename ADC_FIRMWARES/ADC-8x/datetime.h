/* Date and time manipulation */

/* Ignores Daylight Saving Time changes and leap seconds */

class Date_time {
 public:
	uint16_t	year;		// 2000 - 2136
	uint8_t		month, day, hour, minute, second;
	int16_t		tz_offset;

	// The epoch is 2000-03-01 00:00:00
	static const unsigned int	EPOCH_YEAR = 2000;
	static const int		NO_TZ = 19999;

	unsigned int	get_seconds(void);
	unsigned int	get_time_seconds(void);
	void		set_seconds(unsigned int s);
	void		format(char *buffer);		// Length >= 28
	void		format_time(char *buffer);	// Length >= 12
	int		parse_date(const char *dtbuf);
	int		parse_time(const char *dtbuf, bool allow_tz = false);

	static char	buffer[32];

	Date_time(void) : tz_offset(NO_TZ) { }
};
