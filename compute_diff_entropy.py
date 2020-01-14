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

'''
Compute diff from entropy list (first element is used as reference)
'''
def get_zone_diff_entropy(entropy_list):
    
    diff_list = []
    previous_value = 0
    
    for index, value in enumerate(entropy_list):
        
        if index == 0:
            previous_value = value
        else:
            diff = previous_value - value
            diff_list.append(diff)
            previous_value = value
        
    return diff_list


def main():

    parser = argparse.ArgumentParser(description="Read and compute entropy data file")

    parser.add_argument('--data', type=str, help='entropy file data to read and compute')
    parser.add_argument('--output', type=str, help='prediction file used')

    args = parser.parse_args()

    p_data   = args.data
    p_output = args.output

    # create output path if not exists
    p_output_path = os.path.join(cfg.output_data_folder, p_output)
    if not os.path.exists(cfg.output_data_folder):
        os.makedirs(cfg.output_data_folder)

    # read line by line file to estimate threshold entropy stopping criteria
    with open(p_data, 'r') as f:
        lines = f.readlines()

        diff_entropy_found = []
        for line in lines:

            data = line.split(';')

            threshold = data[3]
            image_indices = data[4].split(',')
            entropy_list = data[5].split(',')

            # one element is removed using this function (first element of list for computing first difference)
            entropy_diff_list = get_zone_diff_entropy(entropy_list)
            image_indices_without_first = image_indices[1:]

            found_index = 0
            for index, v in enumerate(image_indices_without_first):
                if threshold > v:
                    found_index = index
                    break
            
            diff_entropy_found.append(entropy_diff_list[found_index])

        mean_entropy_diff = sum(diff_entropy_found) / len(diff_entropy_found)
        print(mean_entropy_diff)
            
        # now we can predict threshold img using `mean_entropy_diff`
        for line in lines:
            data = line.split(';')

            scene_name = data[0]
            zone_index = data[1]
            zone_index_str = data[2]
            threshold = data[3]
            image_indices = data[4].split(',')
            entropy_list = data[5].split(',')

            # one element is removed using this function (first element of list for computing first difference)
            entropy_diff_list = get_zone_diff_entropy(entropy_list)
            image_indices_without_first = image_indices[1:]

            # by default max index (if no stoppring criteria found)
            found_index = len(image_indices_without_first) - 1
            for index, v in enumerate(entropy_diff_list):
                if mean_entropy_diff > v:
                    found_index = index
                    break

            threshold_found = image_indices_without_first[found_index]

            with open(p_output_path, 'a') as f:
                f.write(scene_name + ';')
                f.write(zone_index + ';')
                f.write(zone_index_str + ';')
                f.write(threshold + ';')
                f.write(threshold_found + ';')
                f.write(mean_entropy_diff + ';')
                f.write('\n')


if __name__== "__main__":
    main()
