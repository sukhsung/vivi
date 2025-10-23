/* Include file for the ADC-8x driver program */

#include <string.h>

#include <Arduino.h>
#include "board.h"
#include "ad7190.h"
#include "w25n02kv.h"
#include "pca9557.h"
#include "datetime.h"
#include "timed-delay.h"


/* Microcontroller registers */
extern Pm		* const pm;
extern Adc		* const adc0;
extern Dac		* const dac;
extern Gclk		* const gclk;
extern Sysctrl		* const sysctrl;
extern RtcMode0		* const rtc;
extern SercomI2cm	* const ser_i2c;
extern SercomSpi	* const ser_spi;
extern PortGroup	* const portA;
extern PortGroup	* const portB;
extern PortGroup	* const portAx;
extern PortGroup	* const portBx;
extern uint32_t		* const aux3;


/* General and utility items */
extern const char		version_str[];
extern char			buf[];	// General purpose printing buffer
extern volatile unsigned int	rtc_seconds;
			// RTC counter: seconds since 2000-03-01 00:00:00
extern int			tz_utc_offset;
extern bool			date_time_is_set;
extern int			num_adcs;

extern void		print_buf(void);
extern int		read_string(char *strbuf, int size,
		bool allow_whitespace);
extern unsigned int	read_utf8_string(char *dest, unsigned int max_bytes,
		bool consume_newline);

#define read_word(strbuf, size)		read_string(strbuf, size, false)
#define read_line(strbuf, size)		read_string(strbuf, size, true)


/* Pushbutton tracking */
struct pushbutton {
	unsigned long		state_time;	// Start of current state
	unsigned long		change_time;	// For debouncing
	bool			pressed;	// Current state
	bool			changed;	// For debouncing
	bool			long_press;
	bool			counting;
	uint8_t			multipress_count;
};

extern struct pushbutton		pb1;

#define PB_DEBOUNCE_THRESHOLD		50	// ms
#define PB_MULTIPRESS_THRESHOLD		500	// ms
#define PB_LONG_PRESS_THRESHOLD		1000	// ms
#define PB_MULTIPRESS_MAX		5

extern void		poll_pushbutton(void);


/* AD7190 data structures */
struct adc {
	uint32_t		nCS_pin_bit;
	uint8_t			working;
	uint8_t			running;
	uint8_t			gain;		// 1 - 128, 0 if not in use
	uint8_t			polarity;	// 1=unipolar, 2=bipolar
	uint8_t			buffered;	// 0 or 1
};

extern struct adc adcs[MAX_ADCS];

#define EXPT_TIME_MAX		100000		// Max seconds in an experiment

/* All four ADCs use the same output rate */
// Actual sampling rate is SAMPLING_MAX / rate_divisor
extern unsigned int	rate_divisor;		// 1 - 1023

extern bool		data_collection_in_progress;
extern int		num_running_adcs;
extern unsigned long	data_exp_time;
					// Expiration time for next sample
extern long		samples_remaining;
					// Number of samples remaining to collect


/* Serial communication ADC data structures */
struct channel_header {
	uint8_t		gain;		// 1 - 128, or 0 for not in use
	uint8_t		flags;

};
#define ch_flag_buffered	1
#define ch_flag_bipolar		2

struct output_header {
	uint8_t		sig[8];		// Signature string: "ADC8x-1."
	uint16_t	rate_div;	// Rate divisor: 2-byte little-endian
	struct channel_header	chans[MAX_ADCS];
};
#define SIGNATURE_STRING	"ADC8x-1."

/* 
 * Following the output header, the remaining data consists of buffers
 * each of which has a length byte followed by an array of blocks.
 * Each block consists of N 3-byte little-endian values, where N is the
 * number of ADCs in use.
 */

#define OUTPUT_BUF_SIZE		63	// Force USB packets to be short

extern uint8_t		output_data[OUTPUT_BUF_SIZE];
extern uint8_t		*pout;
extern uint8_t		const *output_limit;

/* ADC routines */
extern void		start_adcs_clock(void);
extern void		stop_adcs_clock(void);
extern int		gain_code(long v);
extern bool		time_expired(unsigned long exp_time);
extern bool		wait_for_nRDY(unsigned long exp_time);
extern void		init_adc(int i);
extern void		compute_mode_and_config(struct adc *adc,
		uint32_t *mode, uint32_t *config);
extern bool		set_up_adcs(bool start);
extern void		stop_adcs(void);
extern void		synchronize_adcs(void);
extern long		run_test(int i);
extern void		test_adcs_and_button(void);
extern void		measure_Rs(bool adjust_channels);
extern void		begin_data_collection(void);
extern void		continue_data_collection(void);


/* W25N02KV flash memory data structures */
extern uint32_t		w25_jedec_id;
extern uint8_t		w25_unique_id[W25_UNIQUE_ID_LEN];

#define MAX_ATTR_LEN		16	// Counting final NUL
#define NUM_ATTRS		3
extern uint8_t		attr_len[NUM_ATTRS];
extern char		attrs[NUM_ATTRS][MAX_ATTR_LEN];
extern const char	*attr_names[NUM_ATTRS];

extern unsigned int	block_end;	/* First unusable block number */

/*
 * We identify pages in the flash memory by information stored out-of-band
 * the data2 parts of the page's user area.
 */
struct oob_0 {				// Stored in the first sector_spare area
	uint8_t		marker;		// 0 for header page, 1 for data page
	uint8_t		expt_num[3];	// 24-bit experiment number
};

#define MAX_EXPT_NUM		9999999

struct oob_1 {				// Stored in the second sector_spare area
	uint16_t	page_len;	// Number of bytes in this page:
				// 2048 for all but the last page in a dataset
};

/* Flash memory routines */
extern void		init_flash_memory(void);
extern void		read_flash_unique_id_and_attrs(void);
extern void		scan_for_bad_blocks(void);
extern void		mark_bad_block(int blocknum);
extern void		scan_datasets(void);


/* PCA I2C expanders */
extern unsigned int	Rd_values;	// Current source & resistor selector bits

extern void		set_Rds(unsigned int packed_values);


/* SPI communications */
enum spi_type {
	SPI_ADC = 0, SPI_FLASH = 1,
};

extern void		enable_SPI(enum spi_type st);
extern void		disable_SPI(void);
extern void		enable_adc_CS(struct adc *adc);
extern void		disable_adc_CS(void);
extern void		enable_flash_CS(unsigned int flash_CS_pin_bit);
extern void		disable_flash_CS(void);
extern void		spi_send_byte(unsigned int val);
extern void		spi_send_3(unsigned int val);
extern unsigned int	spi_read_byte(void);
extern void		spi_send_buffer(const uint8_t *buffer, unsigned int len);
extern void		spi_read_buffer(uint8_t *buffer, unsigned int len);
extern unsigned int	spi_xfer(unsigned int opcode, const char *args, ...);


/* I2C communications */
#define ETIMEOUT	(-1)
#define ENOACK		(-2)
#define EOTHER		(-3)
#define EWRONGID	(-4)
#define ECRC		(-5)

extern bool	led_i2c_expander_present;	// Front panel chip is present
extern bool	Rd_i2c_expander_present;	// Onboard chip is present
extern bool	RdDB_i2c_expander_present;	// Daughterboard chip is present

extern void	i2c_start(int address);
extern void	i2c_stop(void);
extern int	i2c_raw_write(void *wbuf, unsigned int len);
extern int	i2c_write_reg(uint8_t reg, uint8_t value);

extern void	set_channel_status_leds(unsigned int leds);
extern void	show_channel_gain_leds(void);
