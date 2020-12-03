# coding: utf8

"""
    Steganography module allowing to insert text encoded in UTF-8
    in raster images by replacing bits. The number of bits / byte 
    replaced is determined dynamically.
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

# Sélection d'une image et enregistrement tableau de pixels

formats = ['png', 'bmp', 'tiff', 'ppm', 'pgm', 'pnm', 'pcx', 'sgi', 'tga']

pict = "some_image.png" # adresse locale de l’image préalablement téléchargée
with Image.open(pict) as im:
     if (imghdr.what(pict) or im.format.lower()) not in formats:
        raise TypeError("Ce format n’est pas valable")
     else:
        im_array = np.array(im)
       
# Encodage du texte

with open ('some_text.txt', 'r', encoding='utf8') as f: # adresse locale
    message = f.read()    

## or something like that:
# message = 'All work and no play makes Jack a dull boy\n' * 8000

octets = bytes(message, 'utf8')  # conversion en octets codés en UTF-8
octets_dec = np.frombuffer(octets, dtype=np.uint8) # convertit les octets en chiffres (base 10)
octets_bin = np.unpackbits(octets_dec) # base 10 -> base 2 et répartition en éléments d’un bit

# Taille du header et taille utile de l'image

header_size = 1 + ceil(len(f'{im_array.size:b}') / 4)
im_size = im_array.size - header_size # taille utile en octets

# Détermination du nombre de bits / octet à remplacer (nbits)

for nbits in range(1, 9): # groupes d’octets
    if im_size >= len(octets) * 8/nbits:
        break # sortie de boucle car on a trouvé le nbits minimal
else:
    raise ValueError("Texte trop long pour cette image") # msg trop long même avec nbits à 8

if nbits == 8: # les pixels de l'image ont été totalement remplacés
    print("*"*60, "\nAvertissement : Les tailles sont compatibles mais"
          "\nl’image sera totalement écrasée par le texte."
          "\nPour un meilleur résultat, choisissez une image plus grande.")
    print("*"*60)
    
# Affichage de nbits et du taux de bits utilisés (facultatif)

print("Nombre de bits/octet remplacés :", nbits)
print('Taux de bits utilisés : ', round(len(octets) * 100 / im_size, 2), '%')

# Répartition des bits du code texte par groupes de nbits

if octets_bin.size % nbits :  # n’est pas un multiple de nbits -> padding
    masque = np.zeros(nbits * ceil(octets_bin.size / nbits), dtype=np.uint8)
    masque[:octets_bin.size] = octets_bin
    octets_bin = masque
    
code_txt = octets_bin.reshape(-1, nbits)
code_txt = decimalisation(code_txt, 1)

# Extraction du header

header = im_array.flatten()[:header_size]

# Mise à zéro des bits de poids faible

header -= header & (2**4 - 1)  # mise à zéro des 4 bits de poids faible des octets du `header`
im_array -= im_array & (2**nbits - 1) # ràz des nbits de poids faible des autres octets du tableau

# Ecriture du header

header_code = f'{nbits:04b}' + f'{code_txt.size:0{4 * (header_size - 1)}b}'
header_code = np.array(list(header_code), dtype=np.uint8).reshape(-1, 4)
header_code = decimalisation(header_code, 1)

# Fusion des codes texte et image

im_array.ravel()[:header_size] = header + header_code
im_array.ravel()[header_size:header_size+code_txt.size] += code_txt

# Sauvegarde de l'image codée

im = Image.fromarray(im_array)
im.save(f'code_{pict}') # chemin sauvegarde image + code

