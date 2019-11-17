"""VOC Dataset Classes

Original author: Francisco Massa
https://github.com/fmassa/vision/blob/voc_dataset/torchvision/datasets/voc.py

Updated by: Ellis Brown, Max deGroot
"""
import os.path as osp
import sys
import torch
import torch.utils.data as data
import cv2
import numpy as np
import os
import re

# 两类需要识别
SIXray_CLASSES = (
    '带电芯充电宝', '不带电芯充电宝'
)

XRAY_ROOT = osp.abspath('./data_sets/3000')


class SIXrayAnnotationTransform(object):
    """Transforms a VOC annotation into a Tensor of bbox coords and label index
    Initilized with a dictionary lookup of classnames to indexes

    Arguments:
        class_to_ind (dict, optional): dictionary lookup of classnames -> indexes
            (default: alphabetic indexing of VOC's 20 classes)
        keep_difficult (bool, optional): keep difficult instances or not
            (default: False)
        height (int): height
        width (int): width
    """

    def __init__(self, class_to_ind=None, keep_difficult=False):
        self.class_to_ind = class_to_ind or dict(
            zip(SIXray_CLASSES, range(len(SIXray_CLASSES))))
        self.keep_difficult = keep_difficult
        # 添加的记录所有小类总数
        self.type_dict = {}
        # 记录大类数量
        self.type_sum_dict = {}

    def __call__(self, target, width, height, idx):
        """
        Arguments:
            target (annotation) : the target annotation to be made usable
                will be an ET.Element
            it has been changed to the path of annotation-2019-07-10
        Returns:
            a list containing lists of bounding boxes  [bbox coords, class name]
        """

        # 遍历Annotation
        res = []
        # 读取标注的txt文件
        with open(target, "r", encoding='utf-8') as f1:
            dataread = f1.readlines()
        for annotation in dataread:
            bndbox = []
            # 分解标注数据
            temp = annotation.split()
            # 标注数据格式 :
            #   01013328.TIFF 带电芯充电宝 631 700 737 879
            # 标注名称: 带芯充电宝 / 不带芯充电宝
            name = temp[1]
            # 只读两类
            if name != '带电芯充电宝' and name != '不带电芯充电宝':
                continue
            xmin = int(temp[2]) / width
            # 只读取V视角的 ? 为什么只读V视角
            if xmin > 1:
                continue
            if xmin < 0:
                xmin = 0
            ymin = int(temp[3]) / height
            if ymin < 0:
                ymin = 0
            xmax = int(temp[4]) / width
            if xmax > 1:  # 是这么个意思吧？
                xmax = 1
            ymax = int(temp[5]) / height
            if ymax > 1:
                ymax = 1
            bndbox.append(xmin)
            bndbox.append(ymin)
            bndbox.append(xmax)
            bndbox.append(ymax)
            label_idx = self.class_to_ind[name]
            bndbox.append(label_idx)
            res += [bndbox]  # [xmin, ymin, xmax, ymax, label_ind]
        if len(res) == 0:
            return [[0, 0, 0, 0, 3]]
        return res


class SIXrayDetection(data.Dataset):
    """VOC Detection Dataset Object

    input is image, target is annotation

    Arguments:
        root (string): filepath to VOCdevkit folder.
        image_set (string): imageset to use (eg. 'train', 'val', 'test')
        transform (callable, optional): transformation to perform on the
            input image
        target_transform (callable, optional): transformation to perform on the
            target `annotation`
            (eg: take in caption string, return tensor of word indices)
        dataset_name (string, optional): which dataset to load
            (default: 'VOC2007')
    """

    def __init__(self, root,
                 image_sets,
                 transform=None, target_transform=SIXrayAnnotationTransform(),
                 dataset_name='Xray0723_bat_core_coreless'):
        self.root = root
        self.image_set = image_sets
        self.transform = transform
        self.target_transform = target_transform
        self.name = dataset_name
        self._annopath = osp.join('%s' % self.root, 'Annotation', 'battery_%s.txt')
        self._imgpath = osp.join('%s' % self.root, 'Image', 'battery_%s.jpg')
        self.ids = list_ids(XRAY_ROOT, "jpg")

        print(self.ids)

    def __getitem__(self, index):
        im, gt, h, w, og_im = self.pull_item(index)

        return im, gt

    def __len__(self):
        return len(self.ids)

    def pull_item(self, index):
        img_id = self.ids[index]
        target = self._annopath % img_id  # 注释目录
        img = cv2.imread(self._imgpath % img_id)

        if img is None:
            print('\n错误:未找到图像文件\n')
            sys.exit(1)

        height, width, channels = img.shape
        og_img = img

        if self.target_transform is not None:
            target = self.target_transform(target, width, height, img_id)

        if self.transform is not None:
            target = np.array(target)
            img, boxes, labels = self.transform(img, target[:, :4], target[:, 4])
            # to rgb
            img = img[:, :, (2, 1, 0)]
            # img = img.transpose(a2, 0, a1)
            target = np.hstack((boxes, np.expand_dims(labels, axis=1)))
        return torch.from_numpy(img).permute(2, 0, 1), target, height, width, og_img

    # 根据ID 获取图片
    def pull_image(self, index):
        '''Returns the original image object at index in PIL form

        Note: not using self.__getitem__(), as any transformations passed in
        could mess up this functionality.

        Argument:
            index (int): index of img to show
        Return:
            PIL img
        '''
        img_id = self.ids[index]
        return cv2.imread(self._imgpath % img_id, cv2.IMREAD_COLOR)

    # 根据ID 获取标注
    def pull_annotation(self, index):
        img_id = self.ids[index]
        annos = []
        # 读取标注文件
        with open(self._annopath % img_id, "r", encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                temp = line.split()
                fileName = temp[1]
                if fileName != '带电芯充电宝' and fileName != '不带电芯充电宝':
                    continue
                img_tuple = (fileName, (int(temp[2]), int(temp[3])), (int(temp[4]), int(temp[5])))
                annos.append(img_tuple)
        return annos

    def pull_anno(self, index):
        '''Returns the original annotation of image at index

        Note: not using self.__getitem__(), as any transformations passed in
        could mess up this functionality.

        Argument:
            index (int): index of img to get annotation of
        Return:
            list:  [img_id, [(label, bbox coords),...]]
                eg: ('001718', [('dog', (96, 13, 438, 332))])
        '''
        img_id = self.ids[index]
        annos = []
        # 读取标注文件
        with open(self._annopath % img_id, "r", encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                temp = line.split()
                file_name = temp[1]
                if file_name != '带电芯充电宝' and file_name != '不带电芯充电宝':
                    continue
                img_tuple = [file_name, (int(temp[2]), int(temp[3]), int(temp[4]), int(temp[5]))]
                annos.append(img_tuple)
        return img_id, annos


class BaseTransform:
    def __init__(self, size, mean):
        self.size = size
        self.mean = np.array(mean, dtype=np.float32)

    def __call__(self, image, boxes=None, labels=None):
        return base_transform(image, self.size, self.mean), boxes, labels


def base_transform(image, size, mean):
    x = cv2.resize(image, (size, size)).astype(np.float32)
    x -= mean
    x = x.astype(np.float32)
    return x


def list_ids(root, allTypes):
    res = []
    re_img_id = re.compile(r'(\D+)(\d+).(\w+)')
    types = allTypes.split(",")
    for root_temp, dirs, files in os.walk(root, topdown=True):
        for name in files:
            match = re_img_id.match(name)
            if match:
                if match.groups()[2] in types:
                    res.append(match.groups()[1])
    return res
