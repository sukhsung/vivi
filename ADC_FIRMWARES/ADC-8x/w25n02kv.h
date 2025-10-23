/* Definitions for the W25N02KV 256-MB flash memory chip */

#define W25_PAGE_SIZE			2048
#define W25_EXTRA_SIZE			128
#define W25_EXT_PAGE_SIZE		(W25_PAGE_SIZE + W25_EXTRA_SIZE)
#define W25_NUM_BLOCKS			2048
#define W25_PAGES_PER_BLOCK		64
#define W25_SECTORS_PER_PAGE		4
#define W25_NUM_PAGES			(W25_NUM_BLOCKS * W25_PAGES_PER_BLOCK)

#define W25_PAGE_PROGRAM_US		700	// Max times
#define W25_READ_PAGE_DATA_US		60	// With ECC enabled
#define W25_BLOCK_ERASE_US		10000
#define W25_RESUME_US			1500

#define W25_BLOCK_ERASE			0xd8
#define W25_DEEP_POWER_DOWN		0xb9
#define W25_LOAD_PROGRAM_DATA		0x02
#define W25_PAGE_DATA_READ		0x13
#define W25_PROGRAM_EXECUTE		0x10
#define W25_RANDOM_LOAD_PROGRAM_DATA	0x84
#define W25_READ_DATA			0x03
#define W25_READ_JEDEC_ID		0x9f
#define W25_READ_STATUS_REG		0x05
#define W25_RELEASE_POWER_DOWN		0xab
#define W25_WRITE_STATUS_REG		0x01
#define W25_WRITE_ENABLE		0x06

#define W25_JEDEC_ID_LEN		3
#define W25_JEDEC_ID_VALUE		0xefaa22
//#define W25_JEDEC_ID_VALUE		0xefaa21	// W25N01GV 128-MB chip

/* Status Register 1 (Protection register) */
#define W25_SR1_ADDRESS			0xa0
#define W25_SRP0			(1 << 7)
// Protection bits BP3 - BP0, TB, and WP_E not used
#define W25_SRP1			(1 << 0)

/* Status Register 2 (Configuration register) */
#define W25_SR2_ADDRESS			0xb0
#define W25_OTP_L			(1 << 7)
#define W25_OTP_E			(1 << 6)
// SR1_L not used
#define W25_ECC_E			(1 << 4)
#define W25_BUF				(1 << 3)
// Bits 2 - 0 reserved

/* Status Register 3 (Status register) */
#define W25_SR3_ADDRESS			0xc0
// Bits 7-6 reserved
#define W25_ECC_1_0			(3 << 4)
#define W25_P_FAIL			(1 << 3)
#define W25_E_FAIL			(1 << 2)
#define W25_WEL				(1 << 1)
#define W25_BUSY			(1 << 0)

/* ECC feature registers not used */

#define W25_UNIQUE_ID_PAGE		0
#define W25_UNIQUE_ID_LEN		32
#define W25_OTP_PAGE_0			2
#define W25_NUM_OTP_PAGES		10

/* Extended page structure */
struct user_area {
	uint8_t		bad_block[2];
	uint8_t		data2[2];		// Not ECC-protected
	uint8_t		data1[12];
};
struct spare_area {
	struct user_area	user[W25_SECTORS_PER_PAGE];
	uint8_t			parity[16 * W25_SECTORS_PER_PAGE];
};
