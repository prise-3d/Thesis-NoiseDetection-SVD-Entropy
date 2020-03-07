# main imports
import numpy as np
import pandas as pd
import sys, os, argparse

# image processing
import cv2
from PIL import Image
from ipfml import utils
from ipfml.processing import transform, segmentation
from scipy.signal import medfilt2d, wiener, cwt
import pywt
import cv2

import matplotlib.pyplot as plt

# ml imports
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, f1_score
#from sklearn.externals import joblib
import joblib

# modules and config imports
sys.path.insert(0, '') # trick to enable import of main folder module

from modules.utils import data as dt
import custom_config as cfg

dataset_folder = cfg.dataset_path
scenes_list    = cfg.scenes_names
zones_indices  = cfg.zones_indices


def get_image_features(img_lab):
    """
    Method which returns the data type expected
    """

    img_width, img_height = 200, 200
    arr = img_lab

    # compute all filters statistics
    def get_stats(arr, I_filter):

        # e1       = np.abs(arr - I_filter)
        # L        = np.array(e1)
        # mu0      = np.mean(L)
        # A        = L - mu0
        # H        = A * A
        # E        = np.sum(H) / (img_width * img_height)
        # P        = np.sqrt(E)

        # return mu0, P

        return np.mean(I_filter), np.std(I_filter)

    stats = []

    kernel = np.ones((3,3),np.float32)/9
    stats.append(get_stats(arr, cv2.filter2D(arr,-1,kernel)))

    kernel = np.ones((5,5),np.float32)/25
    stats.append(get_stats(arr, cv2.filter2D(arr,-1,kernel)))

    stats.append(get_stats(arr, cv2.GaussianBlur(arr, (3, 3), 0.5)))

    stats.append(get_stats(arr, cv2.GaussianBlur(arr, (3, 3), 1)))

    stats.append(get_stats(arr, cv2.GaussianBlur(arr, (3, 3), 1.5)))

    stats.append(get_stats(arr, cv2.GaussianBlur(arr, (5, 5), 0.5)))

    stats.append(get_stats(arr, cv2.GaussianBlur(arr, (5, 5), 1)))

    stats.append(get_stats(arr, cv2.GaussianBlur(arr, (5, 5), 1.5)))

    stats.append(get_stats(arr, medfilt2d(arr, [3, 3])))

    stats.append(get_stats(arr, medfilt2d(arr, [5, 5])))

    stats.append(get_stats(arr, wiener(arr, [3, 3])))

    stats.append(get_stats(arr, wiener(arr, [5, 5])))

    wave = w2d(arr, 'db1', 2)
    stats.append(get_stats(arr, np.array(wave, 'float64')))

    data = []

    for stat in stats:
        data.append(stat[0])

    for stat in stats:
        data.append(stat[1])
    
    # data normalization
    data = np.array(utils.normalize_arr(data))

    return data


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



def display_estimated_thresholds(scene, estimated, humans):
    
    colors = ['C0', 'C1', 'C2', 'C3']
    
    plt.figure(figsize=(25, 20))
    plt.rc('xtick', labelsize=16)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=16)    # fontsize of the tick labels
    
    plt.plot(estimated, 
             color=colors[0], 
             label='Estimated thresholds')

    
    plt.plot(humans, 
             color=colors[1], 
             label='Human thresholds')
        
    plt.xticks(zones_indices)
    plt.title('Comparisons of estimated vs human thresholds for ' + scene, fontsize=22)
    plt.legend(fontsize=20)
    plt.show()


def main():

    parser = argparse.ArgumentParser(description="Read and compute entropy data file")

    parser.add_argument('--model', type=str, help='joblib sklearn model file to use')
    parser.add_argument('--scene', type=str, help='Scene index to use', choices=cfg.scenes_indices)

    args = parser.parse_args()

    p_model  = args.model
    p_scene  = args.scene

    model = joblib.load(p_model)

    scenes_list = cfg.scenes_names
    scenes_indices = cfg.scenes_indices

    scene_index = scenes_indices.index(p_scene.strip())
    scene = scenes_list[scene_index]

    # get scene path
    scene_path = os.path.join(dataset_folder, scene)

    human_thresholds = []

    # get human thrsholds
    zones_list = []

    # construct zones folder
    for index in zones_indices:

        index_str = str(index)

        while len(index_str) < 2:
            index_str = "0" + index_str
        
        zones_list.append(cfg.zone_folder + index_str)

    # read line by line file to estimate threshold entropy stopping criteria
    for zone in zones_list:
        zone_path = os.path.join(scene_path, zone)

        with open(os.path.join(zone_path, cfg.seuil_expe_filename), 'r') as f:
            human_thresholds.append(int(f.readline()))


    # get estimated thresholds
    estimated_thresholds = []

    # by default estimated threshold is None
    for index in zones_indices:
        estimated_thresholds.append(None)

    scenes_images = sorted([ img for img in os.listdir(scene_path) if cfg.scene_image_extension in img ])
    number_of_images = len(scenes_images)
    image_counter = 0

    print(scenes_images)

    # compute simulation over scene 
    for img_path in scenes_images:

        scene_img_path = os.path.join(scene_path, img_path)

        blocks = segmentation.divide_in_blocks(Image.open(scene_img_path), (200, 200))

        current_img_index = dt.get_scene_image_quality(img_path)

        for index, block in enumerate(blocks):
            
            if estimated_thresholds[index] is None:

                # convert image into L
                img_lab = transform.get_LAB_L(block)
                input_data = get_image_features(img_lab)

                y = model.predict(input_data.reshape(1, -1))[0]
                
                if y != 1:
                    estimated_thresholds[index] = current_img_index

        write_progress((image_counter + 1) / number_of_images)
        image_counter += 1

    print(estimated_thresholds)

    for index, zone in enumerate(zones_list):

        if estimated_thresholds[index] is None:
            # by default associate last image 
            estimated_thresholds[index] = dt.get_scene_image_quality(scenes_images[-1])
        
    display_estimated_thresholds(scene, estimated_thresholds, human_thresholds)

if __name__== "__main__":
    main()
