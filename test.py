# Example:
# $ python test.py 0059.tif
#
import sys
import glob

import numpy as np

import cv2
import skimage
from skimage import exposure, io

import torch
from torchvision.utils import save_image

import segmentation_models_pytorch as smp


def preprocess(img,mn=0,mx=100):
    mx1 = np.max(img).astype(np.float32)
    mn1 = np.min(img).astype(np.float32)
    img = (img.astype(np.float32)-mn1)/(mx1-mn1)
#    img = exposure.equalize_adapthist(img.astype(np.uint16))
#    img = exposure.equalize_hist(img)

    i, j = np.percentile(img, (mn,mx))
    img = exposure.rescale_intensity(img, in_range=(i,j)).astype(np.float32)
    return img


def run(orgfile):
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.backends.cudnn.benchmark = True
    figsize = 512
    encoder = 'resnet18'
    modelparams = 'params/params.pth'

    model = smp.Unet(encoder, in_channels=1)
    model.load_state_dict(torch.load(modelparams, map_location=torch.device(dev)))

    im = io.imread(orgfile).astype(np.float32)
    im = cv2.resize(im,(figsize,figsize))
    im_p = preprocess(im,mn=1,mx=80)
    im_t = torch.from_numpy(im_p).unsqueeze(0).unsqueeze(0)

    model.eval()
    pred = model(im_t)

    return pred[0,0]


if __name__ == '__main__':
    args = sys.argv
    if len(args) == 2:
        with torch.no_grad():
            save_image(run(args[1]),"test.jpg")

    else: 
        print('error 1')




