# main imports
import numpy as np
import pandas as pd
import sys, os, argparse

# image processing
from PIL import Image
from ipfml import utils
from ipfml.processing import transform, segmentation

import matplotlib.pyplot as plt

# modules and config imports
sys.path.insert(0, '') # trick to enable import of main folder module

import custom_config as cfg

dataset_folder = cfg.dataset_path
scenes_list    = cfg.scenes_names
zones_indices  = cfg.zones_indices


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

    parser.add_argument('--data', type=str, help='entropy file data with estimated threshold to read and compute')
    parser.add_argument('--scene', type=str, help='Scene index to use', choices=cfg.scenes_indices)

    args = parser.parse_args()

    p_data   = args.data
    p_scene  = args.scene

    scenes_list = cfg.scenes_names
    scenes_indices = cfg.scenes_indices

    scene_index = scenes_indices.index(p_scene.strip())
    scene = scenes_list[scene_index]


    estimated_thresholds = []
    human_thresholds = []

    # read line by line file to estimate threshold entropy stopping criteria
    with open(p_data, 'r') as f:
        lines = f.readlines()

        for line in lines:

            data = line.split(';')
            scene_name = data[0]

            if scene_name == scene:
                #zone_index = data[1]
                #zone_index_str = data[2]
                threshold = data[3]
                threshold_found = data[4]

                human_thresholds.append(int(threshold))
                estimated_thresholds.append(int(threshold_found))

    display_estimated_thresholds(scene, estimated_thresholds, human_thresholds)

if __name__== "__main__":
    main()
