# coding: utf8

"""
    Steganography module allowing to insert text encoded in UTF-8
    in raster images by replacing bits. The number of bits / byte 
    replaced is determined dynamically.
"""

from math import ceil
from PIL import Image
import numpy as np

# Ouverture de l'image et enregistrement des pixels

im_array = np.array(Image.open('code_some_image.png'))

# Lecture du header

head_binsize = len(f'{im_array.size:b}')
head_size = ceil(head_binsize / 4) + 1 # taille en octets

header = im_array.ravel()[:head_size]
header = header & (2**4 - 1) # formule équivalente à `header % 2**4`

# Enregistement des informations

nbits = header[0] # nombre de bits/octets utilisés
bin_code_size = ''.join(f'{c:04b}' for c in header[1:]) # valeur en binaire de la longueur du message
code_size = int(bin_code_size, 2) # valeur en base décimale

# Récupération du code texte en valeurs binaires

im_array = im_array & (2**nbits - 1)
im_array = im_array.reshape(-1, 1)[head_size:head_size + code_size]
code_txt = np.unpackbits(im_array, axis=1)

# Concaténation des bits par groupes de nbits

code_txt = np.packbits(code_txt[:, 8-nbits:])
code_txt = np.trim_zeros(code_txt, 'b') # on retire d’éventuels octets nuls

# Décodage des octets et conversion en caractères
try:
    message = bytes(code_txt).decode('utf8')
    
except UnicodeDecodeError:
    print("Cette image ne contient pas de code ou le code est illisible.")
    
else:
    print('Début du texte :', message[:273])
    print(f'Longueur du texte : {len(message)} caractères')
    
# Sauvegarde du texte (facultatif)
with open('new_texte.txt', 'w') as f:
  f.write(message)
