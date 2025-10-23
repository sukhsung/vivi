/* Include file for the ADC-8x board hardware */

/* Pin definitions */
#define SCK_PIN_BIT		PORT_PB11	// SPI serial clock
#define MOSI_PIN_BIT		PORT_PB10	// SPI data in to peripherals
#define MISO_PIN_BIT		PORT_PA12	// SPI data out from peripherals

#define SCL_PIN_BIT		PORT_PA23	// I2C clock
#define SDA_PIN_BIT		PORT_PA22	// I2C data

#define nCS1_PIN_BIT		PORT_PA14	// Chip select for ADC channel 1
#define nCS2_PIN_BIT		PORT_PA11
#define nCS3_PIN_BIT		PORT_PA08
#define nCS4_PIN_BIT		PORT_PA10
#define nCS5_PIN_BIT		PORT_PA21
#define nCS6_PIN_BIT		PORT_PA20
#define nCS7_PIN_BIT		PORT_PA19
#define nCS8_PIN_BIT		PORT_PA18	// Chip select for ADC channel 8
#define nCSFM_PIN_BIT		PORT_PB03	// Chip select for flash memory

#define nSYNC_PIN_BIT		PORT_PA05	// AD7190 Sync
#define CLOCK_PIN_BIT		PORT_PA04	// AD7190 4.9152-MHz clock signal

#define DAC_PIN_BIT		PORT_PA02	// DAC output for Vc bias
#define Vref_PIN_BIT		PORT_PA03	// Analog voltage reference

#define Vc_0V_PIN_BIT		PORT_PA06	// Vc set to 0 V
#define EnVc_PIN_BIT		PORT_PA09	// Enable off-board sensor power
#define X4_PIN_BIT		PORT_PA13	// Enable on-board Geophone #4
#define EnX_PIN_BIT		PORT_PB23	// Enable AD7190 clock crystal
#define dbC_PIN_BIT		PORT_PB22	// Daughterboard pullup

#define Vbat_PIN_BIT		PORT_PA07	// Battery voltage / 2
#define USBon_PIN_BIT		PORT_PB09	// USB bus power is on
#define Boff_PIN_BIT		PORT_PB08	// Turn off battery power

#define LD1_PIN_BIT		PORT_PA17	// LED1 (= Arduino LED)
#define LD2_PIN_BIT		PORT_PB02	// LED2
#define RdH_PIN_BIT		PORT_PA16	// LED4 (RdH resistance test)
#define LD5_EN_PIN_BIT		PORT_PA28	// Enable for LED5 driver
#define LD5_SEL_PIN_BIT		PORT_PA27	// Select Red/Green for LED5
#define nPB1_PIN_BIT		PORT_PA15	// Pushbutton

#define USBM_PIN_BIT		PORT_PA24	// USB D-
#define USBP_PIN_BIT		PORT_PA25	// USB D+
#define SWCLK_PIN_BIT		PORT_PA30	// Serial-Wire Debugging clock
#define SWDIO_PIN_BIT		PORT_PA31	// Serial-Wire Debugging I/O

/* Unused pins: PA27, PA28 */

/* Testing */
#define DEBUG(x)		PORT_IOBUS->Group[0].OUT##x.reg = SWDIO_PIN_BIT
#define DEBUG2(x)		PORT_IOBUS->Group[0].OUT##x.reg = SWCLK_PIN_BIT


/* Others */
#define REFERENCE_VOLTAGE	2500		// mV
#define NO_SENSOR_MV_BOUNDARY	150
#define LOW_HIGH_MV_BOUNDARY	50

#define MAX_ADCS	8	// Number of ADCs if daughterboard is present
#define NO_DB_ADCS	4	// Likewise if daughterboard is not present

#define X2_START_DELAY		10		// ms for clock crystal start

#define PCA_LED_ADDR		0x18	// Panel LED I2C expander bus address
#define PCA_Rd_ADDR		0x19	// Onboard Rd I2C expander bus address
#define PCA_RdDB_ADDR		0x1a	// Daughterboard Rd I2C expander address

	// Packed RdN bits:	bit 0 is for the 50-µA current sources;
	//			bits 1 - 8 are for Rd1 - Rd8.
#define PACK_50uA_BIT		0x0001
#define PACK_Rd_BIT(i)		(0x0002 << (i))		// Index 0
#define PACK_ALL_Rd_BITS	0x01fe
	// On the PCA chips, Rd1-4 (or 5-8) are bits 1-4 and
	// the current source is bit 5.
#define UNPACK_Rd_BITS(x)	((((x) & 0x0001) << 5) + ((x) & 0x001e))
#define UNPACK_RdDB_BITS(x)	((((x) & 0x0001) << 5) + (((x) & 0x01e0) >> 4))
