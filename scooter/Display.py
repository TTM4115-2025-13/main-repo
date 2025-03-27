
from sense_hat import SenseHat
sense = SenseHat()

# Define pixel patterns for each status
STATUS_PATTERNS = {
    "unlocked": [(1, 3), (2, 2), (3, 1), (4, 2), (5, 3)], 
    "rented": [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], 
    "locked": [(2, 2), (2, 5), (5, 2), (5, 5)], 
}

# Default off color (black)
OFF_COLOR = (0, 0, 0)

def display_status(status, color):
    """Displays a status pattern on the Sense HAT."""
    pixels = [OFF_COLOR] * 64  # 8x8 grid

    if status in STATUS_PATTERNS:
        for x, y in STATUS_PATTERNS[status]:
            pixels[y * 8 + x] = color  # Convert (x, y) to 1D index

    sense.set_pixels(pixels)

def display_text(message, color="white"):
    sense.show_message(message, text_colour=color)


