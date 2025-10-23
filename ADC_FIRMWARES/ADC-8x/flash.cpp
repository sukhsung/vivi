/* Subroutines to communicate with the flash memory */

#include "adc-8x.h"

uint32_t	w25_jedec_id;
uint8_t		w25_unique_id[W25_UNIQUE_ID_LEN];

uint8_t		attr_len[NUM_ATTRS];
char		attrs[NUM_ATTRS][MAX_ATTR_LEN];
const char	*attr_names[NUM_ATTRS] = {
	"Board serial number", "Board version", "Board fab"
};

unsigned int	block_end;		/* First unusable block number */

int		last_expt_num;
unsigned int	last_expt_start_page, last_expt_end_page;

uint8_t		page_buffer[W25_EXT_PAGE_SIZE];

unsigned int read_flash_status_register(unsigned int addr)
{
	return spi_xfer(W25_READ_STATUS_REG, "1i1", addr);
}

int wait_flash_busy(unsigned long max_us)
{
	unsigned long	us_start;

	max_us += 10;			// Add a little margin
	us_start = micros();
	while (micros() - us_start < max_us) {
		/* Check the BUSY bit in Status Register 3 */
		if (!(read_flash_status_register(W25_SR3_ADDRESS) & W25_BUSY))
			return 0;	// No longer busy
	}
	return 1;			// Timed out -- what can we do now?
}

/* Returns 0 if the page was loaded, does not check ECC */
int load_flash_page(unsigned int page_addr)
{
	spi_xfer(W25_PAGE_DATA_READ, "d2", page_addr);
	return wait_flash_busy(W25_READ_PAGE_DATA_US);	// Wait for the read
}

void store_flash_page(unsigned int page_addr)
{
	spi_xfer(W25_PROGRAM_EXECUTE, "d2", page_addr);
	// Doesn't wait for the command to finish
}

void set_flash_config_reg(unsigned int config)
{
	/* Keep only the specified OPT-enable flag */
	config &= W25_OTP_E;
		// Always set ECC and BUF; we never use Continuous Read Mode
	config |= W25_ECC_E | W25_BUF;

	/* Write the config to Status Register 2 */
	spi_xfer(W25_WRITE_STATUS_REG, "11", W25_SR2_ADDRESS, config);
}

void read_flash_page_buffer(unsigned int len)
{
	/* Read the first len bytes from the page buffer */
	spi_xfer(W25_READ_DATA, "2di", 0, page_buffer, len);
}

void read_flash_spare_buffer(struct spare_area *sp)
{
	/* Read the spare area from the page buffer */
	spi_xfer(W25_READ_DATA, "2di", W25_PAGE_SIZE, sp, sizeof(sp));
}

void write_clear_flash_page_buffer(unsigned int len)
{
	/* Write len bytes to the page buffer, setting the rest to 0xff */
	spi_xfer(W25_LOAD_PROGRAM_DATA, "2o", 0, page_buffer, len);
}

void set_flash_write_enable(void)
{
	spi_xfer(W25_WRITE_ENABLE, "");
}

void init_flash_memory(void)
{
	/* Read the JEDEC IDs */
	spi_xfer(W25_READ_JEDEC_ID, "di", page_buffer, W25_JEDEC_ID_LEN);
	w25_jedec_id = (page_buffer[0] << 16) +
			(page_buffer[1] << 8) + page_buffer[2];

	/* Clear all the protection bits in Status Register 1 */
	spi_xfer(W25_WRITE_STATUS_REG, "11", W25_SR1_ADDRESS, 0);
}

#if 1

void check_flash_pages(void) {}
void get_board_attrs(void) {}

#else

void print_page(const char *name, unsigned int num)
{
	unsigned int	sr3;
	bool		showed_page = false;
	int		i, j;
	char		*p;

	/* Check for CRC error */
	sr3 = read_flash_status_register(W25_SR3_ADDRESS);
	sr3 &= W25_ECC_1_0;
	if (sr3) {
		sprintf(buf, "%s page %d: ECC error %x\n", name, num, sr3);
		print_buf();
		showed_page = true;
	}

	for (i = 0; i < W25_EXT_PAGE_SIZE; i += 16) {
		bool	page_erased = true;

		for (j = 0; j < 16; ++j) {
			if (page_buffer[i+j] != 0xff)
				page_erased = false;
		}

		if (!page_erased) {
			if (!showed_page) {
				sprintf(buf, "%s page %d not erased\n", \
						name, num);
				print_buf();
				showed_page = true;
			}

			p = buf + sprintf(buf, "%4d: ", i);
			for (j = 0; j < 16; ++j) {
				if (j % 4 == 0)
					*p++ = ' ';
				p += sprintf(p, " %02x", page_buffer[i+j]);
			}
			p[0] = '\n';
			p[1] = 0;
			print_buf();
		}
	}
}

void check_flash_pages(void)
{
	/* Enable OTP access */
	set_flash_config_reg(W25_OTP_E);

	if (load_flash_page(W25_OTP_PAGE_0) != 0) {
		Serial.print("Error loading OTP page 0\n");
	} else {
		read_flash_page_buffer(W25_EXT_PAGE_SIZE);
		print_page("OTP", 0);
	}

	/* Disable OTP access */
	set_flash_config_reg(0);
//	for (unsigned int pg = 0; pg < W25_NUM_PAGES; ++pg) {
	for (unsigned int pg = 0; pg < 10; ++pg) {
		if (pg % 1000 == 0)
			Serial.println(pg);
		if (load_flash_page(pg) != 0) {
			Serial.print("Error loading normal page");
			Serial.println(pg);
		} else {
			read_flash_page_buffer(W25_EXT_PAGE_SIZE);
			print_page("Normal", pg);
		}
	}
}

void get_and_store_board_attrs(void)
{
	int		a;
	bool		ok;
	char		*p;
	unsigned int	n;
	uint8_t		*q;
	char		new_attrs[NUM_ATTRS][MAX_ATTR_LEN];

 restart:
	for (a = 0; a < NUM_ATTRS; ++a) {
		p = buf + sprintf(buf, "  Enter new %s", attr_names[a]);
		if (*attrs[a])
			p += sprintf(p, "[default is %s]", attrs[a]);
		sprintf(p, ": ");
		print_buf();

		read_utf8_string(new_attrs[a], MAX_ATTR_LEN, true);
		Serial.println();
		if (!*new_attrs[a])
			strcpy(new_attrs[a], attrs[a]);
	}
	Serial.println();

	for (a = 0; a < NUM_ATTRS; ++a) {
		sprintf(buf, "  %s: %s\n", attr_names[a], new_attrs[a]);
		print_buf();
	}
	Serial.print("Is this correct (y/n)?\n");

	ok = false;
	for (;;) {
		a = Serial.read();
		if (a == 'y' || a == 'Y')
			ok = true;
		else if (a == '\n')
			break;
	}
	if (!ok) {
		Serial.println();
		goto restart;
	}

	q = page_buffer;
	for (a = 0; a < NUM_ATTRS; ++a) {
		strcpy(attrs[a], new_attrs[a]);
		n = strlen(attrs[a]);
		if (n > 0) {
			*q++ = '0' + a;
			memcpy(q, attrs[a], n);
			q += n;
			*q++ = '\n';
		}
	}
	if (q > page_buffer) {
		set_flash_write_enable();
		write_clear_flash_page_buffer(q - page_buffer);
		set_flash_write_enable();
		store_flash_page(W25_OTP_PAGE_0);
		if (wait_flash_busy(W25_PAGE_PROGRAM_US))
			Serial.print("Error storing board attributes!\n");
	} else {
		Serial.print("No board attributes stored\n");
	}

	Serial.println();
}

/* OTP access (W25_OTP_E) must be enabled */
void get_board_attrs(void)
{
	int		i, j, a, c;

	/* Read the first OTP page */
	if (load_flash_page(W25_OTP_PAGE_0) != 0) {
		Serial.print("Error loading OTP page 0\n");
		return;
	}
	read_flash_page_buffer(W25_PAGE_SIZE);

	/* Add sentinels */
	page_buffer[W25_PAGE_SIZE] = page_buffer[W25_PAGE_SIZE + 1] = 0xff;

	/* Parse and store the board attributes */
	a = j = -1;
	for (i = 0; i < W25_PAGE_SIZE; ++i) {
		c = page_buffer[i];
		if (c == 0xff)		// End of the attribute data
			break;
		if (j < 0) {		// Start of next attribute
			j = 0;
			a = c - '0';
			if (a >= NUM_ATTRS)
				a = -1;
		} else {		// Attribute character
			if (c < 32) {
				j = -1;		// End of the attr
			} else if (a >= 0 && j < MAX_ATTR_LEN - 1) {
				attrs[a][j++] = c;
				attrs[a][j] = 0;
			}
			// Ignore invalid data
		}
	}

	/* If no attributes are set, ask for them */
	for (a = 0; a < NUM_ATTRS; ++a) {
		if (attrs[a][0])
			break;
	}
	if (a >= NUM_ATTRS) {
		Serial.print("No board attributes are set.\n");
		get_and_store_board_attrs();
	}
}

#endif

void read_flash_unique_id_and_attrs(void)
{
	/* Enable OTP access */
	set_flash_config_reg(W25_OTP_E);

	/* Read the Unique ID page */
	if (load_flash_page(W25_UNIQUE_ID_PAGE) != 0) {
		Serial.print("Flash load Unique ID page failed!\n");
	} else {
		/* Read the Unique ID from the page buffer */
		read_flash_page_buffer(W25_UNIQUE_ID_LEN);
		memcpy(w25_unique_id, page_buffer, W25_UNIQUE_ID_LEN);
	}

	get_board_attrs();

	/* Disable OTP access */
	set_flash_config_reg(0);

	check_flash_pages();
}

#if 1

void scan_for_bad_blocks(void) {}
void mark_bad_block(int blocknum) {}
void scan_datasets(void) {}

#else

bool block_marked_bad(unsigned int blocknum)
{
	unsigned int	marker;

	/* Read the first page of the block */
	if (load_flash_page(blocknum * W25_PAGES_PER_BLOCK))
		return true;		// If we can't load it, it must be bad

	/* Check the first two bytes of the Spare area (the bad block marker) */
	marker = spi_xfer(W25_READ_DATA, "2di2", W25_PAGE_SIZE);
	return marker != 0xffff;
}

void scan_for_bad_blocks(void)
{
	struct bbm_lut_entry {
		unsigned int	lba, pba;
	}		bbm_lut[W25_NUM_BBM_ENTRIES];
	int		i, j;
	unsigned int	lba, pba, status, num_free_entries;
	unsigned int	min_pba, next_pba, blocknum;

	/* Read in the Bad Block Management Look-Up Table */
	spi_xfer(W25_READ_BBM_LUT, "di", page_buffer, W25_BBM_SIZE);

	/* Convert and store the entries */
	next_pba = min_pba = W25_NUM_BLOCKS;
	num_free_entries = 0;
	for ((i = 0, j = 0); i < W25_NUM_BBM_ENTRIES; (++i, j += 4)) {
		lba = (page_buffer[j] << 8) + page_buffer[j+1];
		pba = (page_buffer[j+2] << 8) + page_buffer[j+3];
		status = lba & W25_BBM_STATUS_MASK;
		lba &= ~W25_BBM_STATUS_MASK;
		switch (status) {
		case W25_BBM_STATUS_EMPTY:
			bbm_lut[i].lba = bbm_lut[i].pba = 0xffff;
			++num_free_entries;
			break;
		case W25_BBM_STATUS_VALID:
		case W25_BBM_STATUS_INVALID:
			bbm_lut[i].lba = lba;
			bbm_lut[i].pba = pba;
			if (pba < min_pba)
				min_pba = pba;
			break;
		default:
			break;
		}
	}

	/*
	 * Scan for blocks marked bad.  We only look at blocks below the
	 * lowest target PBA; blocks after that are reserved for remapping.
	 */
	for (blocknum = 0; blocknum < min_pba; ++blocknum) {
		if (!block_marked_bad(blocknum))
			continue;

		sprintf(buf, "Found bad block at %d\n", blocknum);
		print_buf();

		/* If there are no free entries, we can't do the mapping */
		if (num_free_entries == 0) {
			Serial.print("The BBM LUT is full\n");
			break;
		}

		/* Look for the next block available to be a target PBA */
		while (--next_pba > blocknum) {
			/* Don't use a block if it's already in the BBM LUT */
			for (i = 0; i < W25_NUM_BBM_ENTRIES; ++i) {
				if (next_pba == bbm_lut[i].lba ||
						next_pba == bbm_lut[i].pba)
					break;
			}
			/* Otherwise, use a block if it's not marked bad */
			if (i == W25_NUM_BBM_ENTRIES &&
					!block_marked_bad(next_pba))
				break;
			sprintf(buf, "Block %u already in LUT or marked bad\n",
						next_pba);
			print_buf();
		}

		/*
		 * If the first available PBA is already below blocknum
		 * then we can't do the mapping.
		 */
		if (next_pba <= blocknum) {
			Serial.print("No PBA available for remapping\n");
			break;
		}

		sprintf(buf, "Mapping to block %d\n", next_pba);
		print_buf();

#if 1
		set_flash_write_enable();
		spi_xfer(W25_BAD_BLOCK_MANAGEMENT, "22", blocknum, next_pba);
		if (wait_flash_busy(W25_BAD_BLOCK_MANAGEMENT_US))
			Serial.print("Error writing BBM LUT entry!\n");
#endif

		--num_free_entries;
		if (next_pba < min_pba)
			min_pba = next_pba;
	}

	/* Keep track of the first block we can't use */
	block_end = blocknum;
	sprintf(buf, "Number of usable flash memory blocks: %u / %u\n",
			block_end, W25_NUM_BLOCKS);
	print_buf();
}

/* For TESTING only! */
void mark_bad_block(int blocknum)
{
	unsigned int	pageaddr;
	int		r;

	if (blocknum <= 0 || blocknum >= 1024) {
		sprintf(buf, "Invalid block number: %u\n", blocknum);
		print_buf();
		return;
	}
	pageaddr = blocknum * W25_PAGES_PER_BLOCK;

	/* Turn ECC off and BUF on */
	spi_xfer(W25_WRITE_STATUS_REG, "11", W25_SR2_ADDRESS, W25_BUF);

	/* Set the first byte of the page buffer to 0 and all others to 0xff */
	spi_xfer(W25_LOAD_PROGRAM_DATA, "21", 0, 0);
					// Column address and data

	/* Set the first byte of the spare area to 0 */
	spi_xfer(W25_RANDOM_LOAD_PROGRAM_DATA, "21", W25_PAGE_SIZE, 0);

	/* Store the page buffer */
	set_flash_write_enable();
	spi_xfer(W25_PROGRAM_EXECUTE, "d2", pageaddr);

	r = wait_flash_busy(W25_PAGE_PROGRAM_US);
					// Wait for the page program
	sprintf(buf, "Block %u mark bad: %d\n", blocknum, r);
	print_buf();

	set_flash_config_reg(W25_BUF);
}

void scan_datasets(void)
{
	int			expt_num, delta;
	unsigned int		total_size, page_addr;
	unsigned int		range_start, range_size, range_incr;
	struct oob_0		*oob0;
	struct spare_area	spare;

	oob0 = (struct oob_0 *) &(spare.ssp[0].user_data2);

	/* Find the end page of the most recent experiment by binary search */
	range_start = 0;
	range_size = total_size = block_end * W25_PAGES_PER_BLOCK;

	last_expt_num = -1;
	while (range_size > 0) {
		range_incr = range_size / 2;
		page_addr = range_start + range_incr;
		if (page_addr > total_size)	// Circular storage access
			page_addr -= total_size;
		if (load_flash_page(page_addr))
			goto Error;

		read_flash_spare_buffer(&spare);
		expt_num = oob0->expt_num[0] + (oob0->expt_num[1] << 8) +
				(oob0->expt_num[2] << 24);
		if (oob0->marker == 0xff || expt_num > MAX_EXPT_NUM) {
			// Page not in use, must be beyond the end
			delta = -1;
		} else if (last_expt_num < 0) {
			delta = 1;
			if (range_size == total_size)
				range_incr = 0;
		} else {
			delta = expt_num - last_expt_num;
			if (delta > MAX_EXPT_NUM / 2)
				delta -= MAX_EXPT_NUM;
			else if (delta < - MAX_EXPT_NUM / 2)
				delta += MAX_EXPT_NUM;
		}

		if (delta < 0) {		// Beyond the wrap point
			range_size = range_incr;
		} else {
			last_expt_num = expt_num;
			last_expt_end_page = page_addr;
			range_start = page_addr;
			range_size -= range_incr;
		}
	}

	if (last_expt_num < 0) {
		Serial.print("No experiments found in flash memory\n");
		return;
	}


	/* Find the start page of the most recent experiment by binary search */
	last_expt_start_page = total_size;
	range_start = last_expt_end_page + 1;
	range_size = total_size;

	while (range_size > 0) {
		range_incr = range_size / 2;
		page_addr = range_start + range_incr;
		if (page_addr > total_size)	// Circular storage access
			page_addr -= total_size;
		if (load_flash_page(page_addr))
			goto Error;

		read_flash_spare_buffer(&spare);
		expt_num = oob0->expt_num[0] + (oob0->expt_num[1] << 8) +
				(oob0->expt_num[2] << 24);

		if (expt_num == last_expt_num) {
			if (oob0->marker == 0) {
				last_expt_start_page = page_addr;
				break;
			}
			range_size = range_incr;
		} else {
			range_start = page_addr + 1;
			range_size -= range_incr + 1;
		}
	}

	if (last_expt_start_page >= total_size) {
		Serial.print("Unable to locate start of last experiment"
				" in flash memory\n");
		last_expt_num = -1;
		return;
	}

	sprintf(buf, "Last experiment number is %d, using %d KB"
			" of flash memory\n", last_expt_num,
			(last_expt_end_page - last_expt_start_page + 1)
				* (W25_PAGE_SIZE / 1024));
	print_buf();
	return;

 Error:
	sprintf(buf, "Error reading page %u of flash memory!\n", page_addr);
	print_buf();
}

#endif
