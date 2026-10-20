/* Regression for the actual sdl/interrpt.c key table. GPL-2.0-or-later. */
#include "globals.h"

int main(void)
{
    /* SDL_SCANCODE_AUDIONEXT=258 must not alias scancode 2 when read. */
    const int high = SDL_SCANCODE_AUDIONEXT;
    const int low = high & 0xff;
    assert(high >= 256 && high < SDL_NUM_SCANCODES);
    assert(addkey(low) == 0);
    assert(key_pressed(low) == 1);
    assert(key_pressed(high) == 0);
    assert(addkey(low | 0x8000) == 0);
    assert(addkey(high) == 0);
    assert(key_pressed(high) == 1);
    assert(key_pressed(low) == 0);
    assert(addkey(high | 0x8000) == 0);
    assert(key_pressed(high) == 0);

    assert(addkey(SDL_NUM_SCANCODES - 1) == 0);
    assert(key_pressed(SDL_NUM_SCANCODES - 1) == 1);
    assert(addkey((SDL_NUM_SCANCODES - 1) | 0x8000) == 0);
    assert(key_pressed(SDL_NUM_SCANCODES - 1) == 0);
    assert(addkey(SDL_NUM_SCANCODES) == -1);
    assert(addkey(SDL_NUM_SCANCODES | 0x8000) == -1);
    assert(addkey(0x7fff) == -1);
    assert(key_pressed(-1) == 0);
    assert(key_pressed(SDL_NUM_SCANCODES) == 0);
    assert(key_pressed(0x7fff) == 0);
    puts("scancode press/release, non-aliasing and bounds: PASS");
    return 0;
}
