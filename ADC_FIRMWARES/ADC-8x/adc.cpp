/* Subroutines to communicate with the ADCs */

#include "adc-8x.h"

struct adc adcs[MAX_ADCS] = {
	{ nCS1_PIN_BIT, 0, 0, 1, 2, 0},
	{ nCS2_PIN_BIT, 0, 0, 1, 2, 0},
	{ nCS3_PIN_BIT, 0, 0, 1, 2, 0},
	{ nCS4_PIN_BIT, 0, 0, 1, 2, 0},
	{ nCS5_PIN_BIT, 0, 0, 1, 2, 0},
	{ nCS6_PIN_BIT, 0, 0, 1, 2, 0},
	{ nCS7_PIN_BIT, 0, 0, 1, 2, 0},
	{ nCS8_PIN_BIT, 0, 0, 1, 2, 0},
};

/* All eight ADCs use the same output rate */
// Actual sampling rate is SAMPLING_MAX / rate_divisor
unsigned int	rate_divisor = SAMPLING_MAX / 50;	// 1 - 1023

uint8_t		output_data[OUTPUT_BUF_SIZE];
uint8_t		*pout;
uint8_t		const *output_limit;

bool		data_collection_in_progress;
int		num_running_adcs;
unsigned long	data_exp_time;		// Expiration time for next sample
long		samples_remaining;	// Number of samples remaining to collect


void start_adcs_clock(void)
{
	portB->OUTSET.reg = EnX_PIN_BIT;	// Turn on ADCs' clock
	delay(X2_START_DELAY);			// Wait for it to stabilize
}

void stop_adcs_clock(void)
{
	portB->OUTCLR.reg = EnX_PIN_BIT;	// Turn off ADCs' clock
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
	bool	rc = true;

	while (portAx->IN.reg & MISO_PIN_BIT) {		// nRDY is high
		if (time_expired(exp_time)) {
			rc = false;
			break;
		}
	}

	return rc;
}

void init_adc(int i)
{
	struct adc	*adc = &adcs[i];
	int		n;
	unsigned int	val;

	i += 1;

	/* Reset the ADC */
	enable_adc_CS(adc);
	for (n = 0; n < ADC_RESET_LEN; ++n)
		spi_send_byte(0xFF);
	adc->running = 0;
	disable_adc_CS();

	/* Wait for the ADC to reset itself */
	delay(1);

	enable_adc_CS(adc);

	/* Try to read the ID register */
	spi_send_byte(CR_RnW | REG_ID);		// Read the ID register
	val = spi_read_byte();			// Read the register value

	/* Put the ADC into idle mode */
	spi_send_byte(REG_MODE);		// Write the Mode register
	spi_send_3(MODE_IDLE + CLK_CLOCK + 1);	// Send the mode value

	disable_adc_CS();

	if ((val & ID_MASK) == ID_VALUE) {
		sprintf(buf, "ADC %d ID value: %02x\n", i, val);
		adc->working = 1;
		adc->gain = 1;
	} else {
		sprintf(buf, "ADC %d sent invalid ID value: %02x\n", i, val);
		adc->working = 0;
		adc->gain = 0;
	}
	print_buf();
}

void compute_mode_and_config(struct adc *adc, uint32_t *mode, uint32_t *config)
{
	/* Set up the mode and configuration register values */
	// Mode selection made later
	// Don't get the status
	*mode = CLK_CLOCK;
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

	start_adcs_clock();
	for (i = 0; i < num_adcs; ++i) {
		adc = &adcs[i];
		if (!adc->working || adc->gain == 0)
			continue;

		compute_mode_and_config(adc, &mode, &config);

		/* Send the configuration information */
		enable_adc_CS(adc);
		spi_send_byte(REG_CONFIGURATION);	// Write the Config reg
		spi_send_3(config);
		disable_adc_CS();
		us_delay(1);

		/* Carry out an internal calibration */
		enable_adc_CS(adc);
		exp_time = millis() + 1000;
		spi_send_byte(REG_MODE);		// Write the Mode reg
		spi_send_3(mode + MODE_INT_ZERO);	// Zero-scale calib
		if (!wait_for_nRDY(exp_time))
			goto timed_out;
		disable_adc_CS();
		us_delay(1);

		enable_adc_CS(adc);
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
		disable_adc_CS();
		us_delay(1);

		if (start && rc) {

			/* Start the continuous conversions */
			enable_adc_CS(adc);
			spi_send_byte(REG_MODE);	// Write the Mode reg
			spi_send_3(mode + MODE_CONTINUOUS);

			/* Begin continuous reading of the Data register */
			spi_send_byte(CR_RnW + REG_DATA + CR_CREAD);
			adc->running = 1;
			disable_adc_CS();
		}

	}

	if (!rc)
		stop_adcs();
	return rc;
}

void stop_adcs(void)
{
	int			i;
	struct adc		*adc;
	unsigned long		exp_time;

	for (i = 0; i < num_adcs; ++i) {
		adc = &adcs[i];
		if (!adc->running)
			continue;

		enable_adc_CS(adc);
		exp_time = millis() + 1000;

		if (wait_for_nRDY(exp_time)) {

			/* Exit the continuous-read mode */
			spi_send_byte(CR_RnW + REG_DATA);
		}
		// If the ADC times out, it needs to be reset

		/* Try to go into idle mode */
		spi_send_byte(REG_MODE);	// Write the Mode register
		spi_send_3(MODE_IDLE + CLK_CLOCK + 1);

		disable_adc_CS();
		adc->running = 0;
	}
	stop_adcs_clock();
}

void synchronize_adcs(void)
{
	/* Set the nSYNC pin low, then high on a CLOCK rising edge */
	portA->OUTCLR.reg = nSYNC_PIN_BIT;

	noInterrupts();		// Delicate timing here
	us_delay(1);
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
	enable_adc_CS(adc);

	/* Carry out a single conversion */
	exp_time = millis() + 1000;
	spi_send_byte(REG_MODE);			// Write the Mode reg
	spi_send_3(mode + MODE_SINGLE);			// Single conversion

	if (!wait_for_nRDY(exp_time)) {
		sprintf(buf, "ADC %d timed out during A/D conversion!\n", i + 1);
		print_buf();
		v = -1;
	} else {
		spi_send_byte(CR_RnW + REG_DATA);	// Read the Data reg
		v1 = spi_read_byte();			// 3 bytes, big-endian
		v2 = spi_read_byte();
		v3 = spi_read_byte();
		v = (v1 << 16) + (v2 << 8) + v3;
	}

	disable_adc_CS();
	return v;
}

void test_adcs_and_button(void)
{
	int		i;
	struct adc	*adc;
	long		v;
	float		x;

	Serial.print("\nTest reading\n");

	if (!set_up_adcs(false))
		goto done_SPI;
	for (i = 0; i < num_adcs; ++i) {
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
		print_buf();
	}
	stop_adcs();

 done_SPI:
	/* Test the pushbutton */
	i = !(portAx->IN.reg & nPB1_PIN_BIT);
	sprintf(buf, "Pushbutton1: %d\n", i);
	print_buf();
}

void wait_for_5_seconds_or_button(void)
{
	int		i;

	for (i = 5000; i > 0; i -= 10) {
		delay(10);
		poll_pushbutton();
		if (pb1.pressed)
			break;
	}
	if (i > 0) {
		for (;;) {
			delay(10);
			poll_pushbutton();
			if (!pb1.pressed)
				break;
		}
	}
}

void measure_Rs(bool adjust_channels)
{
	int		i;
	struct adc	*adc;
	long		v;
	float		Vs, Is;
	int		Rs;
	unsigned int	new_Rds, connected_channels, high_channels;
	uint8_t		old_gains[MAX_ADCS], new_gains[MAX_ADCS];
	unsigned int	old_rate_divisor;

	if (!(Rd_i2c_expander_present || RdDB_i2c_expander_present)) {
		Serial.println("\nResistance measurement not available");
		while (pb1.pressed) {
			poll_pushbutton();
			delay(10);
		}
		return;
	}

	Serial.print("\nMeasuring resistances\n");

	/* Save the gain values and set them to 8 for the measurement */
	for (i = 0; i < num_adcs; ++i) {
		new_gains[i] = old_gains[i] = adcs[i].gain;
		adcs[i].gain = 8;
	}

	/* Save the sampling rate and set it to 100 S/s */
	old_rate_divisor = rate_divisor;
	rate_divisor = SAMPLING_MAX / 100;

	enable_SPI(SPI_ADC);

	/* Turn the LEDs off */
	set_channel_status_leds(0);
	set_Rds(0);

	/* 2-second delay */
	for (i = 0; i < 2000; i += 10) {
		delay(10);
		poll_pushbutton();
		if (pb1.multipress_count >= 2)
			adjust_channels = true;
		if (i % 200 == 0)
			portB->OUTTGL.reg = LD2_PIN_BIT;	// Flash LD2
	}
	portB->OUTSET.reg = LD2_PIN_BIT;

	if (!set_up_adcs(false)) {
		Serial.print("Error initializing ADCs\n");
		goto done;
	}

	/* Turn on the all the Rd's and the test current sources */
	set_Rds(PACK_ALL_Rd_BITS | PACK_50uA_BIT);
	new_Rds = connected_channels = high_channels = 0;

	for (i = 0; i < num_adcs; ++i) {
		adc = &adcs[i];
		if (!adc->working)
			continue;
		v = run_test(i);

		Vs = v / (float) (1 << NUM_DATA_BITS);
		if (adc->polarity == 2)
			Vs = 2.0f * Vs - 1.0f;
		Vs *= REFERENCE_VOLTAGE / adc->gain;	// mV

		if (Vs > NO_SENSOR_MV_BOUNDARY) {
			sprintf(buf, "ADC %d:  voltage %5.1f mV  No sensor\n",
					i + 1, Vs);
			new_gains[i] = 0;
		} else {
			connected_channels |= (1 << i);
			if (Vs < LOW_HIGH_MV_BOUNDARY) {
				Is = 0.0369f;		// mA
			} else {
				Is = 0.0209f;
				new_Rds |= PACK_Rd_BIT(i);
				high_channels |= (1 << i);
			}
			Rs = (int) (Vs / Is + 0.5f);	// Ohms
			sprintf(buf, "ADC %d:  voltage %5.1f mV  Rs %d Ohms\n",
					i + 1, Vs, Rs);
			new_gains[i] = 128;
		}
		print_buf();
	}
	stop_adcs();
	set_Rds(0);		// Turn things back off

	/* Turn on LEDs for the channels with sensors connected */
	set_channel_status_leds(connected_channels);
	wait_for_5_seconds_or_button();

	/* Turn on RdH and LEDs for the channels with high resistance */
	portA->OUTSET.reg = RdH_PIN_BIT;
	set_channel_status_leds(high_channels);
	wait_for_5_seconds_or_button();

	/* Change to the new channel settings? */
	if (adjust_channels) {
		for (i = 0; i < num_adcs; ++i)
			old_gains[i] = new_gains[i];
		Rd_values = new_Rds;
		Serial.print("Channel settings updated\n");
	} else {
		Serial.print("Done\n");
	}

 done:
	/* Restore the original sampling rate and gains */
	rate_divisor = old_rate_divisor;
	for (i = 0; i < num_adcs; ++i)
		adcs[i].gain = old_gains[i];
	show_channel_gain_leds();

	/* Restore the original impedance settings */
	set_Rds(Rd_values);
	portB->OUTCLR.reg = LD2_PIN_BIT;

	disable_SPI();
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
	if (t > EXPT_TIME_MAX) {
		sprintf(buf, "Time too long; setting to %d seconds\n",
				EXPT_TIME_MAX);
		print_buf();
		t = EXPT_TIME_MAX;
	}
	if (t <= 0)
		samples_remaining = -1;
	else
		samples_remaining = t * SAMPLING_MAX / rate_divisor;

	/* Set up the output header */
	memset(&hdr, 0, sizeof(hdr));
	memcpy(hdr.sig, SIGNATURE_STRING, sizeof(hdr.sig));
	hdr.rate_div = rate_divisor;

	num_running_adcs = 0;
	for (i = 0; i < MAX_ADCS; ++i) {
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
	print_buf();

	enable_SPI(SPI_ADC);
	if (!set_up_adcs(true)) {
		disable_SPI();
		goto abort;
	}

	Serial.print("Beginning data collection...\n+");
	Serial.write((uint8_t *) &hdr, sizeof(hdr));

	pout = output_data + 1;
	output_limit = &output_data[OUTPUT_BUF_SIZE - num_running_adcs * 3];
	data_collection_in_progress = true;

	synchronize_adcs();
	data_exp_time = millis() + 1000;
	return;

 abort:
	Serial.print("+-\n");
}

void continue_data_collection(void)
{
	int		i;
	struct adc	*adc;
	uint8_t		*p;

	buf[0] = 0;
	if (Serial.peek() >= 0)
		goto abort;

	if (samples_remaining == 0)
		goto abort;
	if (samples_remaining > 0)
		--samples_remaining;

	p = pout;
	for (i = 0; i < num_adcs; ++i) {
		adc = &adcs[i];
		if (!adc->running)
			continue;

		enable_adc_CS(adc);

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

		disable_adc_CS();
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
	disable_adc_CS();
	data_collection_in_progress = false;

	/* Send possible partial buffer and termination byte */
	i = pout - output_data;
	if (i > 1) {
		output_data[0] = i - 1;
		Serial.write(output_data, i);
	}
	Serial.write((uint8_t) 0);
	
	print_buf();
	Serial.print("\nData collection stopped\n");

	stop_adcs();
	disable_SPI();
}
