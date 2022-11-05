from constants import RAYON, INCREMENT, MACROBLOCK_SIZE, MACROBLOCK_THRESHOLD, BLOCK_Y_SIZE, BLOCK_Y_THRESHOLD
import cv2 as cv
import numpy as np
import utils

def block_mactching(current_trame, previous_trame, blocks, blocks_coord):
    height = current_trame.shape[0]
    width = current_trame.shape[1]
    block_len = MACROBLOCK_SIZE
    macroblocks = []
    nbYNoCode = 0

    # fois 2 pour un pas de 1/2 pixels
    if INCREMENT == 2:
        previous_trame = cv.resize(previous_trame, dsize=(width * INCREMENT - 1, height * INCREMENT - 1))
        block_len += MACROBLOCK_SIZE - 1

    if INCREMENT > 2:
        raise ValueError('pixel accuracy should be 1 or 2. Got %s instead.' % INCREMENT)

    # print(previous_trame.shape)
    # utils.show_gray_frame(previous_trame)
    # previous_trame_rezise = previous_trame
    # previous_trame = np.lib.pad(previous_trame, ((0, MACROBLOCK_SIZE * INCREMENT - 1), (0, MACROBLOCK_SIZE * INCREMENT - 1)), 'constant', constant_values=(0))

    # if INCREMENT == 1:
    #    assert np.array_equal(previous_trame_rezise, previous_trame[0:height * INCREMENT, 0:width * INCREMENT])
    # else:
    #    assert np.array_equal(previous_trame_rezise, previous_trame[0:height * INCREMENT - 1, 0:width * INCREMENT - 1])

    # print(previous_trame.shape)
    # utils.show_gray_frame(previous_trame[0:height * INCREMENT - 1, 0:width * INCREMENT - 1])

    for pos in range(0, len(blocks)):
        current_block = blocks[pos]
        current_block_coord = blocks_coord[pos]

        # minimum norm of the SSD norm found so far
        sum_square_diff_min = np.infty
        matching_block = np.empty((MACROBLOCK_SIZE, MACROBLOCK_SIZE), dtype=np.uint8)
        vect_x = 0
        vect_y = 0

        # print(sum_square_diff_min)
        # print(current_block_coord)
        min_h = (current_block_coord[0] - RAYON) * INCREMENT
        if min_h < 0:
            min_h = 0
        max_h = (current_block_coord[0] + RAYON) * INCREMENT
        if max_h + block_len > (height * INCREMENT):
            max_h = height * INCREMENT - block_len  ## c'es louche
            if max_h < current_block_coord[0]:
                max_h = current_block_coord[0] * INCREMENT + 1
        min_w = (current_block_coord[1] - RAYON) * INCREMENT
        if min_w < 0:
            min_w = 0
        max_w = (current_block_coord[1] + RAYON) * INCREMENT
        if max_w + block_len > (width * INCREMENT):
            max_w = width * INCREMENT - block_len
            if max_w < current_block_coord[1]:
                max_w = current_block_coord[1] * INCREMENT + 1

        # print(min_h, max_h, min_w, max_w)

        for i in range(min_h, max_h):
            for j in range(min_w, max_w):
                previous_block = previous_trame[i:i+block_len, j:j+block_len]
                # print(previous_block[::INCREMENT, ::INCREMENT].shape)
                previous_block = previous_block[::INCREMENT, ::INCREMENT]

                assert previous_block.shape == (MACROBLOCK_SIZE, MACROBLOCK_SIZE)

                # print(((current_block-previous_block)**2).sum())

                sum_square_diff = ((current_block-previous_block)**2).sum()

                if sum_square_diff < sum_square_diff_min:
                    sum_square_diff_min = sum_square_diff
                    matching_block = previous_block
                    vect_x = current_block_coord[0] * INCREMENT - i
                    vect_y = current_block_coord[1] * INCREMENT - j

                    if sum_square_diff_min <= MACROBLOCK_THRESHOLD:
                        break

        #set macroblocks
        cbp = 0b0

        b0 = current_block[0:0+BLOCK_Y_SIZE, 0:0+BLOCK_Y_SIZE] - matching_block[0:0+BLOCK_Y_SIZE, 0:0+BLOCK_Y_SIZE]
        if (b0 ** 2).sum() <= BLOCK_Y_THRESHOLD:
            b0 = None
            nbYNoCode += 1
        else:
            cbp = 0b1

        b1 = current_block[0:0+BLOCK_Y_SIZE, BLOCK_Y_SIZE:2*BLOCK_Y_SIZE] - matching_block[0:0+BLOCK_Y_SIZE, BLOCK_Y_SIZE:2*BLOCK_Y_SIZE]
        if (b1 ** 2).sum() <= BLOCK_Y_THRESHOLD:
            b1 = None
            nbYNoCode += 1
        else:
            cbp = cbp | 0b10

        b2 = current_block[BLOCK_Y_SIZE:2*BLOCK_Y_SIZE, 0:0+BLOCK_Y_SIZE] - matching_block[BLOCK_Y_SIZE:2*BLOCK_Y_SIZE, 0:0+BLOCK_Y_SIZE]
        if (b2 ** 2).sum() <= BLOCK_Y_THRESHOLD:
            b2 = None
            nbYNoCode += 1
        else:
            cbp = cbp | 0b100

        b3 = current_block[BLOCK_Y_SIZE:2*BLOCK_Y_SIZE, BLOCK_Y_SIZE:2*BLOCK_Y_SIZE] - matching_block[BLOCK_Y_SIZE:2*BLOCK_Y_SIZE, BLOCK_Y_SIZE:2*BLOCK_Y_SIZE]
        if (b3 ** 2).sum() <= BLOCK_Y_THRESHOLD:
            b3 = None
            nbYNoCode += 1
        else:
            cbp = cbp | 0b1000

        macroblock = {
            "ADDR": current_block_coord,
            "TYPE": "P",
            "VECT": (vect_x, vect_y),
            "CBP": cbp,
            "B0": b0,
            "B1": b1,
            "B2": b2,
            "B3": b3,
        }


        # print('Macroblock update ', pos)
        # print(macroblock)
        macroblocks.append(macroblock)

    # print(len(macroblocks))
    return macroblocks, nbYNoCode


def macroblocks_to_trame_i(macroblocks, trame_height, trame_width):
    trame = np.zeros((trame_height, trame_width), dtype=np.uint8)

    for i in range(0, len(macroblocks)):
        macroblock = macroblocks[i]
        x = macroblock["ADDR"][0]
        y = macroblock["ADDR"][1]

        trame[x:x+BLOCK_Y_SIZE, y:y+BLOCK_Y_SIZE] = macroblock["B0"]
        trame[x:x+BLOCK_Y_SIZE, y+BLOCK_Y_SIZE:y+2*BLOCK_Y_SIZE] = macroblock["B1"]
        trame[x+BLOCK_Y_SIZE:x+2*BLOCK_Y_SIZE, y:y+BLOCK_Y_SIZE] = macroblock["B2"]
        trame[x+BLOCK_Y_SIZE:x+2*BLOCK_Y_SIZE, y+BLOCK_Y_SIZE:y+2*BLOCK_Y_SIZE] = macroblock["B3"]

    #utils.show_gray_frame(trame)
    return trame


def macroblocks_to_trame_p(macroblocks, trame_height, trame_width, previous_trame):
    trame = np.zeros((trame_height, trame_width), dtype=np.uint8)

    block_len = MACROBLOCK_SIZE

    # fois 2 pour un pas de 1/2 pixels
    if INCREMENT == 2:
        previous_trame = cv.resize(previous_trame, dsize=(trame_width * INCREMENT - 1, trame_height * INCREMENT - 1))
        block_len += MACROBLOCK_SIZE - 1

    if INCREMENT > 2:
        raise ValueError('pixel accuracy should be 1 or 2. Got %s instead.' % INCREMENT)

    # print(previous_trame.shape)
    #previous_trame_rezise = previous_trame
    #previous_trame = np.lib.pad(previous_trame,
    #                            ((0, MACROBLOCK_SIZE * INCREMENT - 1), (0, MACROBLOCK_SIZE * INCREMENT - 1)),
    #                            'constant', constant_values=(0))
    #if INCREMENT == 1:
    #    assert np.array_equal(previous_trame_rezise, previous_trame[0:trame_height * INCREMENT, 0:trame_width * INCREMENT])
    #else:
    #    assert np.array_equal(previous_trame_rezise, previous_trame[0:trame_height * INCREMENT - 1, 0:trame_width * INCREMENT - 1])

    for i in range(0, len(macroblocks)):
        macroblock = macroblocks[i]
        x = macroblock["ADDR"][0]
        y = macroblock["ADDR"][1]
        prev_x = x * INCREMENT - macroblock["VECT"][0]
        prev_y = y * INCREMENT - macroblock["VECT"][1]

        previous_block = previous_trame[prev_x:prev_x + block_len, prev_y:prev_y + block_len]
        previous_block = previous_block[::INCREMENT, ::INCREMENT]

        assert previous_block.shape == (MACROBLOCK_SIZE, MACROBLOCK_SIZE)

        cbp = macroblock["CBP"]
        b0 = np.array(previous_block[0:0+BLOCK_Y_SIZE, 0:0+BLOCK_Y_SIZE], copy=True)
        if cbp & 0b1:
            b0 += macroblock["B0"]

        cbp = cbp >> 1
        b1 = np.array(previous_block[0:0+BLOCK_Y_SIZE, BLOCK_Y_SIZE:2*BLOCK_Y_SIZE], copy=True)
        if cbp & 0b1:
            b1 += macroblock["B1"]

        cbp = cbp >> 1
        b2 = np.array(previous_block[BLOCK_Y_SIZE:2*BLOCK_Y_SIZE, 0:0+BLOCK_Y_SIZE], copy=True)
        if cbp & 0b1:
            b2 += macroblock["B2"]

        cbp = cbp >> 1
        b3 = np.array(previous_block[BLOCK_Y_SIZE:2*BLOCK_Y_SIZE, BLOCK_Y_SIZE:2*BLOCK_Y_SIZE], copy=True)
        if cbp & 0b1:
            b3 += macroblock["B3"]

        trame[x:x + BLOCK_Y_SIZE, y:y + BLOCK_Y_SIZE] = b0
        trame[x:x + BLOCK_Y_SIZE, y + BLOCK_Y_SIZE:y + 2 * BLOCK_Y_SIZE] = b1
        trame[x + BLOCK_Y_SIZE:x + 2 * BLOCK_Y_SIZE, y:y + BLOCK_Y_SIZE] = b2
        trame[x + BLOCK_Y_SIZE:x + 2 * BLOCK_Y_SIZE, y + BLOCK_Y_SIZE:y + 2 * BLOCK_Y_SIZE] = b3

    return trame


def macroblocks_to_trame(macroblocks, previous_trame = None):
    last_block = macroblocks[len(macroblocks) - 1]
    trame_height = last_block["ADDR"][0] + MACROBLOCK_SIZE
    trame_width = last_block["ADDR"][1] + MACROBLOCK_SIZE
    type_trame = last_block["TYPE"]

    if type_trame == "I":
        return macroblocks_to_trame_i(macroblocks, trame_height, trame_width)
    else:
        return macroblocks_to_trame_p(macroblocks, trame_height, trame_width, previous_trame)
