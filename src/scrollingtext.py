import neopixel
import board
import bitmapfont
import time
import random

POS = 32
WIDTH = 32
HEIGHT = 8

matrix = neopixel.NeoPixel(board.D21, 256, brightness=0.05, auto_write=False, pixel_order=neopixel.GRB)

#Do not light LED if it is outside of the matrix range
def checkEdges(xpos, ypos):
    #TODO: Clean up, create algorithm
    if (ypos < 0 or ypos > HEIGHT - 1 or xpos < 0 or xpos > WIDTH - 1):
        return False
    else: return True

#Controller for lighting LEDs
def matrix_pixel(x, y, color):
    if (y % 2 != 0):
        x = WIDTH - 1 - x
    led = y * WIDTH + x

    if (checkEdges(x, y)):
        matrix[led] = color

def clear():
    matrix.fill(0)
    matrix.show()

def display(message):
    
    POS = 32
    
    with bitmapfont.BitmapFont(WIDTH, HEIGHT, matrix_pixel) as bf:
        r = random.randint(15, 50)
        g = random.randint(15, 50)
        b = random.randint(15, 50)
        
        while POS > -(len(message) * 6) :
            POS -= 1
            matrix.fill(0)
            bf.text(message, int(POS), 0, (r, g, b))
            matrix.show()
