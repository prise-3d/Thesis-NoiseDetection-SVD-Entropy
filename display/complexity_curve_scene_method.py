# main imports
import numpy as np
import pandas as pd
import sys, os, argparse

# image processing
from PIL import Image
from ipfml import utils
from ipfml.processing import transform, segmentation

import matplotlib.pyplot as plt
import ipfml.iqa.fr as fr

# modules and config imports
sys.path.insert(0, '') # trick to enable import of main folder module

import custom_config as cfg

dataset_folder = cfg.dataset_path
scenes_list    = cfg.scenes_names
zones_indices  = cfg.zones_indices

block_size = (200, 200)
display_xticks_step = 100


'''
Compute diff from entropy list (first element is used as reference)
'''
def get_zone_diff_entropy(entropy_list, std=False):
    
    diff_list = []
    previous_value = 0

    entropy_list = list(map(float, entropy_list))

    if std:
        entropy_list_norm = utils.normalize_arr(entropy_list)
    
    for index, value in enumerate(entropy_list):
        
        if index > 0:
            diff = previous_value - value

            if std:
                # ponderation using `std` from list normalized
                diff = diff * np.std(entropy_list_norm[:(index+1)])

            diff_list.append(diff)

        previous_value = value
        
    return diff_list


def display_estimated_thresholds(scene, displayed_data, info, metric, norm=True, save=True):
    
    colors = ['C0', 'C1', 'C2', 'C3', 'C4']
    
    #plt.figure(figsize=(25, 20))
    plt.rc('xtick', labelsize=16)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=16)    # fontsize of the tick labels
    
    fig, axs = plt.subplots(4, 4, figsize=(25, 20))
    fig.suptitle('Complexity value evolution in scene' + scene + " | " + info, fontsize=24)
    
    for i, ax in enumerate(axs.flat):
        
        complexity_values = get_zone_diff_entropy(displayed_data[i]['data'])
        error_values = displayed_data[i]['errors'][1:] # remove first element such as complexity
        human_threshold = int(displayed_data[i]['human_threshold'])

        if norm:
            complexity_values = utils.normalize_arr(complexity_values)
            error_values = utils.normalize_arr(error_values)

        # display evolution curve and error curve for each zone
        ax.set_title(displayed_data[i]['zone'])

        ax.plot(complexity_values, 
             color=colors[0], 
             label='complexity values')

        ax.plot(error_values, 
            color=colors[1], 
            label= metric + ' error')
        

        # get max `y` value
        max_y = 0

        max_complexity = max(complexity_values)
        max_error = max(error_values)
        max_found = max(max_error, max_complexity) 
        
        if max_found > max_y:
            max_y = max_found

        # for each indices
        image_indices = displayed_data[i]['steps'][1:] # remove first element such as complexity

        index_threshold = 0
        while image_indices[index_threshold] < human_threshold: 
            index_threshold = index_threshold + 1

        ax.plot([index_threshold, index_threshold], [max_y, 0], 'k-', lw=2, color=colors[2])

        # set each labels
        x_labels = [str(label) for label in image_indices if int(label) % display_xticks_step == 0]
        x = [i for i, v in enumerate(image_indices) if int(v) % display_xticks_step == 0 ]
        ax.set_xticks(x)
        ax.set_xticklabels(x_labels, rotation=45)
        #ax.legend(fontsize=16)

        if i >= len(axs.flat) - 1:
            handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper right', bbox_to_anchor=(0.9, 0.95), fontsize=18)

    for ax in axs.flat:
        ax.label_outer()
    
    #fig.tight_layout()
    if save:
        fig_folder = os.path.join(cfg.output_data_folder, cfg.data_fig_folder)

        if not os.path.exists(fig_folder):
            os.makedirs(fig_folder)

        fig.savefig(os.path.join(fig_folder, 'temp.png'), transparent=True)
    else:
        plt.show()



def main():

    parser = argparse.ArgumentParser(description="Read and compute entropy data file")

    parser.add_argument('--data', type=str, help='entropy file data with estimated threshold to read and compute')
    parser.add_argument('--scene', type=str, help='Scene index to use', choices=cfg.scenes_indices)
    parser.add_argument('--metric', type=str, help='metric to use to compare', choices=['ssim', 'mse', 'rmse', 'mae', 'psnr'])
    parser.add_argument('--norm', type=int, help='normalize or not values', choices=[0, 1], default=0)
    parser.add_argument('--info', type=str, help='title information to add')

    args = parser.parse_args()

    p_data   = args.data
    p_scene  = args.scene
    p_metric = args.metric
    p_norm   = args.norm
    p_info   = args.info

    # check fr_iqa metric
    try:
        fr_iqa = getattr(fr, p_metric)
    except AttributeError:
        raise NotImplementedError("FR IQA `{}` not implement `{}`".format(fr.__name__, p_metric))

    scenes_list = cfg.scenes_names
    scenes_indices = cfg.scenes_indices

    scene_index = scenes_indices.index(p_scene.strip())
    scene = scenes_list[scene_index]

    displayed_data = {}
    steps_zones = []
    scene_found = False
    reference_zones = None

    # read line by line file to estimate threshold entropy stopping criteria
    with open(p_data, 'r') as f:
        lines = f.readlines()

        for line in lines:

            data = line.split(';')
            scene_name = data[0]
            zone_index = int(data[1])
            steps = data[4].split(',')

            if scene_name == scene:
                
                if not scene_found:
                    scene_folder = os.path.join(cfg.dataset_path, scene_name)
                    images = sorted([img for img in os.listdir(scene_folder) if cfg.scene_image_extension in img])
                    images_scene = [Image.open(os.path.join(scene_folder, img)) for img in images]
                    scene_found = True

                    # get zones of each step images
                    for i, _ in enumerate(steps):
                        steps_zones.append(segmentation.divide_in_blocks(images_scene[i], block_size))

                    # get zone of reference
                    reference_name = cfg.references_scenes[scene_index]
                    reference_path = os.path.join(cfg.references_folder, reference_name)
                    reference_zones = segmentation.divide_in_blocks(Image.open(reference_path), block_size)


                # TODO : load images at each step and compare error
                # store all needed data
                displayed_data[zone_index] = {}
                displayed_data[zone_index]['zone'] = data[2]
                displayed_data[zone_index]['human_threshold'] = data[3]
                displayed_data[zone_index]['steps'] = list(map(int, steps))
                displayed_data[zone_index]['data'] = list(map(float, data[5].split(',')))

                errors = []
                # get errors from images zones (using step and reference)
                for i, _ in enumerate(steps):
                    noisy_block = steps_zones[i][zone_index]
                    reference_block = reference_zones[zone_index]

                    step_error = fr_iqa(noisy_block, reference_block)
                    errors.append(step_error)

                displayed_data[zone_index]['errors'] = errors

    display_estimated_thresholds(scene, displayed_data, p_info, p_metric, p_norm)

if __name__== "__main__":
    main()
