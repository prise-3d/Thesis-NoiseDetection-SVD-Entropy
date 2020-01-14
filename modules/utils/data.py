import os

from PIL import Image

from ..config.cnn_config import *


_scenes_names_prefix   = '_scenes_names'
_scenes_indices_prefix = '_scenes_indices'

# store all variables from current module context
context_vars = vars()

def get_renderer_scenes_indices(renderer_name):

    if renderer_name not in renderer_choices:
        raise ValueError("Unknown renderer name")

    if renderer_name == 'all':
        return scenes_indices
    else:
        return context_vars[renderer_name + _scenes_indices_prefix]

def get_renderer_scenes_names(renderer_name):

    if renderer_name not in renderer_choices:
        raise ValueError("Unknown renderer name")

    if renderer_name == 'all':
        return scenes_names
    else:
        return context_vars[renderer_name + _scenes_names_prefix]


def get_scene_image_quality(img_path):

    # if path getting last element (image name) and extract quality
    img_postfix = img_path.split('/')[-1].split(scene_image_quality_separator)[-1]
    img_quality = img_postfix.replace(scene_image_extension, '')

    return int(img_quality)


def get_scene_image_postfix(img_path):

    # if path getting last element (image name) and extract quality
    img_postfix = img_path.split('/')[-1].split(scene_image_quality_separator)[-1]
    img_quality = img_postfix.replace(scene_image_extension, '')

    return img_quality


def get_scene_image_prefix(img_path):

    # if path getting last element (image name) and extract prefix
    img_prefix = img_path.split('/')[-1].split(scene_image_quality_separator)[0]

    return img_prefix


def augmented_data_image(block, output_folder, prefix_image_name):

    rotations = [0, 90, 180, 270]
    img_flip_labels = ['original', 'horizontal', 'vertical', 'both']

    horizontal_img = block.transpose(Image.FLIP_LEFT_RIGHT)
    vertical_img = block.transpose(Image.FLIP_TOP_BOTTOM)
    both_img = block.transpose(Image.TRANSPOSE)

    flip_images = [block, horizontal_img, vertical_img, both_img]

    # rotate and flip image to increase dataset size
    for id, flip in enumerate(flip_images):
        for rotation in rotations:
            rotated_output_img = flip.rotate(rotation)

            output_reconstructed_filename = prefix_image_name + post_image_name_separator
            output_reconstructed_filename = output_reconstructed_filename + img_flip_labels[id] + '_' + str(rotation) + '.png'
            output_reconstructed_path = os.path.join(output_folder, output_reconstructed_filename)

            if not os.path.exists(output_reconstructed_path):
                rotated_output_img.save(output_reconstructed_path)