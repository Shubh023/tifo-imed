# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import os
import cv2
import sys
import skimage.io
import numpy as np
import pandas as pd
import skimage as sk
import matplotlib.pyplot as plt
from skimage.color import rgb2gray
from skimage.filters import meijering, sato, frangi, hessian, gaussian, median
from skimage.morphology import disk, white_tophat, area_closing, skeletonize, thin, erosion, diamond, cube, ball



# Please Enter the path to the folder in INPUT
INPUT = "DATA/TEST/"

# Output folder which is RESULTS by default
OUTPUT = "RESULTS"


INPUT = INPUT.rstrip("/")
OUTPUT = OUTPUT.rstrip("/")

if not OUTPUT in os.listdir("."):
    os.mkdir(OUTPUT)
    
images_names = []
for i in os.listdir(INPUT):
    ext = os.path.splitext(i)[1]
    if ext.lower() != ".csv":
        images_names.append(i)

images_names = sorted(images_names)

images = [plt.imread(INPUT + "/" + i) for i in images_names]

def get_intersections(image):
    img = image.copy()
    
    # Reduce image Size at 15% of original
    scale_percent = 15
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    interpolation = cv2.INTER_CUBIC
    reduced = cv2.resize(img, dim, interpolation = interpolation)
    
    # Vessel Detection Filters
    kwargs = {'sigmas': [1, 1.5], 'mode': 'reflect'}
    img = rgb2gray(reduced) # Converting image to grayscale
    # img_blurred = gaussian(img, sigma=2)
    # img_denoised = median(img, selem=np.ones((5,5)))
    
    # Vessel Detection Filters
    meij = meijering(img, **kwargs)
    saato = sato(img, **kwargs)
    frang = frangi(img, **kwargs)
    hess = hessian(img, **kwargs)        

    # Post Process on Vessel detection output
    frang_tophat = white_tophat(frang, disk(10))
    thresh = np.mean(frang_tophat) / 0.99
    frang_tophat[frang_tophat > thresh] = 1
    frang_tophat[frang_tophat <= thresh] = 0

    # Cleaning up noise and unwanted parts of the wing
    img_res = frang_tophat.copy()
    img_bw = img_res > 0
    labels = sk.measure.label(img_bw, return_num=False)

    maxCC_withbcg = labels == np.argmax(np.bincount(labels.flat))
    maxCC_nobcg = labels == np.argmax(np.bincount(labels.flat, weights=img_bw.flat))

    # More processing to remove irregularities
    eroded = maxCC_nobcg
    eroded = sk.morphology.dilation(eroded, disk(1.25))
    eroded = sk.morphology.erosion(eroded, disk(1))
    
    # Applying Thin and closing to remove unwanted holes in the wings
    thinned = thin(eroded)
    thinned = sk.morphology.closing(thinned, disk(1.5))
    skel = thin(thinned)
    
    # Resizing back to the original image dimension
    rescaled_img = np.float32(skel)
    width = int(image.shape[1])
    height = int(image.shape[0])
    dim = (width, height)
        
    # resize image
    resized = cv2.resize(rescaled_img, dim, interpolation = interpolation)
    rescaled = thin(resized)
    
    binarized = np.where(rescaled > 0.1, 1, 0)
    processed = sk.morphology.remove_small_objects(binarized.astype(bool), min_size=200, connectivity=2).astype(int)

    # black out pixels
    mask_x, mask_y = np.where(processed == 0)
    rescaled[mask_x, mask_y] = 0

    gray = rescaled.copy()
    gray = np.float32(gray)

    dst = cv2.cornerHarris(gray, 25, 3, 0.075)

    # result is dilated for marking the corners
    dst = cv2.dilate(dst, None)

    # Threshold for an optimal value, it may vary depending on the image.
    img_thresh = cv2.threshold(dst, 0.185*dst.max(), 255, 0)[1]
    img_thresh = np.uint8(img_thresh)

    # get the matrix with the x and y locations of each centroid
    centroids = cv2.connectedComponentsWithStats(img_thresh)[3]
    
    stop_criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 255, 0.01)
    # refine corner coordinates to subpixel accuracy
    corners = cv2.cornerSubPix(gray, np.float32(centroids), (5,5), (-1,-1), stop_criteria)
    corners = np.round(corners)
    intersections = np.unique(corners, axis=0)
    intersections[:,[0,1]] = intersections[:,[1,0]]

    return intersections

"""

def generate_all_intersection(images, names):
    for i in range(len(names)):
        intersection = get_intersections(images[i])
        file_name = OUTPUT + "/" + os.path.splitext(names[i])[0] + ".csv"
        pd.DataFrame(intersection).to_csv(file_name, header=None, index=False)
        
        plt.imshow(images[i], cmap='gray')
        table = pd.read_csv(file_name, header=Noney
        plt.scatter(table[1], table[0], color='b', marker="o")
        plt.show()

"""

def generate_all_intersection(images, names):
    for i in range(len(images)):
        # Outputing information on the progress of the generation process
        progress = i/len(images)
        block = int(round(20*progress))
        text = "\rProgress: [{0}] {1}%".format( ">"*block + "-"*(20-block), round(100*progress))
        sys.stdout.write(text)
        sys.stdout.flush()
        
        
        # Calculating the intersections and saving them as in a csv file
        intersection = get_intersections(images[i])
        file_name = OUTPUT + "/" + os.path.splitext(names[i])[0] + ".csv"
        pd.DataFrame(intersection).to_csv(file_name, header=None, index=False)
        
        
    
        # For Debugging purposes - Load the generated csv and output a scatter plot among with the input image
        csv = pd.read_csv(file_name, header=None).to_numpy()
        plt.imshow(images[i])
        plt.scatter([x[1] for x in csv], [y[0] for y in csv], color='b', marker="o")
        plt.show()
        
    
    text = "\rProgress: [{0}] DONE.".format(">"*20)
    sys.stdout.write(text)
    sys.stdout.flush()
                
    print("\nGenerated csv files can be found in folder : " + OUTPUT)
    return None

generate_all_intersection(images, images_names)
