import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import skimage as sk
import os

import skimage.io

TEST = "Data/TEST/"
TRAIN = "Data/TRAIN/"

CSVs = []
IMGs = []
for i in os.listdir(TEST):
    if "csv" in i:
        CSVs.append(TEST + i)
    if "jpg" in i or "png" in i:
        IMGs.append(TEST + i)

CSVs = sorted(CSVs)
IMGs = sorted(IMGs)

print(CSVs, IMGs)

tables = [pd.read_csv(c, header=None) for c in CSVs]
images = [skimage.io.imread(i) for i in IMGs]

def apply(image):

    image = skimage.img_as_float(image)
    # Upscale image

    # Extract veins from wings

    # Convert into grayscale and apply plenty of other colorspace transforms to the image to better show the junctions

    # Find a Way to do watershed, openings, closing and more to remove unnecessary parts from the image (dirt, black spots, etc)

    return image

for i, image in zip(range(len(images)), images):
    images[i] = apply(image)

table = pd.DataFrame(tables[0])
for i in range(len(CSVs)):
    plt.imshow(images[i])
    plt.scatter(tables[i][1], tables[i][0], color='r', marker="+")
    plt.show()


# Links
# Google Search : extract junctions from veins in wing images python
# https://stackoverflow.com/questions/57128882/image-segmentation-how-to-detect-this-kind-of-vein-junctions-landmarks
# https://forum.image.sc/t/detecting-and-measuring-gridlines-with-skimage/37738/2 ---> Canny / Hough Approach
# https://scikit-image.org/docs/dev/auto_examples/edges/plot_line_hough_transform.html
# https://www.cs.colostate.edu/~cs510/yr2018sp/more_progress/pdfs/cs510_L17_Canny_Hough.pdf
