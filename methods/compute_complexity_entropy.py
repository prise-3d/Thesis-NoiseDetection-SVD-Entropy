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
Compute gradient from entropy and complexity lists (first element is used as reference)
'''
def get_sobel_entropy_complexity(entropy_list, sobel_list, std=False):
    
    dh_list = []
    previous_entropy_value = 0
    previous_sobel_value = 0

    entropy_list = list(map(float, entropy_list))
    sobel_list = list(map(float, sobel_list))

    if std:
        entropy_list_norm = utils.normalize_arr(entropy_list)
        sobel_list_norm = utils.normalize_arr(sobel_list)
    
    for i in range(len(entropy_list)):
        
        if i > 0:
            
            entropy_diff = abs(previous_entropy_value - entropy_list[i])
            sobel_diff = abs(previous_sobel_value - sobel_list[i])
            
            if std:
                # ponderation using `std` from each list normalized
                dh = (entropy_diff * np.std(entropy_list_norm[:(i+1)])) / (sobel_diff * np.std(sobel_list_norm[:(i+1)]))
            else:
                dh = entropy_diff / sobel_diff

            dh_list.append(dh)
        
        previous_entropy_value = entropy_list[i]
        previous_sobel_value = sobel_list[i]
        
    return dh_list


def main():

    parser = argparse.ArgumentParser(description="Read and compute complexity data file (using entropy and sobel)")

    parser.add_argument('--data1', type=str, help='entropy file data to read and compute')
    parser.add_argument('--data2', type=str, help='entropy file data to read and compute')
    parser.add_argument('--norm', type=int, help='normalize or not entropy', choices=[0, 1], default=0)
    parser.add_argument('--std', type=int, help='multiply result by current std', choices=[0, 1], default=0)
    parser.add_argument('--output', type=str, help='prediction file used')

    args = parser.parse_args()

    p_data1  = args.data1
    p_data2  = args.data2
    p_norm   = args.norm
    p_std    = args.std
    p_output = args.output

    # create output path if not exists
    p_output_path = os.path.join(cfg.output_data_folder, p_output)
    if not os.path.exists(cfg.output_data_folder):
        os.makedirs(cfg.output_data_folder)


    # read line by line file to estimate threshold entropy stopping criteria
    with open(p_data1, 'r') as f:
        lines_entropy = f.readlines()
    
    with open(p_data2, 'r') as f:
        lines_complexity = f.readlines()

    gradient_complexity_found = []
    
    for i in range(len(lines_entropy)):

        data_entropy = lines_entropy[i].split(';')
        data_complexity = lines_complexity[i].split(';')

        threshold = data_entropy[3]
        image_indices = data_entropy[4].split(',')

        entropy_list = data_entropy[5].split(',')
        complexity_list = data_complexity[5].split(',')


        # one element is removed using this function (first element of list for computing first gradient complexity)
        entropy_gradient_list = get_sobel_entropy_complexity(entropy_list, complexity_list, p_std)
        image_indices_without_first = image_indices[1:]

        found_index = 0
        for index, v in enumerate(image_indices_without_first):
            
            if int(v) > int(threshold):
                found_index = index
                break
        
        if p_norm:
            gradient_complexity_kept = utils.normalize_arr(entropy_gradient_list[:found_index+1])[-1]
        else:
            gradient_complexity_kept = entropy_gradient_list[found_index]
        
        # Keep only absolute value
        gradient_complexity_found.append(gradient_complexity_kept)

    mean_complexity_gradient = sum(gradient_complexity_found) / len(gradient_complexity_found)
    std_complexity_gradient = np.std(gradient_complexity_found)
    
    print('mean', mean_complexity_gradient)
    print('std', std_complexity_gradient)
            
    with open(p_output_path, 'w') as f:
        print("Erase", p_output_path, "previous file if exists")

    # now we can predict threshold img using `mean_complexity_gradient`
    for i in range(len(lines_entropy)):

        data_entropy = lines_entropy[i].split(';')
        data_complexity = lines_complexity[i].split(';')

        scene_name = data_entropy[0]
        zone_index = data_entropy[1]
        zone_index_str = data_entropy[2]
        threshold = data_entropy[3]
        image_indices = data_entropy[4].split(',')

        entropy_list = data_entropy[5].split(',')
        complexity_list = data_complexity[5].split(',')

        # one element is removed using this function (first element of list for computing first gradient complexity)
        entropy_gradient_list = get_sobel_entropy_complexity(entropy_list, complexity_list, p_std)
        image_indices_without_first = image_indices[1:]

        # by default max index (if no stoppring criteria found)
        found_index = len(image_indices_without_first) - 1
        for index, v in enumerate(entropy_gradient_list):

            if p_norm:
                current_v = utils.normalize_arr(entropy_gradient_list[:index+1])[-1]
            else:
                current_v = v

            if mean_complexity_gradient > current_v:
                found_index = index
                break

        threshold_found = image_indices_without_first[found_index]

        with open(p_output_path, 'a') as f:
            f.write(scene_name + ';')
            f.write(zone_index + ';')
            f.write(zone_index_str + ';')
            f.write(threshold + ';')
            f.write(threshold_found + ';')
            f.write(str(mean_complexity_gradient) + ';')
            f.write(str(std_complexity_gradient) + ';')
            f.write(str(p_norm))
            f.write('\n')


if __name__== "__main__":
    main()
