# main imports
import os, sys
import argparse
import time
import numpy as np
import random
import multiprocessing

# image import
from PIL import Image
import cv2

# ml library
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVR
from sklearn.metrics import accuracy_score, f1_score
#from sklearn.externals import joblib
import joblib

# modules and config imports
sys.path.insert(0, '') # trick to enable import of main folder module

import custom_config as cfg
from modules.utils import data as dt
from ipfml.processing import transform, segmentation, compression

dataset_folder = cfg.dataset_path
scenes_list    = cfg.scenes_names
zones_indices  = cfg.zones_indices

saved_models_folder = 'saved_models'

def main():

    parser = argparse.ArgumentParser(description="Create output dataset converted using noise mask")

    parser.add_argument('--data', type=str, help='noise mask dataset folder')
    parser.add_argument('--output', type=str, help='name of output model')
    parser.add_argument('--train_scenes', type=str, help='list of train scenes used', default='')
    parser.add_argument('--norm', type=int, help='list of train scenes used', default=0)

    args = parser.parse_args()

    p_data         = args.data
    p_output       = args.output
    p_train_scenes = args.train_scenes.split(',')
    p_norm         = bool(args.norm)

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


    train_dict_data = []
    test_dict_data = []

    print('--------------------------------------------')
    
    # create dictionnary of threshold and get all images path
    for scene in scenes_list:

        scene_path = os.path.join(p_data, scene)
        print('Reading data from', scene)

        for img_path in sorted(os.listdir(scene_path)):

            scene_img_path = os.path.join(scene_path, img_path)

            blocks = segmentation.divide_in_blocks(Image.open(scene_img_path), (200, 200))

            current_img_index = dt.get_scene_image_quality(img_path)

            for index, block in enumerate(blocks):

                label = 1

                if current_img_index < thresholds[scene][index]:
                    label = -1

                data = (label, np.array(block).reshape(200 * 200))

                if scene in scenes_selected:
                    train_dict_data.append(data)
                else:
                    test_dict_data.append(data)

    print('--------------------------------------------')
    print('Train set size', len(train_dict_data))
    print('Test set size', len(test_dict_data))

    random.shuffle(train_dict_data)

    if p_norm:
        x_train_data = [ x / 255. for (y, x) in train_dict_data ]
    else:
        x_train_data = [ x / 255. for (y, x) in train_dict_data ]

    y_train_data = [ y for (y, x) in train_dict_data ]

    # x_test_data = [ x for (y, x) in test_dict_data ]
    # y_test_data = [ y for (y, x) in test_dict_data ]

    print('--------------------------------------------')
    print('Start training model over', scenes_selected)

    # construct model
    #model = SVC(C=2, gamma=2, kernel='rbf', verbose=True)

    parameters = {
        "kernel": ["rbf"],
        "C": [1, 2, 4, 8, 16, 32, 100,1000],
        "gamma": [1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 10, 100]
    }

    print('Number of CPUs found', multiprocessing.cpu_count())
    model = GridSearchCV(SVR(), parameters, cv=5, verbose=2, n_jobs=multiprocessing.cpu_count())
    model.fit(x_train_data, y_train_data)
    
    # y_train_predict = model.predict(x_train_data)
    # y_test_predict = model.predict(x_test_data)

    # train_val_accuracy = accuracy_score(y_train_data, y_train_predict)
    # test_val_accuracy = accuracy_score(y_test_data, y_test_predict)

    # print('--------------------------------------------')
    # print('Train accuracy', train_val_accuracy, '%')
    # print('Test accuracy', test_val_accuracy, '%')

    if not os.path.exists(saved_models_folder):
        os.makedirs(saved_models_folder)

    joblib.dump(model, os.path.join(saved_models_folder, p_output + '.joblib'))

if __name__ == "__main__":
    main()