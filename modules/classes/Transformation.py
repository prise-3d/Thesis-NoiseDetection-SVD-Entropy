# main imports
import os
import numpy as np

# image processing imports
from ipfml.processing import transform
from ipfml.processing import reconstruction
from ipfml.filters import convolution, kernels
from ipfml import utils

from PIL import Image


# Transformation class to store transformation method of image and get usefull information
class Transformation():

    def __init__(self, _transformation, _param, _size):
        self.transformation = _transformation
        self.param = _param
        self.size = _size

    def getTransformedImage(self, img):

        if self.transformation == 'svd_reconstruction':
            begin, end = list(map(int, self.param.split(',')))
            data = reconstruction.svd(img, [begin, end])

        if self.transformation == 'ipca_reconstruction':
            n_components, batch_size = list(map(int, self.param.split(',')))
            data = reconstruction.ipca(img, n_components, batch_size)

        if self.transformation == 'fast_ica_reconstruction':
            n_components = self.param
            data = reconstruction.fast_ica(img, n_components)

        if self.transformation == 'min_diff_filter':
            w_size, h_size = list(map(int, self.param.split(',')))
            h, w = list(map(int, self.size.split(',')))

            # bilateral with window of size (`w_size`, `h_size`)
            lab_img = transform.get_LAB_L(img)

            lab_img = Image.fromarray(lab_img)
            lab_img.thumbnail((h, w))

            diff_img = convolution.convolution2D(lab_img, kernels.min_bilateral_diff, (w_size, h_size))

            data = np.array(diff_img*255, 'uint8')
            
        if self.transformation == 'static':
            # static content, we keep input as it is
            data = img

        return data
    
    def getTransformationPath(self):

        path = self.transformation

        if self.transformation == 'svd_reconstruction':
            begin, end = list(map(int, self.param.split(',')))
            path = os.path.join(path, str(begin) + '_' + str(end))

        if self.transformation == 'ipca_reconstruction':
            n_components, batch_size = list(map(int, self.param.split(',')))
            path = os.path.join(path, 'N' + str(n_components) + '_' + str(batch_size))

        if self.transformation == 'fast_ica_reconstruction':
            n_components = self.param
            path = os.path.join(path, 'N' + str(n_components))

        if self.transformation == 'min_diff_filter':
            w_size, h_size = list(map(int, self.param.split(',')))
            w, h = list(map(int, self.size.split(',')))
            path = os.path.join(path, 'W_' + str(w_size)) + '_' + str(h_size) + '_S_' + str(w) + '_' + str(h)

        if self.transformation == 'static':
            # param contains image name to find for each scene
            path = self.param

        return path

    def getName(self):
        return self.transformation

    def getParam(self):
        return self.param

    def __str__( self ):
        return self.transformation + ' transformation with parameter : ' + self.param