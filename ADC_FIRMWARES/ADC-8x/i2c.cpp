/* Subroutines for I2C communication */

#include "adc-8x.h"


bool		led_i2c_expander_present;
bool		Rd_i2c_expander_present;
bool		RdDB_i2c_expander_present;
uint8_t		i2c_addr;

void i2c_start(int address)
{
	/* Save the I2C address for later use */
	i2c_addr = address;

	/* Set up SERCOM3's generic clock */
	gclk->CLKCTRL.reg = GCLK_CLKCTRL_ID_SERCOM3_CORE;	// Disable
	gclk->CLKCTRL.reg = GCLK_CLKCTRL_ID_SERCOM3_CORE |
			GCLK_CLKCTRL_GEN_GCLK0 | GCLK_CLKCTRL_CLKEN;
	while (gclk->STATUS.bit.SYNCBUSY)
		;	// Wait for synchronization

	/* Configure the SERCOM3 peripheral for I2C */
	ser_i2c->CTRLA.reg = 			// Fast-Mode (400 KHz) speed
			SERCOM_I2CM_CTRLA_MODE_I2C_MASTER;

	/*
	 * The clock frequency is given by:
	 *	fSCL = fGCLK / (10 + 2 BAUD + fGCLK * Trise).
	 * Assume Trise is 0.  We want fSCL to be <= 400 KHz (the maximum
	 * for Fast-Mode, and fGCLK is 48 MHz.  This gives BAUD = 55.
	 */
	ser_i2c->BAUD.reg = SERCOM_I2CM_BAUD_BAUD(55);
	ser_i2c->CTRLA.bit.ENABLE = 1;		// Enable the controller
	while (ser_i2c->SYNCBUSY.bit.ENABLE)
		;	// Wait for the enable

	/* Switch the SCL and SDA pins to peripheral function C (SERCOM) */
	portAx->WRCONFIG.reg = PORT_WRCONFIG_HWSEL |	// Pin #s >= 16
			PORT_WRCONFIG_WRPINCFG |	// Write pin config
			PORT_WRCONFIG_WRPMUX |		// Write pin MUX
			PORT_WRCONFIG_PMUX(PORT_PMUX_PMUXE_C_Val) |
							// Peripheral C
					// Pullup and input disabled
			PORT_WRCONFIG_PMUXEN |		// Periph MUX enabled
			PORT_WRCONFIG_PINMASK((SCL_PIN_BIT | SDA_PIN_BIT)
					>> 16);

	/*
	 * The I2C bus has no other bus masters.  It's safe to tell
	 * the controller that the bus is idle.
	 */
	ser_i2c->STATUS.reg = SERCOM_I2CM_STATUS_BUSSTATE(1);	// Idle state
	while (ser_i2c->SYNCBUSY.bit.SYSOP)
		;	// Wait for synchronization
}

void i2c_stop(void)
{
	/* Turn off the GPIO pins' peripheral function */
	portAx->WRCONFIG.reg = PORT_WRCONFIG_HWSEL |	// Pin #s >= 16
			PORT_WRCONFIG_WRPINCFG |	// Write pin config
					// Pull, input, and MUX disabled
			PORT_WRCONFIG_PINMASK((SCL_PIN_BIT | SDA_PIN_BIT)
					>> 16);

	/* Disable SERCOM3 */
	ser_i2c->CTRLA.bit.ENABLE = 0;		// Disable the controller
	while (ser_i2c->SYNCBUSY.bit.ENABLE)
		;	// Wait for the disable

	/* Turn off SERCOM3's generic clock */
	gclk->CLKCTRL.reg = GCLK_CLKCTRL_ID_SERCOM3_CORE;	// Disable
	while (gclk->STATUS.bit.SYNCBUSY)
		;	// Wait for synchronization
}

int i2c_wait_for_byte(void)
{
	unsigned long	ms;

	ms = millis();
	for (;;) {				// Wait for the result
		if (millis() - ms > 2)		// No more than 2 ms
			return ETIMEOUT;
		if (ser_i2c->INTFLAG.reg & (SERCOM_I2CM_INTFLAG_MB |
				SERCOM_I2CM_INTFLAG_SB))
			break;
	}
	if (ser_i2c->STATUS.reg & (SERCOM_I2CM_STATUS_BUSERR |
			SERCOM_I2CM_STATUS_ARBLOST))
		return EOTHER;
	if (ser_i2c->STATUS.bit.RXNACK) {
		ser_i2c->CTRLB.reg = SERCOM_I2CM_CTRLB_CMD(3);
						// Send Stop
		while (ser_i2c->SYNCBUSY.bit.SYSOP)
			;	// Wait for synchronization
		us_delay(5);	// Wait for Stop
		return ENOACK;
	}
	return 0;
}

int i2c_raw_write(void *_wbuf, unsigned int len)
{
	uint8_t		*wbuf = (uint8_t *) _wbuf;
	int		rc;

	/* Start a transaction by sending the device address */
	ser_i2c->ADDR.reg = SERCOM_I2CM_ADDR_ADDR(i2c_addr << 1);
			// Low bit is 0 for write; 10-bit not supported
	rc = i2c_wait_for_byte();
	if (rc)
		return rc;

	/* Send the data bytes */
	while (len > 0) {
		ser_i2c->DATA.reg = *wbuf++;
		rc = i2c_wait_for_byte();
		if (rc)
			return rc;
		--len;
	}

	ser_i2c->CTRLB.reg = SERCOM_I2CM_CTRLB_CMD(3);		// Send Stop
	while (ser_i2c->SYNCBUSY.bit.SYSOP)
		;	// Wait for synchronization
	us_delay(5);	// Wait for Stop
	return rc;
}

int i2c_write_reg(uint8_t reg, uint8_t value)
{
	uint8_t		wbuf[2];

	wbuf[0] = reg;
	wbuf[1] = value;
	return i2c_raw_write(wbuf, 2);
}

void set_channel_status_leds(unsigned int leds)
{
	i2c_start(PCA_LED_ADDR);
	i2c_write_reg(PCA_CTRL_OUTPUT, ~leds);	// LED values are inverted
	i2c_stop();
}

void show_channel_gain_leds(void)
{
	int		i;
	unsigned int	v;
	struct adc	*adc;

	if (!led_i2c_expander_present)
		return;

	v = 0;
	for (i = 0; i < num_adcs; ++i) {
		adc = &adcs[i];
		if (adc->working && adc->gain > 0)
			v |= 1 << i;		// Channel is enabled
	}
	set_channel_status_leds(v);
}
