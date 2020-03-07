# main imports
import os, sys
import argparse
import time
import numpy as np

# image import
from PIL import Image
import cv2

# modules and config imports
sys.path.insert(0, '') # trick to enable import of main folder module

import custom_config as cfg
from modules.utils import data as dt
from ipfml.processing import transform, segmentation, compression
from scipy.signal import medfilt2d, wiener, cwt
import pywt
import cv2

dataset_folder = cfg.dataset_path
scenes_list    = cfg.scenes_names
zones_indices  = cfg.zones_indices

'''
Display progress information as progress bar
'''
def write_progress(progress):
    barWidth = 180

    output_str = "["
    pos = barWidth * progress
    for i in range(barWidth):
        if i < pos:
           output_str = output_str + "="
        elif i == pos:
           output_str = output_str + ">"
        else:
            output_str = output_str + " "

    output_str = output_str + "] " + str(int(progress * 100.0)) + " %\r"
    print(output_str)
    sys.stdout.write("\033[F")


def get_image_reconstructed(lab_arr):
    """
    Method which returns the reconstructed image after all filters applied and reconstruction
    """

    kernel = np.ones((3,3),np.float32)/9.
    arr = cv2.filter2D(lab_arr,-1,kernel)

    kernel = np.ones((5,5),np.float32)/25.
    arr = cv2.filter2D(arr,-1,kernel)

    arr = cv2.GaussianBlur(arr, (3, 3), 0.5)

    arr = cv2.GaussianBlur(arr, (3, 3), 1)

    arr = cv2.GaussianBlur(arr, (3, 3), 1.5)

    arr = cv2.GaussianBlur(arr, (5, 5), 0.5)

    arr = cv2.GaussianBlur(arr, (5, 5), 1)

    arr = cv2.GaussianBlur(arr, (5, 5), 1.5)

    arr = medfilt2d(arr, [3, 3])

    arr = medfilt2d(arr, [5, 5])

    arr = wiener(arr, [3, 3])

    arr = wiener(arr, [5, 5])

    wave = w2d(arr, 'db1', 2)
        
    return lab_arr - wave


def w2d(arr, mode='haar', level=1):
    #convert to float   
    imArray = arr
    np.divide(imArray, 255)

    # compute coefficients 
    coeffs=pywt.wavedec2(imArray, mode, level=level)

    #Process Coefficients
    coeffs_H=list(coeffs)  
    coeffs_H[0] *= 0

    # reconstruction
    imArray_H = pywt.waverec2(coeffs_H, mode)
    imArray_H *= 255
    imArray_H = np.uint8(imArray_H)

    return imArray_H


def main():

    parser = argparse.ArgumentParser(description="Create output dataset converted using noise mask")

    parser.add_argument('--output', type=str, help='output dataset folder')

    args = parser.parse_args()

    p_output = args.output    

    if not os.path.exists(p_output):
        os.makedirs(p_output)

    zones_list = []

    # construct zones folder
    for index in zones_indices:

        index_str = str(index)

        while len(index_str) < 2:
            index_str = "0" + index_str
        
        zones_list.append(cfg.zone_folder + index_str)


    thresholds = {}
    images_path = {}
    number_of_images = 0

    # create dictionnary of threshold and get all images path
    for scene in scenes_list:

        scene_path = os.path.join(dataset_folder, scene)

        threshold_list = []

        for zone in zones_list:
            zone_path = os.path.join(scene_path, zone)

            with open(os.path.join(zone_path, cfg.seuil_expe_filename), 'r') as f:
                threshold_list.append(int(f.readline()))

        thresholds[scene] = threshold_list
        images_path[scene] = sorted([os.path.join(scene_path, img) for img in os.listdir(scene_path) if cfg.scene_image_extension in img])
        number_of_images = number_of_images + len(images_path[scene])


    # now convert image
    image_counter = 0

    # compute entropy for each zones of each scene images
    for scene in scenes_list:

        image_indices = [ dt.get_scene_image_postfix(img_path) for img_path in images_path[scene] ]

        output_scene_folder = os.path.join(p_output, scene)

        if not os.path.exists(output_scene_folder):
            os.makedirs(output_scene_folder)

        for index, img_path in enumerate(images_path[scene]):

            if index <= len(images_path[scene]) - 1:
                image_to_convert = Image.open(img_path)
                img_lab = transform.get_LAB_L(image_to_convert)

                next_img = Image.open(images_path[scene][index])
                next_img_lab = transform.get_LAB_L(next_img)

                diff_image = img_lab - next_img_lab
                input_image = Image.fromarray(np.array(diff_image, 'uint8'))

                output_image_name = scene + '_' + image_indices[index] + '.png'
                output_image_path = os.path.join(output_scene_folder, output_image_name)

                input_image.save(output_image_path)

            # write progress bar
            write_progress((image_counter + 1) / number_of_images)
            
            image_counter = image_counter + 1
        

if __name__ == "__main__":
    main()
