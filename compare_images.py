# main imports
import os, sys, argparse

# image processing imports
from PIL import Image
import ipfml.iqa.fr as fr

def main():

    parser = argparse.ArgumentParser(description="Compare 2 images and return difference using metric")

    parser.add_argument('--img1', type=str, help='First image')
    parser.add_argument('--img2', type=str, help='Second image')
    parser.add_argument('--metric', type=str, help='metric to use to compare', choices=['ssim', 'mse', 'rmse', 'mae', 'psnr'])
    args = parser.parse_args()

    param_img1 = args.img1
    param_img2 = args.img2
    param_metric  = args.metric

    image1 = Image.open(param_img1)
    image2 = Image.open(param_img2)

    try:
        fr_iqa = getattr(fr, param_metric)
    except AttributeError:
        raise NotImplementedError("FR IQA `{}` not implement `{}`".format(fr.__name__, param_metric))

    print(fr_iqa(image1, image2))


if __name__== "__main__":
    main()