import sys
import platform

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import show_message
from luma.core.legacy.font import CP437_FONT

if platform.system() == "Windows":
    from luma.emulator.device import pygame

    device = pygame(width=8, height=8, rotate=0)  # Virtual LED matrix
else:
    from luma.core.interface.serial import spi, noop
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, width=8, height=8, rotate=0)

# Define pixel patterns for each status
STATUS_PATTERNS = {
    "unlocked": [(1, 3), (2, 2), (3, 1), (4, 2), (5, 3)], 
    "rented": [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], 
    "locked": [(2, 2), (2, 5), (5, 2), (5, 5)], 
}

def display_status(status, color):
    with canvas(device) as draw:
        if status in STATUS_PATTERNS:
            for x, y in STATUS_PATTERNS[status]:
                draw.point((x, y), fill=color)

def display_text(message, color="white"):
    show_message(device, message, fill=color, font=CP437_FONT, scroll_delay=0.1)


