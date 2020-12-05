# coding: utf8

"""
    Steganography module allowing to insert text UTF-8 encoded 
    in raster images by replacing bits. The number of replaced 
    bits / byte is dynamically determined .
"""

import imghdr
from math import ceil
from PIL import Image
import numpy as np

def decimalisation(code, axe):
    """
        Packs the reversed elements of a binary-valued array and returns 
        a one-dimensional integers (uint8) array.
    """
    ar = np.flip(code, axis=axe)
    return np.packbits(ar, axis=axe, bitorder='little').ravel()

# Select the image and record the pixel array

formats = ['png', 'bmp', 'tiff', 'ppm', 'pgm', 'pnm', 'pcx', 'sgi', 'tga']

pict = "some_image.png" # image's path
with Image.open(pict) as im:
     if (imghdr.what(pict) or im.format.lower()) not in formats:
        raise TypeError("This format is not valid.")
     else:
        im_array = np.array(im)
       
# Text encoding

with open ('some_text.txt', 'r', encoding='utf8') as f: # local text
    message = f.read()    

## or smth like that:
# message = 'All work and no play makes Jack a dull boy\n' * 8000

octets = bytes(message, 'utf8')  # converting characters to UTF-8 encoded bytes
octets_dec = np.frombuffer(octets, dtype=np.uint8) # convert bytes to digits (base 10)
octets_bin = np.unpackbits(octets_dec) # base 10 to 2, split into one-bit elements

# Header size and useful image size

header_size = 1 + ceil(len(f'{im_array.size:b}') / 4)
im_size = im_array.size - header_size # useful size (in bytes)

# Determine how many bits per byte should be replaced (nbits)

for nbits in range(1, 9): # bytes groups
    if im_size >= len(octets) * 8/nbits:
        break # loop output because the minimum nbits is found
else:
    raise ValueError("Text too long for this image") # too long even with nbits = 8

if nbits == 8: # all pixels have been replaced
    print("*"*60, "\nWarning: The sizes are compatible but the image will be \
          completely overwritten by the text."
          "\nFor best result, choose a larger image.")
    print("*"*60)
    
# Display nbits and used bit rate (optional)

print("Number of replaced bits per byte:", nbits)
print('Used bits rate: ', round(len(octets) * 100 / im_size, 2), '%')

# Distribute text code's bits by groups of nbits

if octets_bin.size % nbits :  # is not a multiple of nbits -> padding
    masque = np.zeros(nbits * ceil(octets_bin.size / nbits), dtype=np.uint8)
    masque[:octets_bin.size] = octets_bin
    octets_bin = masque
    
code_txt = octets_bin.reshape(-1, nbits)
code_txt = decimalisation(code_txt, 1)

# Header extraction

header = im_array.flatten()[:header_size]

# Reset of the least significant bits (LSB)

header -= header & (2**4 - 1)  # reset of the 4 LSB of the header's bytes
im_array -= im_array & (2**nbits - 1) # nbits reset of other array's bytes

# Header writing

header_code = f'{nbits:04b}' + f'{code_txt.size:0{4 * (header_size - 1)}b}'
header_code = np.array(list(header_code), dtype=np.uint8).reshape(-1, 4)
header_code = decimalisation(header_code, 1)

# Merging text and image codes

im_array.ravel()[:header_size] = header + header_code
im_array.ravel()[header_size:header_size+code_txt.size] += code_txt

# Saving the encoded image

im = Image.fromarray(im_array)
im.save(f'code_{pict}') # path image + code
