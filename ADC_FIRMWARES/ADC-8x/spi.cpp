/* Subroutines for SPI communication */

#include <stdarg.h>
#include "adc-8x.h"

/*
 * SPI uses synchronous communication.  The clock frequency is
 * given by: BAUD = fREF / (2 * fBAUD) - 1 (table 25-2),
 * where fREF is the 48-MHz generic clock.
 */
#define ADC_BAUD	5		// fBAUD = 4 MHz for ADCs
#define FLASH_BAUD	1		// fBAUD = 12 MHz for flash memory

void enable_SPI(enum spi_type st)
{
	/* Set the clock rate */
	switch(st) {
	case SPI_ADC:
		ser_spi->BAUD.reg = ADC_BAUD;
		break;
	case SPI_FLASH:
		ser_spi->BAUD.reg = FLASH_BAUD;
		break;
	}

	/* Enable the SERCOM4 peripheral */
	ser_spi->CTRLA.bit.ENABLE = 1;
	while (ser_spi->SYNCBUSY.reg & SERCOM_SPI_SYNCBUSY_MASK)
		;		// Wait for enable and receiver enable
}

void disable_SPI(void)
{
	/* Disable the SERCOM4 peripheral */
	ser_spi->CTRLA.bit.ENABLE = 0;
	while (ser_spi->SYNCBUSY.reg & SERCOM_SPI_SYNCBUSY_MASK)
		;		// Wait for disable
}

void enable_adc_CS(struct adc *adc)
{
	/* Disable all the CS lines for safety */
	portA->OUTSET.reg = nCS1_PIN_BIT | nCS2_PIN_BIT | nCS3_PIN_BIT |
			nCS4_PIN_BIT | nCS5_PIN_BIT | nCS6_PIN_BIT |
			nCS7_PIN_BIT | nCS8_PIN_BIT;

	/* Enable the CS line for the ADC */
	portA->OUTCLR.reg = adc->nCS_pin_bit;
}

void disable_adc_CS(void)
{
	/* Disable all the CS lines */
	portA->OUTSET.reg = nCS1_PIN_BIT | nCS2_PIN_BIT | nCS3_PIN_BIT |
			nCS4_PIN_BIT | nCS5_PIN_BIT | nCS6_PIN_BIT |
			nCS7_PIN_BIT | nCS8_PIN_BIT;
}

void enable_flash_CS(void)
{
	/* Enable the CS line for the 256-MB flash memory */
	portB->OUTCLR.reg = nCSFM_PIN_BIT;
}

void disable_flash_CS(void)
{
	/* Disable flash memory CS line */
	portB->OUTSET.reg = nCSFM_PIN_BIT;
}

void spi_send_byte(unsigned int val)
{
	ser_spi->DATA.reg = val;
	while (ser_spi->INTFLAG.bit.RXC == 0)
		;			// Wait for data to arrive
	(void) ser_spi->DATA.reg;	// Throw it away
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
	ser_spi->DATA.reg = 0;
	while (ser_spi->INTFLAG.bit.RXC == 0)
		;		// Wait for data to arrive
	return ser_spi->DATA.reg;
}

void spi_send_buffer(const uint8_t *buffer, unsigned int len)
{
	/* Clear INT status */
	ser_spi->INTFLAG.reg = SERCOM_SPI_INTFLAG_MASK;

	for (; len > 0 ; --len) {
		ser_spi->DATA.reg = *buffer++;

		/* Clear out the received byte */
		while (ser_spi->INTFLAG.bit.RXC == 0)
			;               // Wait for data to be ready
		(void) ser_spi->DATA.reg;
        }
}

void spi_read_buffer(uint8_t *buffer, unsigned int len)
{
	/* Clear INT status */
	ser_spi->INTFLAG.reg = SERCOM_SPI_INTFLAG_MASK;
	noInterrupts();			// Don't risk losing data

	/* Send first 0 */
	ser_spi->DATA.reg = 0;

	for (; len > 0 ; --len) {
		if (len > 1) {
			/* Send 0 */
			while (ser_spi->INTFLAG.bit.DRE == 0)
				;       // Wait for data register to be empty
			ser_spi->DATA.reg = 0;
		}
		/* Read the next value */
		while (ser_spi->INTFLAG.bit.RXC == 0)
			;               // Wait for data to be ready
		*buffer++ = ser_spi->DATA.reg;
        }

	interrupts();
}

/*
 * Perform a single SPI transfer of variable type.
 * The first byte sent is opcode.  The remainder of the transfer is
 * described by the specifiers in args. The following specifier characters
 * are accepted:
 *
 * d:	Transfer a dummy byte.
 * 1:	Output a 1-byte value.
 * 2:	Output a 2-byte value.
 * o:	Output a buffer of values (arguments are uint8_t *buf and
 *	unsigned int len).
 * i:	Input a buffer (same arguments as 'o').
 * i1:	Input a 1-byte value.
 * i2:	Input a 2-byte value.
 *
 * The o, i, i1, and i2 specifiers, if present, must occur last in args.
 * If i1 or i2 is specified, the input value is the function's return value.
 * Otherwise the function returns 0.
 */
unsigned int spi_xfer(unsigned int opcode, const char *args, ...)
{
	va_list		ap;
	unsigned int	rc = 0;
	unsigned int	v;
	uint8_t		*buffer;

	enable_flash_CS();
	spi_send_byte(opcode);

	va_start(ap, args);
	while (*args) {
		switch (*args++) {
		case 'd':			// Dummy
			spi_send_byte(0);
			break;
		case '1':			// Send 1-byte value
			spi_send_byte(va_arg(ap, unsigned int));
			break;
		case '2':			// Send 2-byte value
			v = va_arg(ap, unsigned int);
			spi_send_byte(v >> 8);		// Big-endian
			spi_send_byte(v);
			break;
		case 'o':			// Send a buffer
			buffer = va_arg(ap, uint8_t *);
			v = va_arg(ap, unsigned int);
			spi_send_buffer(buffer, v);
			break;
		case 'i':
			if (*args == '1') {		// Receive 1-byte value
				++args;
				rc = spi_read_byte();
			} else if (*args == '2') {	// Receive 2-byte value
				++args;
				rc = spi_read_byte() << 8;
				rc += spi_read_byte();
			} else {			// Receive a buffer
				buffer = va_arg(ap, uint8_t *);
				v = va_arg(ap, unsigned int);
				spi_read_buffer(buffer, v);
			}
			break;
		default:
			break;
		}
	}
	va_end(ap);

	disable_flash_CS();
	return rc;
}
