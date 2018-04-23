#include <stdint.h>

/* The state word must be initialized to non-zero */
uint32_t xorshift32(uint32_t state[static 1])
{
	/* Algorithm "xor" from p. 4 of Marsaglia, "Xorshift RNGs" */
	uint32_t x = state[0];
	x ^= x << 13;
	x ^= x >> 17;
	x ^= x << 5;
	state[0] = x;
	return x;
}

/* The state array must be initialized to not be all zero */
uint32_t xorshift128(uint32_t state[static 4])
{
	/* Algorithm "xor128" from p. 5 of Marsaglia, "Xorshift RNGs" */
	uint32_t s, t = state[3];
	t ^= t << 11;
	t ^= t >> 8;
	state[3] = state[2]; state[2] = state[1]; state[1] = s = state[0];
	t ^= s;
	t ^= s >> 19;	
	state[0] = t;
	return t;
}