import argparse
from PIL import Image
from os import listdir
# from time import sleep

DEFAULT_CUTSIZE = 400

def handleImg(path, filename, outdir, cutsize):
    img = Image.open(path+filename)
    img_w, img_h = img.size

    target_size = cutsize if cutsize else DEFAULT_CUTSIZE
    steps_x = img_w // target_size
    steps_y = img_h // target_size

    for x in range(steps_x):
        for y in range(steps_y):
            area = (x*target_size, y*target_size, (x+1)*target_size, (y+1)*target_size)
            cropped_img = img.crop(area)
            # cropped_img.show()
            cropped_img.save(outdir + "/" + filename.split(".")[0] + "_" + str(x) + "_" + str(y) + ".png")


def isValidInput(filename):
    validtypes = [".jpg",".jpeg",".png"]
    for t in validtypes:
        if t in filename:
            return True
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="path to input directory")
    parser.add_argument("output", help="path to output directory")
    parser.add_argument("--cutsize", help="dimensions in px of the resulting output images")
    args = parser.parse_args()

    onlyfiles = [f for f in listdir(args.input) if isValidInput(f)]

    # Image.MAX_IMAGE_PIXELS = 365310800   

    for file in onlyfiles:
        handleImg(args.input,file, args.output, args.cutsize)

    # sleep(1000)

