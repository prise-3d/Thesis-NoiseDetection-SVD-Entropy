# main imports
import numpy as np
import pandas as pd
import sys, os, argparse

# image processing
from PIL import Image
from ipfml import utils
from ipfml.processing import transform, segmentation, compression

# modules and config imports
sys.path.insert(0, '') # trick to enable import of main folder module

import custom_config as cfg
from modules.utils import data as dt

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


'''
Compute for list of images entropy list of these images
'''
def get_zone_entropy(images, interval, imnorm=False):
    
    entropy_list = []
    
    begin, end = interval

    for img in images:
        img_lab = transform.get_LAB_L(img)
        
        if imnorm:
            img_lab = np.array(img_lab / 255.)

        sigma = compression.get_SVD_s(img_lab)
        sigma = sigma[begin:end]

        s_entropy = utils.get_entropy(sigma)
        entropy_list.append(s_entropy)
        
    return entropy_list


def main():

    parser = argparse.ArgumentParser(description="Output data file")

    parser.add_argument('--vdp_folder', type=str, help='vdp folder images with thresholds data')
    parser.add_argument('--output', type=str, help='save entropy for each zone of each scene into file')
    parser.add_argument('--interval', type=str, help='svd interval to use', default="0,200")
    parser.add_argument('--imnorm', type=int, help="specify if image is normalized before computing something", default=0, choices=[0, 1])

    args = parser.parse_args()

    p_vdp_folder = args.vdp_folder
    p_output     = args.output
    p_interval   = tuple(map(int, args.interval.split(',')))
    p_imnorm     = args.imnorm

    # create output path if not exists
    p_output_path = os.path.join(cfg.output_data_folder, cfg.data_generated, p_output)
    if not os.path.exists(cfg.output_data_folder):
        os.makedirs(os.path.join(cfg.output_data_folder, cfg.data_generated))
    
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

        scene_path = os.path.join(p_vdp_folder, scene)

        threshold_list = []

        for zone in zones_list:
            zone_path = os.path.join(scene_path, zone)

            with open(os.path.join(zone_path, cfg.seuil_expe_filename), 'r') as f:
                threshold_list.append(int(f.readline()))

        thresholds[scene] = threshold_list
        images_path[scene] = sorted([os.path.join(scene_path, img) for img in os.listdir(scene_path) if cfg.scene_image_extension in img])
        number_of_images = number_of_images + len(images_path[scene])



    with open(p_output_path, 'w') as f:
        print("Erase", p_output_path, "previous file if exists")

    image_counter = 0
    # compute entropy for each zones of each scene images
    for scene in scenes_list:

        image_indices = [ dt.get_scene_image_quality(img_path) for img_path in images_path[scene] ]

        blocks_entropy = []

        # append empty list
        for zone in zones_list:
            blocks_entropy.append([])

        for img_path in images_path[scene]:

            blocks = segmentation.divide_in_blocks(Image.open(img_path), (200, 200))
            entropy_list = get_zone_entropy(blocks, p_interval, p_imnorm)

            for index, entropy in enumerate(entropy_list):
                blocks_entropy[index].append(entropy)

            # write progress bar
            write_progress((image_counter + 1) / number_of_images)
            
            image_counter = image_counter + 1
        
        # write data into files
        with open(p_output_path, 'a') as f:
            for index, zone in enumerate(zones_list):
                f.write(scene + ';')
                f.write(str(index) + ';')
                f.write(zone + ';')

                f.write(str(thresholds[scene][index]) + ';')

                for index_img, img_quality in enumerate(image_indices):
                    f.write(str(img_quality))

                    if index_img + 1 < len(image_indices):
                        f.write(',')

                f.write(';')

                for index_v, v in enumerate(blocks_entropy[index]):
                    f.write(str(v))

                    if index_v + 1 < len(blocks_entropy[index]):
                        f.write(',')

                
                f.write(';\n')


if __name__== "__main__":
    main()
