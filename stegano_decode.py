# coding: utf8

"""
    Steganography module allowing to insert text UTF-8 encoded 
    in raster images by replacing bits. The number of replaced 
    bits / byte is dynamically determined .
    This second script allows to decode the images which were encoded 
    with stegano_code.py (first script).
"""

from math import ceil
from PIL import Image
import numpy as np

# Open the image and save pixels

im_array = np.array(Image.open('code_some_image.png'))

# Reading header

head_binsize = len(f'{im_array.size:b}')
head_size = ceil(head_binsize / 4) + 1 # size in bytes

header = im_array.ravel()[:head_size]
header = header & (2**4 - 1) # equivalent to 'header % 2**4'

# Picking informations

nbits = header[0] # number of used bits per byte
bin_code_size = ''.join(f'{c:04b}' for c in header[1:]) # binary value of the message length
code_size = int(bin_code_size, 2) # same value in base 10

# Convert text code into binary values

im_array = im_array & (2**nbits - 1)
im_array = im_array.reshape(-1, 1)[head_size:head_size + code_size]
code_txt = np.unpackbits(im_array, axis=1)

# Concatenation of bits by nbits-groups

code_txt = np.packbits(code_txt[:, 8-nbits:])
code_txt = np.trim_zeros(code_txt, 'b') # remove any null bytes

# Decoding bytes and converting to characters

try:
    message = bytes(code_txt).decode('utf8')
        
except UnicodeDecodeError:
    print("This image does not contain code or the code is unreadable.")
    
else:
    # if save to file:
    with open('new_text.txt', 'w') as f: 
        f.write(message)
    # if print:
    # print(message) 

