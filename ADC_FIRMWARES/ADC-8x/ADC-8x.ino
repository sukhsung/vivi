/* Driver for the ADC-8x quad 24-bit ADC board with 256 MB memory */

#include "adc-8x.h"

const char		version_str[] = "4h";
char			buf[128];
volatile unsigned int	rtc_seconds;
int			rtc_tz_offset = Date_time::NO_TZ;
bool			date_time_is_set;
int			num_adcs;

struct pushbutton	pb1;

bool		Vc_0V_setting;		// True => Vc = 0, False => Vc = Vc-bias
bool		EnVc_setting;		// True => enabled
unsigned int	dac_value;		// 10-bit DAC data value

uint32_t	samd21_serial_number[4];

unsigned int	Rd_values;		// Packed bits for PCA_Rd and PCA_RdDB

void		print_id(void);

Pm		* const pm = PM;
Adc		* const adc0 = ADC;
Dac		* const dac = DAC;
Gclk		* const gclk = GCLK;
Sysctrl		* const sysctrl = SYSCTRL;
RtcMode0	* const rtc = &RTC->MODE0;
SercomI2cm	* const ser_i2c = &SERCOM3->I2CM;
SercomSpi	* const ser_spi = &SERCOM4->SPI;
PortGroup	* const portA = &PORT_IOBUS->Group[0];
PortGroup	* const portB = &PORT_IOBUS->Group[1];
PortGroup	* const portAx = &PORT->Group[0];
PortGroup	* const portBx = &PORT->Group[1];
uint32_t	* const aux3 = (uint32_t *) NVMCTRL_AUX3_ADDRESS;

void setup(void)
{
	int	i;

	/*
	 * Set the negated output pins and SPI and I2C pins HIGH, the rest LOW.
	 */
	portA->OUTSET.reg = nSYNC_PIN_BIT | nCS1_PIN_BIT | nCS2_PIN_BIT |
			nCS3_PIN_BIT | nCS4_PIN_BIT | nCS5_PIN_BIT |
			nCS6_PIN_BIT | nCS7_PIN_BIT | nCS8_PIN_BIT |
			SWCLK_PIN_BIT | SDA_PIN_BIT | SCL_PIN_BIT;
	portB->OUTSET.reg = nCSFM_PIN_BIT | MOSI_PIN_BIT | SCK_PIN_BIT;
	portA->OUTCLR.reg = DAC_PIN_BIT | Vc_0V_PIN_BIT | EnVc_PIN_BIT |
			X4_PIN_BIT | LD1_PIN_BIT | RdH_PIN_BIT |
			USBM_PIN_BIT | USBP_PIN_BIT | SWDIO_PIN_BIT |
			LD5_EN_PIN_BIT | LD5_SEL_PIN_BIT;
	portB->OUTCLR.reg = LD2_PIN_BIT | Boff_PIN_BIT | EnX_PIN_BIT;

	/* Set the appropriate pins to be outputs */
	portA->DIRSET.reg = DAC_PIN_BIT | nSYNC_PIN_BIT | Vc_0V_PIN_BIT |
			EnVc_PIN_BIT | X4_PIN_BIT | LD1_PIN_BIT | RdH_PIN_BIT |
			nCS1_PIN_BIT | nCS2_PIN_BIT | nCS3_PIN_BIT |
			nCS4_PIN_BIT | nCS5_PIN_BIT | nCS6_PIN_BIT |
			nCS7_PIN_BIT | nCS8_PIN_BIT |
			SWDIO_PIN_BIT | SWCLK_PIN_BIT |
			SDA_PIN_BIT | SCL_PIN_BIT |
			LD5_EN_PIN_BIT | LD5_SEL_PIN_BIT;
	portB->DIRSET.reg = LD2_PIN_BIT | nCSFM_PIN_BIT | Boff_PIN_BIT |
			MOSI_PIN_BIT | SCK_PIN_BIT | EnX_PIN_BIT;

	/* Change the SWD pins from peripheral G (COM) back to PORT */
	portAx->WRCONFIG.reg = PORT_WRCONFIG_HWSEL |	// Port #s >= 16
			PORT_WRCONFIG_WRPINCFG |
			PORT_WRCONFIG_DRVSTR |
							// PMUXEN not set
			PORT_WRCONFIG_PINMASK(
				(SWCLK_PIN_BIT | SWDIO_PIN_BIT) >> 16);

	/* Enable input on the CLOCK, nPB1, USBon, and dbC pins */
	portAx->WRCONFIG.reg = PORT_WRCONFIG_WRPINCFG |
			PORT_WRCONFIG_INEN |
			PORT_WRCONFIG_PINMASK(CLOCK_PIN_BIT | nPB1_PIN_BIT);
	portBx->WRCONFIG.reg = PORT_WRCONFIG_WRPINCFG |
			PORT_WRCONFIG_INEN |
			PORT_WRCONFIG_PINMASK(USBon_PIN_BIT);
	portBx->WRCONFIG.reg = PORT_WRCONFIG_HWSEL |	// Port #s > 16
			PORT_WRCONFIG_WRPINCFG |
			PORT_WRCONFIG_INEN |
			PORT_WRCONFIG_PINMASK(dbC_PIN_BIT >> 16);

	// Turn on continuous sampling of the CLOCK pin
	portAx->CTRL.reg = CLOCK_PIN_BIT;

	/* Switch the DAC, Vref, and Vbat pins to peripheral B (analog) */
	portAx->WRCONFIG.reg = PORT_WRCONFIG_WRPINCFG |	// Write pin config
			PORT_WRCONFIG_WRPMUX |
			PORT_WRCONFIG_PMUX(PORT_PMUX_PMUXE_B_Val) |
					// Pullup and input disabled
			PORT_WRCONFIG_PMUXEN |
			PORT_WRCONFIG_PINMASK(DAC_PIN_BIT | Vref_PIN_BIT |
				Vbat_PIN_BIT);

	/* Set up the bus clock masks */
	// Disable the AHB bus clocks for DMAC and DSU
	pm->AHBMASK.reg &= ~(PM_AHBMASK_DMAC | PM_AHBMASK_DSU);

	// Enable the APBA bus clock for RTC
	pm->APBAMASK.reg |= PM_APBAMASK_RTC;
	// Turn off WDT and PAC0
	pm->APBAMASK.reg &= ~(PM_APBAMASK_WDT | PM_APBAMASK_PAC0);

	// Turn off APBB bus clocks for DMAC, NVMCTRL, DSU, and PAC1
	pm->APBBMASK.reg &= ~(PM_APBBMASK_DMAC | PM_APBBMASK_NVMCTRL |
			PM_APBBMASK_DSU | PM_APBBMASK_PAC1);

	// Enable the APBC bus clocks for SERCOM3 and 4, DAC, and ADC
	// Turn off all others
	pm->APBCMASK.reg = PM_APBCMASK_SERCOM3 | PM_APBCMASK_SERCOM4 |
			PM_APBCMASK_DAC | PM_APBCMASK_ADC;

	/* Disable unused clock generators 2 and 3 (OSCULP32K and OSC8M) */
	gclk->GENCTRL.reg = GCLK_GENCTRL_ID(2);		// Turn off GENEN bit
	gclk->GENCTRL.reg = GCLK_GENCTRL_ID(3);

	/* Disable unused generic clocks WDT and AC_ANA */
	gclk->CLKCTRL.reg = GCLK_CLKCTRL_ID_WDT;
	gclk->CLKCTRL.reg = GCLK_CLKCTRL_ID_AC_ANA;

	/*
	 * Set up the generic clocks for SERCOM4, DAC, and ADC
	 * to run off generator 0 at 48 MHz
	 */
	gclk->CLKCTRL.reg = GCLK_CLKCTRL_ID_SERCOM4_CORE;	// Disable
	gclk->CLKCTRL.reg = GCLK_CLKCTRL_ID_SERCOM4_CORE |
			GCLK_CLKCTRL_GEN_GCLK0 | GCLK_CLKCTRL_CLKEN;

	gclk->CLKCTRL.reg = GCLK_CLKCTRL_ID_DAC;	// Disable
	gclk->CLKCTRL.reg = GCLK_CLKCTRL_ID_DAC |
			GCLK_CLKCTRL_GEN_GCLK0 | GCLK_CLKCTRL_CLKEN;

	gclk->CLKCTRL.reg = GCLK_CLKCTRL_ID_ADC;	// Disable
	gclk->CLKCTRL.reg = GCLK_CLKCTRL_ID_ADC |
			GCLK_CLKCTRL_GEN_GCLK0 | GCLK_CLKCTRL_CLKEN;

	/*
	 * Set up the RTC generic clock to run off generator 1 (XOSC32K)
	 * at 32.768 KHz
	 */
	gclk->CLKCTRL.reg = GCLK_CLKCTRL_ID_RTC;	// Disable
	gclk->CLKCTRL.reg = GCLK_CLKCTRL_ID_RTC |
			GCLK_CLKCTRL_GEN_GCLK1 | GCLK_CLKCTRL_CLKEN;

	while (gclk->STATUS.bit.SYNCBUSY)
		;	// Wait for synchronization

	/* Disable unused clock sources OSC32K and OSC8M */
	sysctrl->OSC32K.bit.ENABLE = 0;
	sysctrl->OSC8M.bit.ENABLE = 0;

	/* Set the XOSC32K clock source to always run in STANDBY */
	sysctrl->XOSC32K.bit.RUNSTDBY = 1;
	sysctrl->XOSC32K.bit.ONDEMAND = 0;

	/* Configure the RTC peripheral */
	rtc->CTRL.reg = RTC_MODE0_CTRL_PRESCALER_DIV1024 |	// 32-Hz counter
			RTC_MODE0_CTRL_MATCHCLR |	// One-second period
			RTC_MODE0_CTRL_MODE_COUNT32;
	rtc->INTENSET.reg = RTC_MODE0_INTENSET_CMP0;
	rtc->COUNT.reg = 0;
	rtc->COMP[0].reg = 31;			// Interrupt on 32nd count

	/* Enable the RTC peripheral */
	rtc->CTRL.bit.ENABLE = 1;
	while (rtc->STATUS.bit.SYNCBUSY)
		;		// Wait for the enable
	NVIC_EnableIRQ(RTC_IRQn);

	/* Configure the SERCOM4 peripheral for SPI */
	ser_spi->CTRLA.reg =				// MSB first
			SERCOM_SPI_CTRLA_CPOL |		// Clock mode 3:
			SERCOM_SPI_CTRLA_CPHA |
				// clock is idle high, sampled on rising edge
							// No address in frame
			SERCOM_SPI_CTRLA_DIPO(0) |	// Pad 0 (PA12) is MISO
			SERCOM_SPI_CTRLA_DOPO(1) |	// Pad 2 (PB10) is MOSI
							// Pad 3 (PB11) is SCK
			SERCOM_SPI_CTRLA_MODE_SPI_MASTER;
							// No enable yet

	ser_spi->CTRLB.reg = SERCOM_SPI_CTRLB_RXEN |	// Enable the receiver
							// SS control disabled
			SERCOM_SPI_CTRLB_CHSIZE(0);	// 8-bit data

	/* Set SCK and MOSI pins to peripheral D (SERCOM-ALT) */
	portBx->WRCONFIG.reg = PORT_WRCONFIG_WRPINCFG |
			PORT_WRCONFIG_WRPMUX |
			PORT_WRCONFIG_PMUX(PORT_PMUX_PMUXE_D_Val) |
			PORT_WRCONFIG_PMUXEN |
			PORT_WRCONFIG_DRVSTR |		// Set high strength
			PORT_WRCONFIG_PINMASK(SCK_PIN_BIT | MOSI_PIN_BIT);

	/* Set the MISO pin to peripheral D (SERCOM-ALT) */
	portAx->WRCONFIG.reg = PORT_WRCONFIG_WRPINCFG |
			PORT_WRCONFIG_WRPMUX |
			PORT_WRCONFIG_PMUX(PORT_PMUX_PMUXE_D_Val) |
			PORT_WRCONFIG_PMUXEN |
			PORT_WRCONFIG_PINMASK(MISO_PIN_BIT);

	/* Flash the channel-status LEDs on the I2C expander port */
	i2c_start(PCA_LED_ADDR);
	if (i2c_write_reg(PCA_CTRL_OUTPUT, ~0) == 0) {
				// All off: output byte is inverted
		led_i2c_expander_present = true;
		// Set all ports to output and cycle through them
		i2c_write_reg(PCA_CTRL_CONFIG, 0);
		for (i = 0; i < MAX_ADCS; ++i) {
			if (i2c_write_reg(PCA_CTRL_OUTPUT, ~(1 << i)) != 0)
				break;
			delay(250);
		}
		i2c_write_reg(PCA_CTRL_OUTPUT, ~0);	// All LEDs off
	}
	i2c_stop();

	/* Initialize the resistor-test I2C expanders */
	i2c_start(PCA_Rd_ADDR);
	if (i2c_write_reg(PCA_CTRL_OUTPUT, 0) == 0) {
		Rd_i2c_expander_present = true;
		// Set all ports to output
		i2c_write_reg(PCA_CTRL_CONFIG, 0);
	}
	i2c_stop();

	i2c_start(PCA_RdDB_ADDR);
	if (i2c_write_reg(PCA_CTRL_OUTPUT, 0) == 0) {
		RdDB_i2c_expander_present = true;
		// Set all ports to output
		i2c_write_reg(PCA_CTRL_CONFIG, 0);
	}
	i2c_stop();

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

	/* Set up the ADC peripheral */
	// Call it adc0 to distinguish it from the adc structures
	adc0->REFCTRL.reg = ADC_REFCTRL_REFCOMP |
				// Enable reference buffer offset compensation
			ADC_REFCTRL_REFSEL_AREFA;
				// Voltage reference is VREFA = Vref = 2.50 V
	// Use maximum amount of averaging
	adc0->SAMPCTRL.reg = 64 - 1;	// Sampling period = 42.7 us
	adc0->CTRLB.reg = ADC_CTRLB_PRESCALER_DIV32;	// 48 MHz / 32 = 1.5 MHz
	// 12-bit resolution, no gain or offset correction,
	// single-conversion mode, right-adjusted results, single-ended mode,
	// no windowing
	adc0->INPUTCTRL.reg = 		// 1X gain, no scanning
				ADC_INPUTCTRL_MUXNEG_IOGND |
				ADC_INPUTCTRL_MUXPOS_PIN7;	// AIN[7] = PA07
	adc0->CTRLA.reg = ADC_CTRLA_ENABLE;	// Enable the ADC
	while (adc0->STATUS.bit.SYNCBUSY)
		;		// Wait for the enable

	adc0->INTFLAG.reg = ADC_INTFLAG_MASK;	// Clear INTFLAG register
	adc0->SWTRIG.reg = ADC_SWTRIG_START;	// Start a conversion
	while (!adc0->INTFLAG.bit.RESRDY)
		;		// Wait for the result
	(void) adc0->RESULT.reg;			// Throw first one away

	/*
	 * The SAMD21's serial number is a 128-bit value distributed among
	 * four 32-bit words in the AUX3 area.
	 */
	samd21_serial_number[0] = aux3[3];
	samd21_serial_number[1] = aux3[16];
	samd21_serial_number[2] = aux3[17];
	samd21_serial_number[3] = aux3[18];

	/* See if an ADC-8xD daughterboard is present */
	if (portBx->IN.reg & dbC_PIN_BIT)
		num_adcs = MAX_ADCS;
	else
		num_adcs = NO_DB_ADCS;

	/* Disallow running on battery power */
	portB->OUTSET.reg = Boff_PIN_BIT;

	/* Initialize the USB link */
	Serial.begin(9600);
	Serial.setTimeout(0);

	/* Blink the LED while waiting for a serial connection */
	while (!Serial) {
		portA->OUTTGL.reg = LD1_PIN_BIT;
		delay(100);
	}
	portA->OUTCLR.reg = LD1_PIN_BIT;

	delay(500);
	Serial.print("\n\n");

	/* Set the fast flash-memory clock rate */
	enable_SPI(SPI_FLASH);
	init_flash_memory();

	if (w25_jedec_id != W25_JEDEC_ID_VALUE) {
		Serial.print("Flash memory JEDEC ID value is invalid\n");
		w25_jedec_id = 0;
	} else {
		read_flash_unique_id_and_attrs();
	}

	print_id();

	if (w25_jedec_id) {
		scan_for_bad_blocks();
		scan_datasets();
	}
	disable_SPI();

	/* Set the slower ADC clock rate */
	enable_SPI(SPI_ADC);

	/* Reset and query all the ADCs */
	for (i = 0; i < num_adcs; ++i)
		init_adc(i);
	disable_SPI();

	/* Show the channel-status LEDs */
	show_channel_gain_leds();
}

/* Interrupt handler */
void RTC_Handler(void)
{
	rtc->INTFLAG.reg = RTC_MODE0_INTFLAG_MASK;	// Clear all IRQs
	++rtc_seconds;
}

/* Poll the pushbutton (should happen at approx. 10 - 100-ms intervals) */
void poll_pushbutton()
{
	bool			state;
	struct pushbutton 	*pb = &pb1;
	unsigned long		t;

	state = !(portAx->IN.reg & nPB1_PIN_BIT);

	// Fast path for the normal case: button not pressed for a while
	if (!(state | pb->pressed | pb->changed | pb->counting))
		return;

	t = millis();

	// Exceeded the multipress threshold?
	if (pb->counting && !pb->changed &&
			t - pb->state_time > PB_MULTIPRESS_THRESHOLD)
		pb->counting = false;

	// Handle state changes
	if (state != pb->pressed) {
		if (!pb->changed) {		// Start debounce
			pb->changed = true;
			pb->change_time = t;
		} else if (t - pb->change_time >= PB_DEBOUNCE_THRESHOLD) {
			// Debounce finished; state has changed
			pb->pressed = state;
			pb->changed = false;
			pb->state_time = pb->change_time;
			if (state) {
				pb->long_press = false;

				// Count multipress events
				if (!pb->counting) {
					pb->counting = true;
					pb->multipress_count = 1;
				} else if (pb->multipress_count <
						PB_MULTIPRESS_MAX) {
					++pb->multipress_count;
				}
			}
		}

	// Handle no change of state
	} else {
		pb->changed = false;

		// Check for a long press
		if (state && !pb->long_press &&
				t - pb->state_time > PB_LONG_PRESS_THRESHOLD)
			pb->long_press = true;
	}
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
	int	c;

	for (;;) {
		c = Serial.peek();
		if (c < 0)
			break;
		Serial.read();
		if (c == '\n')
			break;
	}
}

/* Trims leading and trailing whitespace */
int read_string(char *strbuf, int size, bool allow_whitespace)
{
	int	c, n, nw;

	--size;			// Leave room for terminating NUL
	n = nw = 0;

	/* Skip leading whitespace */
	do {
		c = Serial.read();
		if (c < 0 || c == '\n')
			goto Done;
	} while (c <= ' ');

	/* Read text, keeping track of last non-whitespace */
	for (;;) {
		if (n < size) {
			strbuf[n++] = c;
			if (c > ' ')
				nw = n;
		}
		c = Serial.read();
		if (c < 0 || c == '\n')
			break;
		if (c <= ' ' && !allow_whitespace)
			break;
	}

 Done:
	strbuf[nw] = 0;
	return nw;
}

#define IS_UTF8_CONTINUATION_BYTE(b)		(((b) & 0xc0) == 0x80)

/* Read in a UTF-8 string limited to max_bytes counting the terminal NUL */
unsigned int read_utf8_string(char *dest, unsigned int max_bytes,
		bool consume_newline)
{
	int		c;
	unsigned int	n;

	n = 0;
	for (;;) {
		c = Serial.peek();
		if (c < 0)
			continue;

		/* End at newline; skip other control characters */
		if (c == '\n') {
			if (consume_newline)
				Serial.read();
			break;
		}
		Serial.read();
		if (c < 32)
			continue;

		/* If there's room, store the byte */
		if (n < max_bytes)
			dest[n++] = c;
	}

	/* Back up to the start of the last complete code point */
	if (n == max_bytes) {
		while (--n > 0) {
			if (!IS_UTF8_CONTINUATION_BYTE(dest[n]))
				break;		// Start of a codepoint
		}
	}
	dest[n] = 0;
	return n;		// String length in bytes
}

void print_buf(void)
{
	Serial.print(buf);
}

void print_id(void)
{
	char	*p;
	int	i;

	sprintf(buf, "ADC-8x driver version %s\n", version_str);
	print_buf();
	sprintf(buf, "SAMD21 ID: %08lx-%08lx-%08lx-%08lx\n",
			samd21_serial_number[0], samd21_serial_number[1],
			samd21_serial_number[2], samd21_serial_number[3]);
	print_buf();
	p = buf + sprintf(buf, "Flash ID:  ");
	if (w25_jedec_id) {		// Flash chip is working
		for (i = 0; i < W25_UNIQUE_ID_LEN / 2; i += 4)
			p += sprintf(p, "%02x%02x%02x%02x-",
					w25_unique_id[i],
					w25_unique_id[i+1],
					w25_unique_id[i+2],
					w25_unique_id[i+3]);
		p[-1] = '\n';
		print_buf();
		// Second half of the Unique ID is one's complement of first half

#if 0
		p = buf;
		for (i = 0; i < NUM_ATTRS; ++i) {
			if (i > 0)
				p += sprintf(p, ",  ");
			p += sprintf(p, "%s = %s", attr_names[i], attrs[i]);
		}
		sprintf(p, "\n");
		print_buf();
#endif
	} else {
		strcpy(p, "not working\n");
		print_buf();
	}
	Serial.println();
}

void show_current_settings(void)
{
	int		i;
	unsigned int	x, dbc, usbon, vbat;
	struct adc	*adc;
	char		*p;

	sprintf(buf, "\nCurrent settings:  Sampling rate %.2f\n",
			SAMPLING_MAX / (float) rate_divisor);
	print_buf();

	i = portAx->OUTSET.reg & X4_PIN_BIT;
	sprintf(buf, "Extra on-board channel-4 input %s\n",
			(i ? "enabled" : "disabled"));
	print_buf();

	for (i = 0; i < num_adcs; ++i) {
		adc = &adcs[i];
		p = buf;
		p += sprintf(p, "ADC %d: ", i + 1);
		if (!adc->working) {
			sprintf(p, "not working\n");
		} else if (adc->gain == 0) {
			sprintf(p, "disabled\n");
		} else {
			p += sprintf(p, "gain %d, %spolar, %sbuffered, Rd %c\n",
					adc->gain,
					(adc->polarity == 1 ? "uni" : "bi"),
					(adc->buffered ? "" : "un"),
					(Rd_values & PACK_Rd_BIT(i) ? '+' : '-'));
		}
		print_buf();
	}

	x = (dac_value * REFERENCE_VOLTAGE + 512) / 1024;
	sprintf(buf, "DAC output voltage set to %u mV\n", x);
	print_buf();
	sprintf(buf, "Vc bias setting: %d   EnVc setting: %d\n",
			!Vc_0V_setting, EnVc_setting);
	print_buf();

	/* Read the dbC, USBon, and Boff pin values */
	dbc = !!(portBx->IN.reg & dbC_PIN_BIT);
	usbon = !!(portBx->IN.reg & USBon_PIN_BIT);
	i = !!(portBx->OUTSET.reg & Boff_PIN_BIT);

	/* Read half the battery voltage */
	adc0->SWTRIG.reg = ADC_SWTRIG_START;	// Start a conversion
	while (!adc0->INTFLAG.bit.RESRDY)
		;		// Wait for the result
	x = adc0->RESULT.reg;
	// Scale by the reference voltage and the full-scale value
	x = (x * REFERENCE_VOLTAGE) >> 12;
	// Double the result to get Vbat rather than Vbat/2
	vbat = x * 2;

	sprintf(buf, "dbC: %u  USBon: %u  Vbat: %u mV  Boff: %u\n",
			dbc, usbon, vbat, i);
	print_buf();
}

void show_current_settings_fixed_format(void)
{
	int		i;
	unsigned int	dac_voltage_mv;
	unsigned int	X4_setting;
	struct adc	*adc;

	dac_voltage_mv = (dac_value * REFERENCE_VOLTAGE + 512) / 1024;
	X4_setting = !!(portAx->OUTSET.reg & X4_PIN_BIT);
	sprintf(buf, "%.3f,%u,%d,%d,%d\n",
			SAMPLING_MAX / (float) rate_divisor,
			dac_voltage_mv,
			EnVc_setting,
			!Vc_0V_setting,
			X4_setting);
	print_buf();

	for (i = 0; i < MAX_ADCS; ++i) {
		adc = &adcs[i];
		sprintf(buf, "%d,%d,%d,%d\n",
				adc->gain,
				adc->polarity,
				adc->buffered,
				!!(Rd_values & PACK_Rd_BIT(i)));
		print_buf();
	}
}

void set_dac_voltage(void)
{
	long		v;
	unsigned int	x;

	v = Serial.parseInt();
	if (v < 0 || v > REFERENCE_VOLTAGE) {
		sprintf(buf, "Invalid DAC voltage: %ld\n", v);
		print_buf();
		return;
	}

	/* Convert to a 10-bit output value and write to the DAC */
	x = (1024 * v + REFERENCE_VOLTAGE / 2) / REFERENCE_VOLTAGE;
	x = min(x, 1023);
	dac->DATA.reg = dac_value = x;

	x = (x * REFERENCE_VOLTAGE + 512) / 1024;
	sprintf(buf, "DAC output voltage set to %u mV\n", x);
	print_buf();
}

#define ALL_CHANNELS		0x00ff

void parse_gain(void)
{
	unsigned int	mask;
	int		c, b, g, i;
	long		v1, v2;
	bool		settings_okay;
	struct adc	*adc;
	char		*p;

	/* Parse the channel numbers */
	mask = 0;
	for (;;) {
		c = Serial.read();
		if ('1' <= c && c <= '8') {
			i = c - '1';
			if (!adcs[i].working) {
				sprintf(buf, "ADC %c is not working\n", c);
				print_buf();
			} else {
				mask |= 1 << i;
			}
		} else if (c == '0') {
			mask = ALL_CHANNELS;
		} else if (c <= ' ') {
			if (mask)
				break;
			if (c < 0 || c == '\n') {
				Serial.print("No settings specified\n");
				return;
			}
		} else {
			sprintf(buf, "Invalid ADC channel number: %c\n", c);
			print_buf();
			return;
		}
	}

	v1 = Serial.parseInt();
	v2 = Serial.parseInt();
	b = get_next_nonspace();

	settings_okay = false;
	if (v1 == 0)
		g = 999;
	else
		g = gain_code(v1);

	if (g < 0)
		sprintf(buf, "Invalid gain setting: %ld\n", v1);
	else if (v2 < 0 || v2 > 2)
		sprintf(buf, "Invalid polarity setting: %ld\n", v2);
	else if (!(b == 0 || b == 'b' || b == 'u'))
		sprintf(buf, "Invalid buffer selection: %c\n", b);
	else
		settings_okay = true;
	if (!settings_okay) {
		print_buf();
		return;
	}

	for (i = 0; i < num_adcs; ++i) {
		if (mask & (1 << i)) {
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
	if (mask == ALL_CHANNELS) {
		p += sprintf(p, "All ADCs");
	} else {
		p += sprintf(p, "ADC ");
		c = 0;
		for (i = 0; i < num_adcs; ++i) {
			if (mask & (1 << i)) {
				if (c)
					*p++ = ',';
				p += sprintf(p, "%d", i + 1);
				c = 1;
			}
		}
	}
	if (v1 == 0) {
		sprintf(p, " disabled\n");
	} else {
		p += sprintf(p, " set to gain %ld, ", v1);
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
	print_buf();

	show_channel_gain_leds();
}

void parse_sampling(void)
{
	long	v1;

	v1 = Serial.parseInt();

	if (v1 <= 0 || v1 > SAMPLING_MAX) {
		sprintf(buf, "Invalid sampling rate: %ld\n", v1);
	} else {
		rate_divisor = min(SAMPLING_MAX / v1, MR_FSMASK);

		sprintf(buf, "Sampling rate set to %.2f Hz\n",
				SAMPLING_MAX / (float) rate_divisor);
	}
	print_buf();
}

void parse_vc_sp(void)
{
	int	i, j;

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
	print_buf();
}

void set_Rds(unsigned int packed_values)
{
	// Set the current source and resistor switches according to the
	// packet bits in packed_values
	i2c_start(PCA_Rd_ADDR);
	i2c_write_reg(PCA_CTRL_OUTPUT, UNPACK_Rd_BITS(packed_values));
	i2c_stop();

	i2c_start(PCA_RdDB_ADDR);
	i2c_write_reg(PCA_CTRL_OUTPUT, UNPACK_RdDB_BITS(packed_values));
	i2c_stop();

	// Set the RdH (LD4) LED to match the 50-µA current source state
	if (packed_values & PACK_50uA_BIT)
		portA->OUTSET.reg = RdH_PIN_BIT;
	else
		portA->OUTCLR.reg = RdH_PIN_BIT;
}

void parse_Rds(void)
{
	int			c, i;
	unsigned int		mask, new_Rds;
	char			*p;
	static const char	signs[] = "-+";

	new_Rds = Rd_values;
	mask = 0;
	for (;;) {
		c = Serial.read();

		if ('1' <= c && c <= '8') {
			i = c - '1';
			mask |= PACK_Rd_BIT(i);
		} else if (c == '0') {
			mask |= PACK_ALL_Rd_BITS;
		} else if (c == '+' || c == '-') {
			if (!mask)
				Serial.print("Warning: + or - with no settings\n");
			else if (c == '+')
				new_Rds |= mask;
			else
				new_Rds &= ~mask;
			mask = 0;
		} else if (c <= ' ') {
			if (mask)
				Serial.print("Warning: setting with no + or -\n");
			mask = 0;
		} else {
			sprintf(buf, "Invalid setting: %c\n", c);
			print_buf();
		}
		if (c < 0 || c == '\n')
			break;
	}

	Rd_values = new_Rds;
	set_Rds(new_Rds);

	p = buf + sprintf(buf, "Impedance settings: ");
	p += sprintf(p, " sources%c", signs[new_Rds & 1]);
	for (i = 1; i <= 8; ++i)
		p += sprintf(p, " %d%c", i, signs[!!(new_Rds & (1 << i))]);
	strcpy(p, "\n");
	print_buf();
}

void set_leds(void)
{
	long	v1, v2, v4;

	v1 = Serial.parseInt();
	v2 = Serial.parseInt();
	v4 = Serial.parseInt();

	if (v1 < 0 || v1 > 1 || v2 < 0 || v2 > 1 || v4 < 0 || v4 > 1) {
		Serial.print("Invalid LED value\n");
		return;
	}
	sprintf(buf, "Setting LEDs: %ld %ld %ld\n", v1, v2, v4);
	print_buf();

	if (v1)
		portA->OUTSET.reg = LD1_PIN_BIT;
	else
		portA->OUTCLR.reg = LD1_PIN_BIT;
	if (v2)
		portB->OUTSET.reg = LD2_PIN_BIT;
	else
		portB->OUTCLR.reg = LD2_PIN_BIT;
	if (v4)
		portA->OUTSET.reg = RdH_PIN_BIT;
	else
		portA->OUTCLR.reg = RdH_PIN_BIT;
}

void get_set_date_time(void)
{
	bool			anything;
	class Date_time		dt;

	anything = true;
	dt.tz_offset = rtc_tz_offset;
	dt.set_seconds(rtc_seconds);

	if (read_word(buf, sizeof(buf)) == 0) {
		if (!date_time_is_set) {
			Serial.println("Date and time have not been set");
			return;
		}
		anything = false;
	} else if (dt.parse_date(buf) != 0) {
		if (dt.parse_time(buf, true) != 0) {
			Serial.println("Invalid date/time");
			return;
		}
		if (!date_time_is_set) {
			Serial.println("No date specified");
			return;
		}
	} else if (read_word(buf, sizeof(buf)) == 0) {
		if (!date_time_is_set) {
			Serial.println("No time specified");
			return;
		}
	} else if (dt.parse_time(buf, true) != 0) {
		Serial.println("Invalid time");
		return;
	} else if (dt.tz_offset == rtc_tz_offset) {
		// Allow removal of the TZ offset
		dt.tz_offset = Date_time::NO_TZ;
		dt.parse_time(buf, true);
	}

	if (anything) {
		rtc_seconds = dt.get_seconds();
		rtc_tz_offset = dt.tz_offset;
		date_time_is_set = true;
	}

	dt.format(dt.buffer);
	sprintf(buf, "Date and time set to: %s\n", dt.buffer);
	print_buf();
}

void loop(void)
{
	int	c, i;

	if (data_collection_in_progress) {
		continue_data_collection();
		return;
	}

	poll_pushbutton();
	if (pb1.pressed) {
		measure_Rs(false);
		return;
	}

	c = Serial.read();
	if (c <= ' ')		// Skip whitespace
		return;

	switch (c) {
	case '*':	/* Identify myself */
		print_id();
		break;

	case 'b':	// Begin data collection
		begin_data_collection();
		break;

	case 'c':	// Show the settings
		i = Serial.parseInt();
		if (i == 0)
			show_current_settings();
		else
			show_current_settings_fixed_format();
		break;

	case 'd':	// Get/set the current date and time
		get_set_date_time();
		break;

	case 'e':	// Set DAC bias voltage output
		set_dac_voltage();
		break;

	case 'f':	// Set the 50-µA current sources
		i = Serial.parseInt();
		if (i == 0) {
			Serial.println("50-uA current sources disabled");
			Rd_values &= ~PACK_50uA_BIT;
			set_Rds(Rd_values);
		} else if (i == 1) {
			Serial.println("50-uA current sources enabled");
			Rd_values |= PACK_50uA_BIT;
			set_Rds(Rd_values);
		} else {
			Serial.println("Invalid current-source setting");
		}
		break;

	case 'g':	// Gain and other individual settings
		parse_gain();
		break;

	case 'i':	// Set the damping resistor switches
		parse_Rds();
		break;

	case 'l':	// Set the LEDs
		set_leds();
		break;

	case 'm':	// Measure the Rs signal resistances
		i = Serial.parseInt();
		measure_Rs(!!i);
		break;

	case 'r':	// Reset all ADCs and LEDs
		Serial.print("\nReset all ADCs and LEDs...\n");
		enable_SPI(SPI_ADC);
		for (i = 0; i < num_adcs; ++i)
			init_adc(i);
		disable_SPI();

		portA->OUTCLR.reg = LD1_PIN_BIT;
		portB->OUTCLR.reg = LD2_PIN_BIT;
		portA->OUTCLR.reg = RdH_PIN_BIT;
		break;

	case 's':	// Sampling rate
		parse_sampling();
		break;

	case 't':	// Single reading test
		enable_SPI(SPI_ADC);
		test_adcs_and_button();
		disable_SPI();
		break;

	case 'v':	// Set Vc voltage and SP sensor power output enable
		parse_vc_sp();
		break;

	case 'x':	// Enable/disable the extra onboard channel-4 input
		i = Serial.parseInt();
		if (i == 0) {
			Serial.println("On-board channel-4 input disabled");
			portA->OUTCLR.reg = X4_PIN_BIT;
		} else if (i == 1) {
			Serial.println("On-board channel-4 input enabled");
			portA->OUTSET.reg = X4_PIN_BIT;
		} else {
			Serial.println("Invalid on-board input setting");
		}
		break;

#if 0
	case 'y':	// Enable/disable the LD5 battery LEDs
		i = Serial.parseInt();
		if (i == 0) {
			Serial.println("Disable battery LEDs");
			portA->OUTCLR.reg = LD5_EN_PIN_BIT;
		} else if (i == 1) {
			Serial.println("Enable red battery LED");
			portA->OUTSET.reg = LD5_EN_PIN_BIT;
			portA->OUTCLR.reg = LD5_SEL_PIN_BIT;
		} else if (i == 2) {
			Serial.println("Enable green battery LED");
			portA->OUTSET.reg = LD5_EN_PIN_BIT | LD5_SEL_PIN_BIT;
		} else {
			Serial.println("Invalid battery LED setting");
		}
		break;
#endif

	case 'z':	// Turn the Boff signal on or off
		i = Serial.parseInt();
		if (i == 0) {
			Serial.println("Set Boff low");
			portB->OUTCLR.reg = Boff_PIN_BIT;
		} else {
			Serial.println("Set Boff high");
			portB->OUTSET.reg = Boff_PIN_BIT;
		}
		break;
	}

	/* Throw away everything else on the input line */
	skip_to_eol();
}
