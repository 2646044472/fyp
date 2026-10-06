##+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
## Created by: Donny You, RainbowSecret, JingyiXie
## Microsoft Research
## yuyua@microsoft.com
## Copyright (c) 2019
##
## This source code is licensed under the MIT-style license found in the
## LICENSE file in the root directory of this source tree 
##+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
## Modified for PKLNet 10.27 2021
## Modified by Xu Liang for PKLNet 10.19 2022

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pdb
import torch
from torch.utils import data
from torchvision import transforms


import lib.datasets.tools.transforms as trans
from lib.datasets.tools import cv2_aug_transforms_palm
# import lib.datasets.tools.pil_aug_transforms as pil_aug_trans


from lib.datasets.loader.MyDataset import DefaultLoader#, CSDataTestLoader
from lib.datasets.loader.MyTestDataset import TestLoader


# from lib.datasets.loader.default_loader import DefaultLoader, CSDataTestLoader
# from lib.datasets.loader.ade20k_loader import ADE20KLoader
# from lib.datasets.loader.lip_loader import LipLoader
# from lib.datasets.loader.offset_loader import DTOffsetLoader
from lib.datasets.tools.collate import collate
from lib.utils.tools.logger import Logger as Log

from lib.utils.distributed import get_world_size, get_rank, is_distributed


class DataLoader(object):

    def __init__(self, root_dir, batch_size=8):
        # self.configer = configer
        self.root_dir = root_dir
        self.batch_size = batch_size

        self.aug_train_transform = cv2_aug_transforms_palm.CV2AugCompose(split='train')
        self.aug_val_transform = cv2_aug_transforms_palm.CV2AugCompose(split='val')


        self.img_transform = trans.Compose([
            trans.ToTensor(),
            trans.Normalize(div_value=255.0, 
                            mean=[0.485, 0.456, 0.406],
                            std=[0.229, 0.224, 0.225]), 
            ])

        self.label_transform = trans.Compose([
            trans.ToLabel(),
            trans.ReLabel(255, -1), # padding region in cv2 aug -> 255 -> -1  ######
            ])

        self.keypoint_transform = None
             

    def get_trainloader(self):

        itemloader_train = DefaultLoader(  
            root_dir=self.root_dir, 
            aug_transform=self.aug_train_transform, 
            dataset='train', 
            img_transform=self.img_transform, 
            label_transform=self.label_transform, 
            keypoint_transform=self.keypoint_transform
        )

        trainloader = data.DataLoader(
            itemloader_train,
            batch_size=self.batch_size,            
            shuffle=True,
            drop_last=True,
            num_workers=4,
            collate_fn=lambda *args: collate(*args, trans_dict={"size_mode": "fix_size",
                                                                "input_size": [300/1, 400/1],##################################
                                                                "align_method": "only_pad",
                                                                "pad_mode": "random" })
        )
        return trainloader
            

    def get_valloader(self, dataset=None):
        dataset = 'val' if dataset is None else dataset        
        
        itemloader_val = DefaultLoader(  
            root_dir=self.root_dir, 
            aug_transform=self.aug_val_transform, 
            dataset=dataset, 
            img_transform=self.img_transform, 
            label_transform=self.label_transform
        )
        
        valloader = data.DataLoader(
            itemloader_val,
            batch_size=self.batch_size,
            shuffle=False,
            collate_fn=lambda *args: collate(*args, trans_dict={"size_mode": "diverse_size",
                                                                "align_method": "only_pad",
                                                                "pad_mode": "pad_right_down"})
        )
        return valloader


    def get_testloader(self):

        itemloader_test = TestLoader(  
            root_dir=self.root_dir, 
            dataset='', #'test', 
            img_transform=self.img_transform
        )

        testloader = data.DataLoader(
            itemloader_test,
            batch_size=self.batch_size,            
            shuffle=False,
            drop_last=False,
            # num_workers=4,
            collate_fn=lambda *args: collate(*args, trans_dict={"size_mode": "fix_size",
                                                                "input_size": [300/1, 400/1],##################################
                                                                "align_method": "only_pad",
                                                                "pad_mode": "random" })
        )
        return testloader





    # def get_testloader(self, dataset=None):
    #     dataset = 'test/image' if dataset is None else dataset
        
    #     Log.info('use CSDataTestLoader for test ...')
    #     test_loader = data.DataLoader(

    #         CSDataTestLoader(   root_dir=self.root_dir, 
    #                             dataset=dataset,
    #                             img_transform=self.img_transform
    #                          ),

    #         batch_size=self.batch_size,
    #         shuffle=False,
    #         collate_fn=lambda *args: collate(*args, trans_dict={"size_mode": "diverse_size", # diverse_size: image sizes of one mini-batch can be different
    #                                                             "align_method": "only_pad",
    #                                                             "pad_mode": "pad_right_down"})
    #         # collate_fn=lambda *args: collate(*args, trans_dict={"size_mode": "fix_size",
    #         #                                                     "input_size": [300/1, 400/1],##################################
    #         #                                                     "align_method": "only_pad",
    #         #                                                     "pad_mode": "random" })
    #     )
    #     return test_loader


if __name__ == "__main__":
    pass