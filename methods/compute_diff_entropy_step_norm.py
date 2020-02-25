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

k_factor = 1.4

'''
Compute diff from entropy list (first element is used as reference)
'''
def get_zone_diff_entropy(entropy_list, step, std=False):
    
    diff_list = []
    previous_value = 0

    entropy_list = list(map(float, entropy_list))

    if std:
        entropy_list_norm = utils.normalize_arr(entropy_list)
    
    for index, value in enumerate(entropy_list):
        
        if index > 0:

            if std:
                # ponderation using `std` from list normalized
                diff = previous_value - np.std(entropy_list[:(index+1)])
            else:
                diff = previous_value - (value * float(step))

            diff_list.append(diff)

        if std:
            previous_value = np.std(entropy_list_norm[:(index+1)])
        else:
            previous_value = value * float(step)
        
    return diff_list


def main():

    parser = argparse.ArgumentParser(description="Read and compute entropy data file (using diff)")

    parser.add_argument('--data', type=str, help='entropy file data to read and compute')
    parser.add_argument('--norm', type=int, help='normalize or not entropy', choices=[0, 1], default=0)
    parser.add_argument('--std', type=int, help='multiply result by current std', choices=[0, 1], default=0)
    parser.add_argument('--output', type=str, help='prediction file used')
    parser.add_argument('--train_scenes', type=str, help='list of train scenes used', default='')

    args = parser.parse_args()

    p_data         = args.data
    p_norm         = args.norm
    p_std          = args.std
    p_output       = args.output
    p_train_scenes = args.train_scenes.split(',')

     # list all possibles choices of renderer
    scenes_list = cfg.scenes_names
    scenes_indices = cfg.scenes_indices

    # getting scenes from indexes user selection
    scenes_selected = []

    # if training set is empty then use all scenes
    if p_train_scenes[0] == '':
        scenes_selected = scenes_list
    else:
        for scene_id in p_train_scenes:
            index = scenes_indices.index(scene_id.strip())
            scenes_selected.append(scenes_list[index])

    print("Scenes used in train:", scenes_selected)

    # create output path if not exists
    threshold_path = os.path.join(cfg.output_data_folder, cfg.data_thresholds)
    p_output_path = os.path.join(threshold_path, p_output)
    if not os.path.exists(threshold_path):
        os.makedirs(threshold_path)

    # read line by line file to estimate threshold entropy stopping criteria
    with open(p_data, 'r') as f:
        lines = f.readlines()

        diff_entropy_found = []
        for line in lines:

            data = line.split(';')

            scene_name = data[0]

            # only if scene is used for training part
            if scene_name in scenes_selected:
                    
                threshold = data[3]
                image_indices = data[4].split(',')
                entropy_list = data[5].split(',')
                step_size = int(image_indices[1]) - int(image_indices[0])
                print(step_size)

                # one element is removed using this function (first element of list for computing first difference)
                entropy_diff_list = get_zone_diff_entropy(entropy_list, step_size, p_std)
                image_indices_without_first = image_indices[1:]

                found_index = 0
                for index, v in enumerate(image_indices_without_first):
                    
                    if int(v) > int(threshold):
                        found_index = index
                        break
                
                if p_norm:
                    diff_entropy_kept = utils.normalize_arr(entropy_diff_list[:found_index+1])[-1]
                else:
                    diff_entropy_kept = entropy_diff_list[found_index]
            
                # Keep only absolute value
                diff_entropy_found.append(diff_entropy_kept)


        mean_entropy_diff = sum(diff_entropy_found) / len(diff_entropy_found)
        std_entropy_diff = np.std(diff_entropy_found)

        print('mean', mean_entropy_diff)
        print('std', std_entropy_diff)
            
        with open(p_output_path, 'w') as f:
            print("Erase", p_output_path, "previous file if exists")

        # now we can predict threshold img using `mean_entropy_diff`
        for line in lines:
            data = line.split(';')

            scene_name = data[0]
            zone_index = data[1]
            zone_index_str = data[2]
            threshold = data[3]
            image_indices = data[4].split(',')
            entropy_list = data[5].split(',')

            step_size = int(image_indices[1]) - int(image_indices[0])

            # one element is removed using this function (first element of list for computing first difference)
            entropy_diff_list = get_zone_diff_entropy(entropy_list, step_size, p_std)
            image_indices_without_first = image_indices[1:]

            # by default max index (if no stoppring criteria found)
            found_index = len(image_indices_without_first) - 1
            for index, v in enumerate(entropy_diff_list):

                if p_norm:
                    current_v = utils.normalize_arr(entropy_diff_list[:index+1])[-1]
                else:
                    current_v = v

                if mean_entropy_diff > current_v * k_factor:
                    found_index = index
                    break

            threshold_found = image_indices_without_first[found_index]

            with open(p_output_path, 'a') as f:
                f.write(scene_name + ';')
                f.write(zone_index + ';')
                f.write(zone_index_str + ';')
                f.write(threshold + ';')
                f.write(threshold_found + ';')
                f.write(str(mean_entropy_diff) + ';')
                f.write(str(std_entropy_diff) + ';')
                f.write(str(p_norm))
                f.write('\n')


if __name__== "__main__":
    main()
