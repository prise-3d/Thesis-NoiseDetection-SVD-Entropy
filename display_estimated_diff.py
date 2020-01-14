# main imports
import numpy as np
import pandas as pd
import sys, os, argparse

# image processing
from PIL import Image
from ipfml import utils
from ipfml.processing import transform, segmentation

# modules and config imports
sys.path.insert(0, '') # trick to enable import of main folder module

import custom_config as cfg

dataset_folder = cfg.dataset_path
scenes_list    = cfg.scenes_names
zones_indices  = cfg.zones_indices


def main():

    parser = argparse.ArgumentParser(description="Read and compute entropy data file")

    parser.add_argument('--data', type=str, help='entropy file data with estimated threshold to read and compute')
    parser.add_argument('--scene', type=str, help='scene expected to display', choices=scenes_list)

    args = parser.parse_args()

    p_data   = args.data
    p_scene  = args.scene

    # read line by line file to estimate threshold entropy stopping criteria
    with open(p_data, 'r') as f:
        lines = f.readlines()

        for line in lines:

            data = line.split(';')
            scene_name = data[0]

            if scene_name == p_scene:
                zone_index = data[1]
                zone_index_str = data[2]
                threshold = data[3]
                threshold_found = data[3]

                # TODO : print plot using these data
                print(zone_index_str, '(true, estimated)', threshold, ' <=>', threshold_found)



if __name__== "__main__":
    main()
