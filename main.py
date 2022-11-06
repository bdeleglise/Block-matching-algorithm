import os

import cv2
import utils
import blockmatching
import numpy as np
import sys
import time

from constants import SEQUENCE_LEN, PLOT_HEAT_MAP

np.set_printoptions(threshold=sys.maxsize)

def main():
    if len(sys.argv) != 2:
        print('Error args')
        exit(1)

    type = "I"
    previous_trame = None

    result_dir = sys.argv[1] + "_result"
    try:
        os.mkdir(result_dir)
    except OSError:
        print('Already exist')

    macroblocks_list = []
    results = []

    # encode
    print("Creates macroblocks ...")
    tot_macroblocks_bits = 0
    tot_macroblocks_bits_without_data = 0
    tot_original_len = 0
    time_encode = 0
    for i in range(0, SEQUENCE_LEN):
        #Debug
        #if i == 2:
        #    break
        result = []
        img = sys.argv[1] + '/frame%d.jpg' % i
        print("Opening : ", img)
        current_trame = cv2.imread(img, cv2.IMREAD_UNCHANGED)

        current_trame = utils.BGR2Y(current_trame)
        cv2.imwrite(result_dir + "/frame%d.jpg" % i, current_trame)  # save frame as JPEG file

        start_macroblock = time.time()
        blocks, blocks_coord = utils.get_16x16_blocks(current_trame)
        nbYNoCode = 0
        if type == "I":
            macroblocks = utils.init_macroblocks(blocks, blocks_coord, "I")
        else:
            macroblocks, nbYNoCode = blockmatching.block_mactching(current_trame, previous_trame, blocks, blocks_coord)

        len_macroblocks_bits_binaire, len_macroblocks_bits_binaire_without_date, len_original_frame = utils.get_length_macroblocks_bits(
            macroblocks, current_trame)
        end_macroblock = time.time()

        print("NBY pas codé : ", nbYNoCode)
        print('Macroblocks bits                 : ', len_macroblocks_bits_binaire)
        print('Compression                      : ', 1 - len_macroblocks_bits_binaire/len_original_frame)
        print('Macroblocks bits without data    : ', len_macroblocks_bits_binaire_without_date)
        print('Compression without data         : ', 1 - len_macroblocks_bits_binaire_without_date / len_original_frame)
        print('Original bits                    : ', len_original_frame)
        print('Time                             : ', end_macroblock - start_macroblock)

        if PLOT_HEAT_MAP == True and type == "P":
            utils.plot_heat_map(macroblocks, current_trame, img)

        tot_macroblocks_bits += len_macroblocks_bits_binaire
        tot_macroblocks_bits_without_data += len_macroblocks_bits_binaire_without_date
        tot_original_len += len_original_frame
        time_encode += (end_macroblock - start_macroblock)
        result.append(img)
        result.append(1 - len_macroblocks_bits_binaire/len_original_frame)
        result.append(1 - len_macroblocks_bits_binaire_without_date/len_original_frame)
        result.append(end_macroblock - start_macroblock)

        results.append(result)
        macroblocks_list.append(macroblocks)
        type = "P"
        previous_trame = current_trame

    print('Macroblocks tot bits             : ', tot_macroblocks_bits)
    print('Compression tot                  : ', 1 - tot_macroblocks_bits / tot_original_len)
    print('Macroblocks tot bits without data: ', tot_macroblocks_bits_without_data)
    print('Compression tot without data     : ', 1 - tot_macroblocks_bits_without_data / tot_original_len)
    print('Original bits                    : ', tot_original_len)
    print("Time encode                      : ", time_encode)

    #decode
    print("Decodes macroblocks...")
    time_decode = 0
    previous_trame = None
    for i in range(0, SEQUENCE_LEN):
        #Debug
        #if i == 2:
        #    break

        start_to_img = time.time()
        macroblocks = macroblocks_list[i]
        current_trame = blockmatching.macroblocks_to_trame(macroblocks, previous_trame)
        cv2.imwrite(result_dir + "/frame%d_decode.jpg" % i, current_trame)  # save frame as JPEG file
        end_to_img = time.time()

        print('Time                             : ', end_to_img - start_to_img)
        time_decode += (end_to_img - start_to_img)

        results[i].append(end_to_img - start_to_img)
        previous_trame = current_trame
    print("Time decode  : ",time_decode)
    utils.save_results(results)


def test():
    """
    # read image
    trame0 = cv2.imread('./sequence_video_0/frame0.jpg', cv2.IMREAD_UNCHANGED)

    trame0 = utils.BGR2Y(trame0)
    # utils.show_gray_frame(trame0)
    blocks_0, blocks_coord_0 = utils.get_16x16_blocks(trame0)

    # trame i :
    macroblocks_i = utils.init_macroblocks(blocks_0, blocks_coord_0, "I")
    len_macroblocks_bits_binaire_0, len_macroblocks_bits_binaire_without_date_0, len_original_frame_0 \
        = utils.get_length_macroblocks_bits(macroblocks_i, trame0)

    # trame p :
    trame1 = cv2.imread('./sequence_video_0/frame1.jpg', cv2.IMREAD_UNCHANGED)
    trame1 = utils.BGR2Y(trame1)
    # utils.show_gray_frame(trame1)
    blocks_1, blocks_coord_1 = utils.get_16x16_blocks(trame1)

    print("Mvmt detection ::: ")
    macroblocks_p, nbYNoCode = blockmatching.block_mactching(trame1, trame0, blocks_1, blocks_coord_1)
    len_macroblocks_bits_binaire, len_macroblocks_bits_binaire_without_date, len_original_frame = utils.get_length_macroblocks_bits(
        macroblocks_p, trame1)

    print("NBY pas codé : ", nbYNoCode)
    print('Macroblocks bits                 : ', len_macroblocks_bits_binaire)
    print('Macroblocks bits without data    : ', len_macroblocks_bits_binaire_without_date)
    print('Original bits                    : ', len_original_frame)

    # decode trame i:
    img_decode_i = blockmatching.macroblocks_to_trame(macroblocks_i)
    assert np.array_equal(img_decode_i, trame0)

    # decode trame p:
    img_decode_p = blockmatching.macroblocks_to_trame(macroblocks_p, trame0)
    utils.show_gray_frame(img_decode_p)

    utils.plot_heat_map(macroblocks_p, trame0)"""

    """
    print("Test rezise ::: ")
    test1 = np.array([[1,1,5,6], [3,1,5,6], [1,2,5,6], [6,1,5,6]], dtype='uint8')
    print(test1)
    test1 = cv2.resize(test1, dsize=(7, 7))
    print(test1)
    print(test1[::2, ::2])

    print("Test SSD ::: ")
    ref = np.array([[4,4,4], [3,3,3], [4,4,4]])
    A = np.array([[3,5,4], [3,3,2], [5,5,4]])
    B = np.array([[4,5,3], [3,2,3], [3,4,6]])

    print(((ref-A) ** 2).sum())
    print(((ref-B) ** 2).sum())

    test1 = np.array([[1, 1, 5, 6], [3, 1, 5, 6], [1, 2, 5, 6], [6, 1, 5, 6]], dtype='uint8')
    test1 = cv2.resize(test1, dsize=(7, 7))
    print(test1)
    test1 = np.lib.pad(test1, ((0, 3), (0, 3)), 'constant', constant_values=(0))
    print(test1)
    
    """



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
