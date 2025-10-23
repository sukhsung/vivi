/* Utility functions for timed delays */

inline void tick_delay(int nticks) __attribute__((always_inline));
inline void tick_delay(int nticks)
{
	/*
	 * The following code:
	 *
	 *	do {
	 *		nticks -= 3;
	 *	} while (nticks > 0);
	 *
	 * produces the following assembly code:
	 *
	 * loop:
	 *	sub r0, #3	// 1 cycle
	 *	bgt loop	// 1 cycle + 1 if branch is taken
	 */

	__asm__ __volatile__ (
	"1:			\n"
	"   sub %0, #3		\n" // subtract 3 from %0 (nticks)
	"   bgt 1b		\n" // if result is > 0, jump to 1
	: "+r" (nticks)      	    // '%0' is nticks with RW access
	:               	    // no input
	:               	    // no clobber
	);
}

inline void us_delay(volatile int us) __attribute__((always_inline));
inline void us_delay(volatile int us)
{
	/*
	 * Overhead of load & multiply is 2 cycles;
	 * subtraction adds a third cycle
	 */
	tick_delay(us * (VARIANT_MCK / 1000000) - 3);
}
