/* Driver for the ADC-8 quad 24-bit delta-sigma ADC board */

#include <Arduino.h>

const char	id_string[] = "ADC-8 driver version 5";

#define REFERENCE_VOLTAGE	2500		// mV

#define SCK_PIN_BIT		PORT_PB11	// SCK
#define MOSI_PIN_BIT		PORT_PB10	// MOSI
#define MISO_PIN_BIT		PORT_PA12	// MISO

#define CS1_PIN_BIT		PORT_PA19	// d12
#define CS2_PIN_BIT		PORT_PA18	// d10
#define CS3_PIN_BIT		PORT_PA17	// d13
#define CS4_PIN_BIT		PORT_PA16	// d11

#define nSYNC_PIN_BIT		PORT_PA05	// A4
#define CLOCK_PIN_BIT		PORT_PA04	// A3

#define DAC_PIN_BIT		PORT_PA02	// A0
#define VREF_PIN_BIT		PORT_PA03	// ARef

#define Vc_0V_PIN_BIT		PORT_PA07	// d9
#define EnVc_PIN_BIT		PORT_PA15	// d5

#define DEBUG_PIN_BIT		PORT_PA11	// Rx0
#define DEBUG_ON()		PORT_IOBUS->Group[0].OUTSET.reg = DEBUG_PIN_BIT
#define DEBUG_OFF()		PORT_IOBUS->Group[0].OUTCLR.reg = DEBUG_PIN_BIT

/* Definitions for the AD7190 A/D converter chip */
#define CR_nWEN			(1 << 7)	// Write (dis)able bit
#define CR_RnW			(1 << 6)	// Read/write bit
// Bits 3-5 for register selection
#define CR_CREAD		(1 << 2)	// Continuous read of data reg.
// Bits 0-1 not used

/* Register selection */
#define REG_STATUS		(0 << 3)	// Status register (for read)
#define REG_MODE		(1 << 3)	// Mode register
#define REG_CONFIGURATION	(2 << 3)	// Configuration register
#define REG_DATA		(3 << 3)	// Data (+ status) register
#define REG_ID			(4 << 3)	// ID register
#define REG_GPOCON		(5 << 3)	// GP outputl control register
#define REG_OFFSET		(6 << 3)	// Offset calibration register
#define REG_FULL_SCALE		(7 << 3)	// Full-scale calibration reg

/* Status register */
#define	SR_nRDY			(1 << 7)	// Ready
#define SR_ERR			(1 << 6)	// ADC error
#define SR_NOREG		(1 << 5)	// No external reference
#define SR_PARITY		(1 << 4)	// Parity check for data
// Bit 3 not used
#define SR_CH_MASK		0x07		// Channel mask

/* Mode register */
// Bits 21-23 for mode selection
#define MR_DAT_STA		(1 << 20)	// Data with status
// Bits 18-19 for clock source selection
// Bits 16-17 not used
#define MR_SINC3		(1 << 15)	// Sinc^3 filter selection
// Bit 14 not used
#define MR_ENPAR		(1 << 13)	// Enable parity
// Bit 12 not used
#define MR_SINGLE		(1 << 11)	// Single-cycle conversion
#define MR_REJ60		(1 << 10)	// 60-Hz rejection filter notch
#define MR_FSMASK		0x03ff		// filter output data rate mask

/* Mode selection */
#define MODE_CONTINUOUS		(0 << 21)	// Continuous conversion mode
#define MODE_SINGLE		(1 << 21)	// Single conversion mode
#define MODE_IDLE		(2 << 21)	// Idle mode
#define MODE_POWER_DOWN		(3 << 21)	// Power-down mode
#define MODE_INT_ZERO		(4 << 21)	// Internal zero-scale calib.
#define MODE_INT_FULL		(5 << 21)	// Internal full-scale calib.
#define MODE_SYS_ZERO		(6 << 21)	// System zero-scale calibration
#define MODE_SYS_FULL		(7 << 21)	// System full-scale calibration

/* Clock source selection */
#define CLK_CRYSTAL		(0 << 18)	// External crystal clock
#define CLK_CLOCK		(1 << 18)	// External clock
#define CLK_INTERNAL		(2 << 18)	// Internal 4.92 MHz clock
#define CLK_INT_MCLK2		(3 << 18)	// Internal clock on MCLK2 pin

#define SAMPLING_MAX		4800		// Max sampling rate

/* Configuration register */
#define CON_CHOP		(1 << 23)	// Chop enable
// Bits 21-22 not used
#define CON_REFSEL		(1 << 20)	// Reference source selection
// Bits 16-19 not used
// Bits 8-15 for channel selection
#define CON_BURN		(1 << 7)	// Burnout current enable
#define CON_REFDET		(1 << 6)	// Reference detect enable
// Bit 5 not used
#define CON_BUF			(1 << 4)	// Buffered input enable
#define CON_UnB			(1 << 3)	// Unipolar/Bipolar select
// Bits 0-2 for gain selection

/* Channel selection */
#define CHAN_1_2		(1 << 8)	// AIN1 - AIN2
#define CHAN_3_4		(1 << 9)	// AIN3 - AIN4
#define CHAN_TEMP		(1 << 10)	// Temperature sensor
#define CHAN_2_2		(1 << 11)	// AIN2 - AIN2 ???
#define CHAN_1			(1 << 12)	// AIN1 - AINCOM
#define CHAN_2			(1 << 13)	// AIN2 - AINCOM
#define CHAN_3			(1 << 14)	// AIN3 - AINCOM
#define CHAN_4			(1 << 15)	// AIN4 - AINCOM

/* Gain selection */
#define GAIN_1			0
// 1 - 2 reserved
#define GAIN_8			3
#define GAIN_16			4
#define GAIN_32			5
#define GAIN_64			6
#define GAIN_128		7

/* Data register */
#define NUM_DATA_BITS		24

/* ID register */
#define ID_MASK			0x0f
#define ID_VALUE		0x04

/* GPOCON and calibration registers ignored */

#define ADC_RESET_LEN		5		// Reset is 40 bits all high

/* Description of a single AD7190 */
struct adc {
	uint32_t		CS_pin_bit;
	uint8_t			working;
	uint8_t			running;
	uint8_t			gain;		// 1 - 128, 0 if not in use
	uint8_t			polarity;	// 1=unipolar, 2=bipolar
	uint8_t			buffered;	// 0 or 1
};

#define NUM_ADCS	4
struct adc adcs[NUM_ADCS] = {
	{ CS1_PIN_BIT, 0, 0, 1, 2, 0},
	{ CS2_PIN_BIT, 0, 0, 1, 2, 0},
	{ CS3_PIN_BIT, 0, 0, 1, 2, 0},
	{ CS4_PIN_BIT, 0, 0, 1, 2, 0},
};

/* All four ADCs use the same output rate and filter choice */
// Actual sampling rate is SAMPLING_MAX / rate_divisor
unsigned int		rate_divisor = SAMPLING_MAX / 50;	// 1 - 1023
unsigned int		sinc_order = 4;				// 3 or 4

/* Output data structures */
struct channel_header {
	uint8_t		gain;		// 1 - 128, or 0 for not in use
	uint8_t		flags;

};
#define ch_flag_buffered	1
#define ch_flag_bipolar		2

struct output_header {
	uint8_t		sig[4];		// Signature string: "ADC8"
	uint16_t	rate_div;	// Rate divisor: 2-byte little-endian
	uint8_t		order;		// Sinc filter order: 3 or 4
	uint8_t		unused;		// For alignment
	struct channel_header	chans[NUM_ADCS];
};
#define SIGNATURE_STRING	"ADC8"

/* 
 * Following the output header, the remaining data consists of buffers
 * each of which has a length byte followed by an array of blocks.
 * Each block consists of N 3-byte little-endian values, where N is the
 * number of ADCs in use.
 */
#define OUTPUT_BUF_SIZE		63	// Force USB packets to be short
uint8_t		output_data[OUTPUT_BUF_SIZE];
uint8_t		*pout;
uint8_t		const *output_limit;

bool		data_collection_in_progress;
int		num_running_adcs;
unsigned long	data_exp_time;		// Expiration time for next sample
unsigned long	second_exp_time;	// Expiration time for next second
unsigned long	run_exp_seconds;	// Number of seconds remaining to run

bool		Vc_0V_setting;		// True => Vc = 0, False => Vc = Vc-bias
bool		EnVc_setting;		// True => enabled
unsigned int	dac_value;		// 10-bit DAC data value
uint32_t	serial_number[4];
char		buf[80];		// General purpose printing buffer

void print_id(void)
{
	sprintf(buf, "%s   %08lx-%08lx-%08lx-%08lx\n", id_string,
			serial_number[0], serial_number[1],
			serial_number[2], serial_number[3]);
	Serial.print(buf);
}

int gain_code(long v)
{
	/* Return the GAIN bits corresponding to v, or -1 for invalid value */
	switch (v) {
	case 1:
		return GAIN_1;
	case 8:
		return GAIN_8;
	case 16:
		return GAIN_16;
	case 32:
		return GAIN_32;
	case 64:
		return GAIN_64;
	case 128:
		return GAIN_128;
	}
	return -1;
}

bool time_expired(unsigned long exp_time)
{
	unsigned long		cur_time;

	cur_time = millis();
	return (long) (cur_time - exp_time) >= 0;
}

bool wait_for_nRDY(unsigned long exp_time)
{
	static PortGroup	* const portAx = &PORT->Group[0];
	bool			rc = true;

	while (portAx->IN.reg & MISO_PIN_BIT) {		// nRDY is high
		if (time_expired(exp_time)) {
			rc = false;
			break;
		}
	}

	return rc;
}

void enable_CS(struct adc *adc)
{
	static PortGroup	* const portA = &PORT_IOBUS->Group[0];

	/* Disable all the CS lines for safety */
	portA->OUTSET.reg = CS1_PIN_BIT | CS2_PIN_BIT | CS3_PIN_BIT |
			CS4_PIN_BIT;

	/* Enable the CS line for the ADC */
	portA->OUTCLR.reg = adc->CS_pin_bit;
}

void disable_CS(void)
{
	static PortGroup	* const portA = &PORT_IOBUS->Group[0];

	/* Disable all the CS lines */
	portA->OUTSET.reg = CS1_PIN_BIT | CS2_PIN_BIT | CS3_PIN_BIT |
			CS4_PIN_BIT;
}

void spi_send_byte(unsigned int val)
{
	static SercomSpi	* const sercom4 = &SERCOM4->SPI;

	sercom4->DATA.reg = val;
	while (sercom4->INTFLAG.bit.RXC == 0)
		;			// Wait for data to arrive
	(void) sercom4->DATA.reg;	// Throw it away
}

void spi_send_3(unsigned int val)
{
	/* Send the data bytes in big-endian order */
	spi_send_byte(val >> 16);
	spi_send_byte(val >> 8);
	spi_send_byte(val);
}

unsigned int spi_read_byte(void)
{
	static SercomSpi	* const sercom4 = &SERCOM4->SPI;

	sercom4->DATA.reg = 0;	// Keep the data line low to avoid reset
	while (sercom4->INTFLAG.bit.RXC == 0)
		;		// Wait for data to arrive
	return sercom4->DATA.reg;
}

void init_adc(int i)
{
	static PortGroup	* const portA = &PORT_IOBUS->Group[0];
	struct adc		*adc = &adcs[i];
	int			n;
	unsigned int		val;
	char			buf[64];

	i += 1;

	enable_CS(adc);

	/* Reset the ADC */
	for (n = 0; n < ADC_RESET_LEN; ++n)
		spi_send_byte(0xFF);
	adc->running = 0;

	/* Wait for the ADC to reset itself */
	delay(1);
	portA->OUTSET.reg = DEBUG_PIN_BIT;

	/* Try to read the ID register */
	spi_send_byte(CR_RnW | REG_ID);		// Read the ID register
	val = spi_read_byte();			// Read the register value

	/* Put the ADC into idle mode */
	spi_send_byte(REG_MODE);		// Write the Mode register
	spi_send_3(MODE_IDLE + CLK_CLOCK + 1);	// Send the mode value

	disable_CS();

	if ((val & ID_MASK) == ID_VALUE) {
		sprintf(buf, "ADC %d ID value: %02x\n", i, val);
		adc->working = 1;
		adc->gain = 1;
	} else {
		sprintf(buf, "ADC %d sent invalid ID value: %02x\n", i, val);
		adc->working = 0;
		adc->gain = 0;
	}
	Serial.print(buf);
}

void compute_mode_and_config(struct adc *adc, uint32_t *mode, uint32_t *config)
{
	/* Set up the mode and configuration register values */
	// Mode selection made later
	// Don't get the status
	*mode = CLK_CLOCK;
	if (sinc_order == 3)
		*mode += MR_SINC3;
	// No parity, zero-latency, or 60-Hz rejection
	*mode += rate_divisor;

	// No chop
	// Reference is between REFIN1(+) and REFIN1(-)
	*config = CHAN_1_2;
	// No burnout current or reference detection
	if (adc->buffered)
		*config += CON_BUF;
	if (adc->polarity == 1)
		*config += CON_UnB;
	*config += gain_code(adc->gain);
}

bool set_up_adcs(bool start)
{
	bool			rc = true;
	int			i;
	struct adc		*adc;
	uint32_t		mode, config;
	unsigned long		exp_time;

	for (i = 0; i < NUM_ADCS; ++i) {
		adc = &adcs[i];
		if (!adc->working || adc->gain == 0)
			continue;

		compute_mode_and_config(adc, &mode, &config);
		enable_CS(adc);

		/* Send the configuration information */
		spi_send_byte(REG_CONFIGURATION);	// Write the Config reg
		spi_send_3(config);

		/* Carry out an internal calibration */
		exp_time = millis() + 1000;
		spi_send_byte(REG_MODE);		// Write the Mode reg
		spi_send_3(mode + MODE_INT_ZERO);	// Zero-scale calib
		if (!wait_for_nRDY(exp_time))
			goto timed_out;

		exp_time = millis() + 1000;
		spi_send_byte(REG_MODE);		// Write the Mode reg
		spi_send_3(mode + MODE_INT_FULL);	// Full-scale calib
		if (!wait_for_nRDY(exp_time)) {
 timed_out:
			Serial.print("ADC ");
			Serial.print(i + 1);
			Serial.print(" timed out during calibration!\n");
			rc = false;
		}

		if (start && rc) {

			/* Start the continuous conversions */
			spi_send_byte(REG_MODE);	// Write the Mode reg
			spi_send_3(mode + MODE_CONTINUOUS);

			/* Begin continuous reading of the Data register */
			spi_send_byte(CR_RnW + REG_DATA + CR_CREAD);
			adc->running = 1;
		}

		disable_CS();
	}
	return rc;
}

void stop_adcs(void)
{
	int			i;
	struct adc		*adc;
	unsigned long		exp_time;

	for (i = 0; i < NUM_ADCS; ++i) {
		adc = &adcs[i];
		if (!adc->running)
			continue;

		enable_CS(adc);
		exp_time = millis() + 1000;

		if (wait_for_nRDY(exp_time)) {

			/* Exit the continuous-read mode */
			spi_send_byte(CR_RnW + REG_DATA);
		}
		// If the ADC times out, it needs to be reset

		/* Try to go into idle mode */
		spi_send_byte(REG_MODE);	// Write the Mode register
		spi_send_3(MODE_IDLE + CLK_CLOCK + 1);

		disable_CS();
		adc->running = 0;
	}
}

void synchronize_adcs(void)
{
	static PortGroup	* const portA = &PORT_IOBUS->Group[0];
	static PortGroup	* const portAx = &PORT->Group[0];

	/* Set the nSYNC pin low, then high on a CLOCK rising edge */
	portA->OUTCLR.reg = nSYNC_PIN_BIT;

	noInterrupts();		// Delicate timing here
	delayMicroseconds(1);
	while (!(portAx->IN.reg & CLOCK_PIN_BIT))	// Wait for CLOCK high
		;
	while (portAx->IN.reg & CLOCK_PIN_BIT)		// Wait for falling edge
		;
	portA->OUTSET.reg = nSYNC_PIN_BIT;	// nSYNC high after rising edge
	interrupts();
}

long run_test(int i)
{
	struct adc		*adc;
	uint32_t		mode, config;
	unsigned long		exp_time;
	unsigned int		v1, v2, v3;
	long			v;

	adc = &adcs[i];
	compute_mode_and_config(adc, &mode, &config);
	enable_CS(adc);

	/* Carry out a single conversion */
	exp_time = millis() + 1000;
	spi_send_byte(REG_MODE);			// Write the Mode reg
	spi_send_3(mode + MODE_SINGLE);			// Single conversion

	if (!wait_for_nRDY(exp_time)) {
		sprintf(buf, "ADC %d timed out during A/D conversion!\n", i + 1);
		Serial.print(buf);
		v = -1;
	} else {
		spi_send_byte(CR_RnW + REG_DATA);	// Read the Data reg
		v1 = spi_read_byte();			// 3 bytes, big-endian
		v2 = spi_read_byte();
		v3 = spi_read_byte();
		v = (v1 << 16) + (v2 << 8) + v3;
	}

	disable_CS();
	return v;
}

void continue_data_collection(void)
{
	static PortGroup	* const portAx = &PORT->Group[0];
	int			i;
	struct adc		*adc;
	uint8_t			*p;

	buf[0] = 0;
	if (Serial.peek() >= 0)
		goto abort;

	if (run_exp_seconds > 0) {
		if (time_expired(second_exp_time)) {
			if (--run_exp_seconds == 0)
				goto abort;
			second_exp_time += 1000;
		}
	}

	p = pout;
	for (i = 0; i < NUM_ADCS; ++i) {
		adc = &adcs[i];
		if (!adc->running)
			continue;

		enable_CS(adc);

		/* Continue to check for abort while waiting for nRDY */
		while (portAx->IN.reg & MISO_PIN_BIT) {		// nRDY is high
			if (Serial.peek() >= 0)
				goto abort;
			if (time_expired(data_exp_time)) {
				sprintf(buf, "\nADC %d timed out!", i - 1);
				goto abort;
			}
		}

		/* Read and store the Data register value, swapping bytes */
		p[2] = spi_read_byte();
		p[1] = spi_read_byte();
		p[0] = spi_read_byte();
		p += 3;

		disable_CS();
	}
	pout = p;

	if (pout > output_limit) {
		i = pout - output_data;
		output_data[0] = i - 1;
		Serial.write(output_data, i);
		pout = output_data + 1;
	}
	data_exp_time = millis() + 1000;
	return;

 abort:
	disable_CS();
	data_collection_in_progress = false;

	/* Send possible partial buffer and termination byte */
	i = pout - output_data;
	if (i > 1) {
		output_data[0] = i - 1;
		Serial.write(output_data, i);
	}
	Serial.write((uint8_t) 0);
	
	Serial.print(buf);
	Serial.print("\nData collection stopped\n");

	stop_adcs();
}

void setup(void)
{
	static Pm		* const pm = PM;
	static Dac		* const dac = DAC;
	static Gclk		* const gclk = GCLK;
	static SercomSpi	* const sercom4 = &SERCOM4->SPI;
	static PortGroup	* const portA = &PORT_IOBUS->Group[0];
	static PortGroup	* const portB = &PORT_IOBUS->Group[1];
	static PortGroup	* const portAx = &PORT->Group[0];
	static PortGroup	* const portBx = &PORT->Group[1];
	uint32_t		* const aux3 =
			(uint32_t *) NVMCTRL_AUX3_ADDRESS;
	int			i;

	/* Set the output pins HIGH (MISO too for pull-up, but not DAC) */
	/* Also not Vc_0V and EnVc */
	portA->OUTSET.reg = MISO_PIN_BIT | CS1_PIN_BIT | CS2_PIN_BIT |
			CS3_PIN_BIT | CS4_PIN_BIT | nSYNC_PIN_BIT;
	portB->OUTSET.reg = SCK_PIN_BIT | MOSI_PIN_BIT;

	/* Set the appropriate pins to be outputs */
	portA->DIRSET.reg = CS1_PIN_BIT | CS2_PIN_BIT |
			CS3_PIN_BIT | CS4_PIN_BIT | nSYNC_PIN_BIT |
			DAC_PIN_BIT | Vc_0V_PIN_BIT | EnVc_PIN_BIT |
			DEBUG_PIN_BIT;
	portB->DIRSET.reg = SCK_PIN_BIT | MOSI_PIN_BIT;

	/* Enable input on the CLOCK pin and turn on continuous sampling */
	portAx->WRCONFIG.reg = PORT_WRCONFIG_WRPINCFG |
			PORT_WRCONFIG_INEN |
			PORT_WRCONFIG_PINMASK(CLOCK_PIN_BIT);
	portAx->CTRL.reg = CLOCK_PIN_BIT;

	/* Enable the APB bus clock for SERCOM 4 and the DAC */
	pm->APBCMASK.reg |= PM_APBCMASK_SERCOM4 | PM_APBCMASK_DAC;

	/* Set up SERCOM 4's generic clock */
	gclk->CLKCTRL.reg = GCLK_CLKCTRL_ID_SERCOM4_CORE;	// Disable
	gclk->CLKCTRL.reg = GCLK_CLKCTRL_ID_SERCOM4_CORE |
			GCLK_CLKCTRL_GEN_GCLK0 | 	// Gen 0 is 48 MHz
			GCLK_CLKCTRL_CLKEN;

	/* Set up DAC's generic clock */
	gclk->CLKCTRL.reg = GCLK_CLKCTRL_ID_DAC;	// Disable
	gclk->CLKCTRL.reg = GCLK_CLKCTRL_ID_DAC |
			GCLK_CLKCTRL_GEN_GCLK0 | 	// Gen 0 is 48 MHz
			GCLK_CLKCTRL_CLKEN;
	while (gclk->STATUS.bit.SYNCBUSY)
		;	// Wait for synchronization

	/* Configure the SERCOM4 peripheral for SPI */
	sercom4->CTRLA.reg =				// MSB first
			SERCOM_SPI_CTRLA_CPOL |		// Clock mode 3:
			SERCOM_SPI_CTRLA_CPHA |
				// clock is idle high, sampled on rising edge
							// No address in frame
			SERCOM_SPI_CTRLA_DIPO(0) |	// Pad 0 (PA12) is MISO
			SERCOM_SPI_CTRLA_DOPO(1) |	// Pad 2 (PB10) is MOSI
							// Pad 3 (PB11) is SCK
			SERCOM_SPI_CTRLA_MODE_SPI_MASTER;
							// No enable yet

	sercom4->CTRLB.reg = SERCOM_SPI_CTRLB_RXEN |	// Enable the receiver
							// SS control disabled
			SERCOM_SPI_CTRLB_CHSIZE(0);	// 8-bit data

	/*
	 * SPI uses synchronous communication.  The clock frequency is
	 * given by: BAUD = fREF / (2 * fBAUD) - 1 = 11 (table 25-2),
	 * where fREF is the 48-MHz generic clock and we want fBAUD
	 * to be 2 MHz.
	 */
	sercom4->BAUD.reg = 11;

	sercom4->CTRLA.bit.ENABLE = 1;
	while (sercom4->SYNCBUSY.reg & SERCOM_SPI_SYNCBUSY_MASK)
		;		// Wait for enable and receiver enable

	/* Set SCK and MOSI pins to peripheral D (SERCOM-ALT) */
	portBx->WRCONFIG.reg = PORT_WRCONFIG_WRPINCFG |
			PORT_WRCONFIG_WRPMUX |
			PORT_WRCONFIG_PMUX(PORT_PMUX_PMUXE_D_Val) |
			PORT_WRCONFIG_PMUXEN |
			PORT_WRCONFIG_PINMASK(SCK_PIN_BIT | MOSI_PIN_BIT);

	/* Set the MISO pin to peripheral D (SERCOM-ALT) */
	portAx->WRCONFIG.reg = PORT_WRCONFIG_WRPINCFG |
			PORT_WRCONFIG_WRPMUX |
			PORT_WRCONFIG_PMUX(PORT_PMUX_PMUXE_D_Val) |
			PORT_WRCONFIG_PMUXEN |
			PORT_WRCONFIG_PINMASK(MISO_PIN_BIT);

	/* Start up the DAC */
	dac->CTRLB.reg = DAC_CTRLB_REFSEL_VREFP |	// VREFA is reference
			DAC_CTRLB_VPD |		// Disable voltage pump
						// Registers are right-adjusted
			DAC_CTRLB_EOEN;		//  outputs needed for ADC

	dac->CTRLA.reg = DAC_CTRLA_ENABLE;	// Enable the DAC
	while (dac->STATUS.bit.SYNCBUSY)
		;	// Wait for the enable

	/* Set the output voltage level */
	dac->DATA.reg = DAC_DATA_DATA(0);

	/* Switch the DAC and VREF pins to peripheral B (analog) */
	portAx->WRCONFIG.reg = PORT_WRCONFIG_WRPINCFG |	// Write pin config
			PORT_WRCONFIG_WRPMUX |
			PORT_WRCONFIG_PMUX(PORT_PMUX_PMUXE_B_Val) |
					// Pullup and input disabled
			PORT_WRCONFIG_PMUXEN |
			PORT_WRCONFIG_PINMASK(DAC_PIN_BIT | VREF_PIN_BIT);

	/*
	 * The serial number is a 128-bit value distributed among four 32-bit
	 * words in the AUX3 area.
	 */
	serial_number[0] = aux3[3];
	serial_number[1] = aux3[16];
	serial_number[2] = aux3[17];
	serial_number[3] = aux3[18];

	/* Initialize the USB link */
	Serial.begin(9600);
	Serial.setTimeout(0);

	while (!Serial)		// Wait for an open connection
		;
	delay(500);
	Serial.print("\n\n");
	print_id();
	/* Reset and query all the ADCs */
	for (i = 0; i < NUM_ADCS; ++i)
		init_adc(i);
}

int get_next_nonspace(void)
{
	int		c;

	for (;;) {
		c = Serial.peek();
		if (c < 0 || c == '\n')
			return 0;
		Serial.read();
		if (c > ' ')
			break;
	}
	return c;
}

void skip_to_eol(void)
{
	int		c;

	for (;;) {
		c = Serial.peek();
		if (c < 0)
			break;
		Serial.read();
		if (c == '\n')
			break;
	}
}

void show_current_settings(void)
{
	int		i;
	unsigned int	x;
	struct adc	*adc;
	char		*p;

	sprintf(buf, "\nCurrent settings:  Sampling rate %.2f, sinc filter order %d\n",
			SAMPLING_MAX / (float) rate_divisor,
			sinc_order);
	Serial.print(buf);

	for (i = 0; i < NUM_ADCS; ++i) {
		adc = &adcs[i];
		p = buf;
		p += sprintf(p, "ADC %d: ", i + 1);
		if (!adc->working) {
			sprintf(p, "not working\n");
		} else if (adc->gain == 0) {
			sprintf(p, "disabled\n");
		} else {
			p += sprintf(p, "gain %d, %spolar, %sbuffered\n",
					adc->gain,
					(adc->polarity == 1 ? "uni" : "bi"),
					(adc->buffered ? "" : "un"));
		}
		Serial.print(buf);
	}

	x = (dac_value * REFERENCE_VOLTAGE + 512) / 1024;
	sprintf(buf, "DAC output voltage set to %u mV\n", x);
	Serial.print(buf);
	sprintf(buf, "Vc bias setting: %d   EnVc setting: %d\n",
			!Vc_0V_setting, EnVc_setting);
	Serial.print(buf);
}

void show_current_settings_fixed_format(void)
{
	int		i;
	unsigned int	dac_voltage_mv;
	struct adc	*adc;

	dac_voltage_mv = (dac_value * REFERENCE_VOLTAGE + 512) / 1024;
	sprintf(buf, "%.3f,%u,%d,%d,%d\n",
			SAMPLING_MAX / (float) rate_divisor,
			dac_voltage_mv,
			EnVc_setting,
			!Vc_0V_setting,
			0);
	Serial.print(buf);

	for (i = 0; i < NUM_ADCS; ++i) {
		adc = &adcs[i];
		sprintf(buf, "%d,%d,%d,%d\n",
				adc->gain,
				adc->polarity,
				adc->buffered,
				0);
		Serial.print(buf);
	}
	for (; i < 8; ++i)	// No daughterboard support
		Serial.print("0,2,0,0\n");
}

void set_dac_voltage(void)
{
	static Dac		* const dac = DAC;
	long			v;
	unsigned int		x;

	v = Serial.parseInt();
	if (v < 0 || v > REFERENCE_VOLTAGE) {
		sprintf(buf, "Invalid DAC voltage: %ld\n", v);
		Serial.print(buf);
		return;
	}

	/* Convert to a 10-bit output value and write to the DAC */
	x = (1024 * v + REFERENCE_VOLTAGE / 2) / REFERENCE_VOLTAGE;
	x = min(x, 1023);
	dac->DATA.reg = dac_value = x;

	x = (x * REFERENCE_VOLTAGE + 512) / 1024;
	sprintf(buf, "DAC output voltage set to %u mV\n", x);
	Serial.print(buf);
}

void parse_gain(void)
{
	int		b, g, i;
	long		chan, v1, v2;
	bool		settings_okay;
	struct adc	*adc;
	char		*p;

	chan = Serial.parseInt();
	v1 = Serial.parseInt();
	v2 = Serial.parseInt();
	b = get_next_nonspace();

	settings_okay = false;
	if (v1 == 0)
		g = 999;
	else
		g = gain_code(v1);

	if (chan < 0 || chan > NUM_ADCS)
		sprintf(buf, "Invalid ADC number: %ld\n", chan);
	else if (chan > 0 && !adcs[chan - 1].working)
		sprintf(buf, "ADC %ld is not working\n", chan);
	else if (g < 0)
		sprintf(buf, "Invalid gain setting: %ld\n", v1);
	else if (v2 < 0 || v2 > 2)
		sprintf(buf, "Invalid polarity setting: %ld\n", v2);
	else if (!(b == 0 || b == 'b' || b == 'u'))
		sprintf(buf, "Invalid buffer selection: %c\n", b);
	else
		settings_okay = true;
	if (!settings_okay) {
		Serial.print(buf);
		return;
	}

	for (i = 0; i < NUM_ADCS; ++i) {
		if (chan == 0 || i + 1 == chan) {
			adc = &adcs[i];
			if (!adc->working)
				continue;
			adc->gain = v1;
			if (v2)
				adc->polarity = v2;
			if (b)
				adc->buffered = (b == 'b');
		}
	}

	p = buf;
	if (chan == 0)
		p += sprintf(p, "All ADCs ");
	else
		p += sprintf(p, "ADC %ld ", chan);
	if (v1 == 0) {
		sprintf(p, "disabled\n");
	} else {
		p += sprintf(p, "set to gain %ld, ", v1);
		if (v2 == 0)
			p += sprintf(p, "polarity unchanged, ");
		else
			p += sprintf(p, "polarity %ld (%spolar), ", v2,
					(v2 == 1 ? "uni" : "bi"));
		if (b == 0)
			sprintf(p, "buffer unchanged\n");
		else
			sprintf(p, "%sbuffered\n", (b == 'b' ? "" : "un"));
	}
	Serial.print(buf);
}

void parse_sampling(void)
{
	long		v1, v2;
	char		*p;

	v1 = Serial.parseInt();
	v2 = Serial.parseInt();

	if (v1 <= 0 || v1 > SAMPLING_MAX) {
		sprintf(buf, "Invalid sampling rate: %ld\n", v1);
	} else if (!(v2 == 0 || v2 == 3 || v2 == 4)) {
		sprintf(buf, "Invalid sinc filter order: %ld\n", v2);
	} else {
		rate_divisor = min(SAMPLING_MAX / v1, MR_FSMASK);
		if (v2)
			sinc_order = v2;

		p = buf;
		p += sprintf(p, "Sampling rate set to %.2f Hz",
				SAMPLING_MAX / (float) rate_divisor);
		p += sprintf(p, " sinc filter order ");
		if (v2)
			sprintf(p, "set to %u\n", sinc_order);
		else
			sprintf(p, "unchanged\n");
	}
	Serial.print(buf);
}

void parse_vc(void)
{
	static PortGroup	* const portA = &PORT_IOBUS->Group[0];
	int			i, j;

	i = Serial.parseInt();
	j = Serial.parseInt();

	Vc_0V_setting = (i == 0);
	EnVc_setting = j;

	if (Vc_0V_setting)
		portA->OUTSET.reg = Vc_0V_PIN_BIT;
	else
		portA->OUTCLR.reg = Vc_0V_PIN_BIT;
	if (EnVc_setting)
		portA->OUTSET.reg = EnVc_PIN_BIT;
	else
		portA->OUTCLR.reg = EnVc_PIN_BIT;

	sprintf(buf, "Vc bias setting: %d   EnVc setting: %d\n",
			!Vc_0V_setting, EnVc_setting);
	Serial.print(buf);
}

void test_adcs(void)
{
	int		i;
	struct adc	*adc;
	long		v;
	float		x;

	Serial.print("\nTest reading\n");

	if (!set_up_adcs(false))
		return;

	for (i = 0; i < NUM_ADCS; ++i) {
		adc = &adcs[i];
		if (!adc->working || adc->gain == 0)
			continue;

		v = run_test(i);
		x = v / (float) (1 << NUM_DATA_BITS);
		if (adc->polarity == 2)
			x = 2.0f * x - 1.0f;
		// Include 2% correction in the voltage value
		x *= (1.02 * REFERENCE_VOLTAGE) / adc->gain;

		sprintf(buf, "ADC %d: value %.6f mV  (%ld)\n",
				i + 1, x, v);
		Serial.print(buf);
	}
}

void begin_data_collection(void)
{
	long			t;
	int			i;
	struct adc		*adc;
	struct output_header	hdr;

	t = Serial.parseInt();
	if (t < 0)
		t = 0;

	/* Set up the output header */
	memset(&hdr, 0, sizeof(hdr));
	memcpy(hdr.sig, SIGNATURE_STRING, sizeof(hdr.sig));
	hdr.rate_div = rate_divisor;
	hdr.order = sinc_order;

	num_running_adcs = 0;
	for (i = 0; i < NUM_ADCS; ++i) {
		adc = &adcs[i];
		if (!adc->working)
			adc->gain = 0;
		hdr.chans[i].gain = adc->gain;
		if (adc->gain)
			++num_running_adcs;
		hdr.chans[i].flags = adc->buffered + (adc->polarity & 2);
	}

	if (num_running_adcs == 0) {
		Serial.print("No active ADCs!  Data collection aborted\n");
		goto abort;
	}
	sprintf(buf, "\nNumber of active ADCs: %d\n", num_running_adcs);
	Serial.print(buf);

	if (!set_up_adcs(true)) {
		stop_adcs();
		goto abort;
	}

	Serial.print("Beginning data collection...\n+");
	Serial.write((uint8_t *) &hdr, sizeof(hdr));

	pout = output_data + 1;
	output_limit = &output_data[OUTPUT_BUF_SIZE - num_running_adcs * 3];
	data_collection_in_progress = true;

	synchronize_adcs();
	run_exp_seconds = t;
	second_exp_time = millis() + 1000;
	data_exp_time = second_exp_time + 1000;
	return;

 abort:
	Serial.print("+-\n");
}

void loop(void)
{
	int		c, i;

	if (data_collection_in_progress) {
		continue_data_collection();
		return;
	}

	c = Serial.read();
	if (c <= ' ')		// Skip whitespace
		return;

	switch (c) {
	case '*':	/* Identify myself */
		print_id();
		break;

	case 'b':	/* Begin data collection */
		begin_data_collection();
		break;

	case 'c':	/* Show the settings */
		show_current_settings();
		break;

	case 'd':	/* Set DAC bias voltage output */
		set_dac_voltage();
		break;

	case 'g':	/* Gain and other individual settings */
		parse_gain();
		break;

	case 'r':	/* Reset all ADCs */
		Serial.print("\nReset all ADCs...\n");
		for (i = 0; i < NUM_ADCS; ++i)
			init_adc(i);
		break;

	case 's':	/* Sampling rate and sinc filter order */
		parse_sampling();
		break;

	case 't':	/* Single reading test */
		test_adcs();
		break;

	case 'v':	/* Set Vc voltage and output enable */
		parse_vc();
		break;
	}

	/* Throw away everything else on the input line */
	skip_to_eol();
}
