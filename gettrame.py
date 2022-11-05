import sys
import cv2

def main():
    if len(sys.argv) != 4:
        print('Error args')
        exit(1)

    try:
        #Inspired from https://stackoverflow.com/questions/33311153/python-extracting-and-saving-video-frames
        vidcap = cv2.VideoCapture(sys.argv[1])

        length = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(length)

        if int(sys.argv[2]) + 15 > length:
            print('Error len')
            exit(1)

        count = 0
        print(int(sys.argv[2]))
        while count != int(sys.argv[2]):
            success, image = vidcap.read()
            if success == False:
                print('Error')
                exit(1)
            count += 1
        print(count)
        count = 0
        for i in range(0, 15):
            success, image = vidcap.read()
            print('Read a new frame: ', success)

            if success == False:
                print('Error')
                exit(1)

            cv2.imwrite(sys.argv[3] + "frame%d.jpg" % count, image)  # save frame as JPEG file
            count += 1

    except OSError:
        print('Error: Opening directory of the video')


if __name__ == '__main__':
    main()