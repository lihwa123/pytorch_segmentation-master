from base import BaseDataSet, BaseDataLoader
from utils import palette
import numpy as np
import os
import torch
import cv2
from PIL import Image
from glob import glob
from torch.utils.data import Dataset
from torchvision import transforms


class LLXDataset(BaseDataSet):
    """
    ADE20K dataset 
    http://groups.csail.mit.edu/vision/datasets/ADE20K/
    """

    def __init__(self, **kwargs):
        self.num_classes = 41  # 种类数，加背景151
        self.palette = palette.LLX_palette  # 调色盘
        super(LLXDataset, self).__init__(**kwargs)

    def _set_files(self):
        if self.split in ["training", "validation"]:
            # data\ADEChallengeData2016\images\training
            self.image_dir = os.path.join(self.root, 'images', self.split)
            # data\ADEChallengeData2016\annotations\training
            self.label_dir = os.path.join(self.root, 'annotations', self.split)
            # 图像和标注共同的名字
            self.files = [os.path.basename(path).split('.')[0] for path in glob(self.image_dir + '/*.tif')]
        else:
            raise ValueError(f"Invalid split name {self.split}")

    def _load_data(self, index):
        image_id = self.files[index]  # 图片名称
        image_path = os.path.join(self.image_dir, image_id + '.tif')
        label_path = os.path.join(self.label_dir, image_id + '.tif')
        image = np.asarray(Image.open(image_path).convert('RGB'), dtype=np.float32)
        label = np.asarray(Image.open(label_path), dtype=np.int32) - 1  # from -1 to 39
        return image, label, image_id


class LLX(BaseDataLoader):
    def __init__(self, data_dir, batch_size, split, crop_size=None, base_size=None, scale=True, num_workers=1,
                 val=False,
                 shuffle=False, flip=False, rotate=False, blur=False, augment=False, val_split=None, return_id=False):
        self.MEAN = [0.48897059, 0.46548275, 0.4294]  # 均值
        self.STD = [0.22861765, 0.22948039, 0.24054667]  # 方差

        kwargs = {
            'root': data_dir,  # 文件路径 data/ADEChallengeData2016
            'split': split,  # 训练集或验证集文件夹名字 training validation
            'mean': self.MEAN,  # 均值
            'std': self.STD,  # 方差
            'augment': augment,  # 数据增强
            'crop_size': crop_size,
            'base_size': base_size,
            'scale': scale,
            'flip': flip,
            'blur': blur,
            'rotate': rotate,
            'return_id': return_id,
            'val': val
        }

        self.dataset = LLXDataset(**kwargs)
        super(LLX, self).__init__(self.dataset, batch_size, shuffle, num_workers, val_split)
