#! /usr/bin/python3
# Copyright (c) 2020 Richard Ulrich <richi@ulrichard.ch>
import time, datetime

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

import yfinance as yf

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess
import httplib2
import json

# Get the BTC price
h = httplib2.Http(".cache") 
h.debuglevel = 2 
resp, usdprice = h.request('https://api.coingate.com/v2/rates/merchant/BTC/USD', "GET")
resp, chfprice = h.request('https://api.coingate.com/v2/rates/merchant/BTC/CHF', "GET")
tsla = yf.Ticker("TSLA")
tslaprice = tsla.info['bid']
now = datetime.datetime.now()


# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

# 128x32 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

# 128x64 display with hardware I2C:
# disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# Load default font.
font = ImageFont.load_default()

draw.text((0, -2), "BTC: " + usdprice.decode("utf-8") + " USD",  font=font, fill=255)
draw.text((0, 6),  "BTC: " + chfprice.decode("utf-8") + " CHF",  font=font, fill=255)
draw.text((0, 14), "TSLA: " + str(tslaprice) + " USD",  font=font, fill=255)
draw.text((0, 23), now.strftime('%Y-%m-%d %H:%M:%S'),  font=font, fill=255)

# Display image.
disp.image(image)
disp.display()
