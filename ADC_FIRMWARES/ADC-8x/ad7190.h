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
