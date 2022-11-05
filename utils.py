import numpy as np
import cv2
import matplotlib.pyplot as plt
from constants import MACROBLOCK_SIZE, BLOCK_Y_SIZE, RAYON, INCREMENT


def BGR2Y(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return gray

def show_gray_frame(frame):
    plt.imshow(frame, cmap='gray')
    plt.show()

def get_16x16_blocks(frame):
    # height, width, number of channels in image
    height = frame.shape[0]
    width = frame.shape[1]

    # print('Image Height       : ', height)
    # print('Image Width        : ', width)

    blocks = []
    blocks_coord = [] #coord of the first pixel in the block

    for i in range(0, height, MACROBLOCK_SIZE):
        for j in range(0, width, MACROBLOCK_SIZE):
            blocks.append(frame[i:i+MACROBLOCK_SIZE, j:j+MACROBLOCK_SIZE])
            blocks_coord.append([i, j])

    # print('Block 0        : ', blocks[0])
    # print('NB Blocks      : ', len(blocks))

    return blocks, blocks_coord


def init_macroblocks(blocks, blocks_coord, type):
    macroblocks = []

    for i in range(0, len(blocks)):
        block = blocks[i]
        coord = blocks_coord[i]
        macroblock = {
            "ADDR": coord,
            "TYPE": type,
            "VECT": None,
            "CBP": 15,
            "B0": block[0:0+BLOCK_Y_SIZE, 0:0+BLOCK_Y_SIZE],
            "B1": block[0:0+BLOCK_Y_SIZE, BLOCK_Y_SIZE:2*BLOCK_Y_SIZE],
            "B2": block[BLOCK_Y_SIZE:2*BLOCK_Y_SIZE, 0:0+BLOCK_Y_SIZE],
            "B3": block[BLOCK_Y_SIZE:2*BLOCK_Y_SIZE, BLOCK_Y_SIZE:2*BLOCK_Y_SIZE],
        }
        macroblocks.append(macroblock)

    # print('Macroblock 0    :', macroblocks[0])

    return macroblocks


def get_length_macroblocks_bits(macroblocks, frame):
    height = frame.shape[0]
    width = frame.shape[1]

    len_macroblocks_bits = 0
    len_macroblocks_bits_without_h_w_r_i = 0
    len_original = height*width*8

    # TYPE 1 pour P ou 0 pour I
    len_type = 1
    # ADDR on a max(frame.shape[0], frame.shape[1]) symboles différents
    len_addr = 2 * np.ceil(np.log2(max(height, width)))
    # VECT pour I -> null, pour P on a max Rayon*INCREMENT symboles différents par axe plus le signe sur
    # un bit pour chaque axe
    len_vect = 2 * (np.ceil(np.log2(INCREMENT*RAYON)) + 1)
    # CBP 4 bits
    len_cbp = 4
    # B 9 bits pour le symbole minimal qui peut être négatif + nbsymbolesMax (= max - min + 1) symboles différents
    for i in range(0, len(macroblocks)):
        macroblock = macroblocks[i]
        len_block = len_type + len_addr + len_cbp
        if macroblock["TYPE"] == "P":
            len_block += len_vect

        cbp = macroblock["CBP"]
        if cbp & 0b1:
            b0 = macroblock["B0"]
            len_block += 9 + (np.ceil(np.log2(np.amax(b0) - np.amin(b0) + 1)) * BLOCK_Y_SIZE * BLOCK_Y_SIZE)

        cbp = cbp >> 1
        if cbp & 0b1:
            b1 = macroblock["B1"]
            len_block += 9 + (np.ceil(np.log2(np.amax(b1) - np.amin(b1) + 1)) * BLOCK_Y_SIZE * BLOCK_Y_SIZE)

        cbp = cbp >> 1
        if cbp & 0b1:
            b2 = macroblock["B2"]
            len_block += 9 + (np.ceil(np.log2(np.amax(b2) - np.amin(b2) + 1)) * BLOCK_Y_SIZE * BLOCK_Y_SIZE)

        cbp = cbp >> 1
        if cbp & 0b1:
            b3 = macroblock["B3"]
            len_block += 9 + (np.ceil(np.log2(np.amax(b3) - np.amin(b3) + 1)) * BLOCK_Y_SIZE * BLOCK_Y_SIZE)

        len_macroblocks_bits += len_block

    # hauteur largeur rayon increment et taille des macroblock
    len_macroblocks_bits_without_h_w_r_i = len_macroblocks_bits + (len(macroblocks) * (8+32*3+1))

    return len_macroblocks_bits, len_macroblocks_bits_without_h_w_r_i, len_original