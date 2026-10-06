#!/usr/bin/env python
#-*- coding:utf-8 -*-
# Author: Donny You(youansheng@gmail.com)
# Visualizer for segmentation.


import os

import cv2
import numpy as np

from lib.datasets.tools.transforms import DeNormalize
from lib.utils.tools.logger import Logger as Log

PROJECT_DIR ='./rst/'

SEG_DIR = 'vis/results/seg'


class SegVisualizer(object):

    def __init__(self, configer=None):
        self.configer = configer
        self.colorlist = [[0,255,0], [255, 0,0], [0, 80, 100], [0, 0, 230], [128, 64, 128], [244, 35, 232], [70, 70, 70], [102, 102, 156], [190, 153, 153],
                     [153, 153, 153], [250, 170, 30], [220, 220, 0], [107, 142, 35], [152, 251, 152],
                     [70, 130, 180], [220, 20, 60], [255, 0, 0], [0, 0, 142], [0, 0, 70], [0, 60, 100],
                     [119, 11, 32]]
        self.num_class = 2

    def vis_fn(self, preds, targets, ori_img_in=None, name='default', sub_dir='fn'):
        base_dir = os.path.join(PROJECT_DIR, SEG_DIR, sub_dir)
        if not os.path.exists(base_dir):
            Log.error('Dir:{} not exists!'.format(base_dir))
            os.makedirs(base_dir)

        # print(preds.size())
        if not isinstance(preds, np.ndarray):
            # print(preds.size(), len(preds.size()))
            if len(preds.size()) > 3:
                Log.error('Preds size is not valid.')
                exit(1)

            elif len(preds.size()) == 3:
                preds = preds.clone().data.cpu().numpy()
                # print(preds)
                # print(preds.shape)
                # print(len(preds.shape))

            elif len(preds.size()) == 2:
                preds = preds.unsqueeze(0).data.cpu().numpy()

        else:
            if len(preds.shape) > 3:
                Log.error('Preds size is not valid.')
                exit(1)

            if len(preds.shape) == 2:
                preds = preds.unsqueeze(0)

        if not isinstance(targets, np.ndarray):

            if len(targets.size()) == 3:
                targets = targets.clone().data.cpu().numpy()

            elif len(targets.size()) == 2:
                targets = targets.unsqueeze(0).data.cpu().numpy()

        else:
            if len(targets.shape) == 2:
                targets = targets.unsqueeze(0)

        if ori_img_in is not None:
            if not isinstance(ori_img_in, np.ndarray):
                if len(ori_img_in.size()) < 3:
                    Log.error('Image size is not valid.')
                    exit(1)

                elif len(ori_img_in.size()) == 4:
                    ori_img_in = ori_img_in.data.cpu()

                elif len(ori_img_in.size()) == 3:
                    ori_img_in = ori_img_in.unsqueeze(0).data.cpu()

                ori_img = ori_img_in.clone()
                for i in range(ori_img_in.size(0)):
                    # ori_img[i] = DeNormalize(div_value=255.0,
                    #                          mean=[0.485, 0.456, 0.406],
                    #                          std=[0.229, 0.224, 0.225])(ori_img_in.clone())     
                    ori_img[i] = DeNormalize(div_value=255.0,
                                             mean=[0.485, 0.456, 0.406],
                                             std=[0.229, 0.224, 0.225])(ori_img_in[i].clone())                                             


                # ori_img = ori_img.numpy().transpose(2, 3, 1).astype(np.uint8)
                ori_img = ori_img.numpy().transpose(0, 2, 3, 1).astype(np.uint8)

            else:
                if len(ori_img_in.shape) == 3:
                    ori_img_in = ori_img_in.unsqueeze(0)

                ori_img = ori_img_in.copy()

        for img_id in range(preds.shape[0]):
            label = targets[img_id]
            pred = preds[img_id]
            # print('-------', pred.max(), pred.min())
            # pred = (pred-pred.min())/(pred.max()-pred.min())
            # pred[pred>0.7] = 1
            # pred[pred<=0.7] = 0
            pred[pred>0] = 1
            pred[pred<=0] = 0
            pred = pred.astype(np.uint8)
            # print('-------', pred.max(), pred.min())
            result = np.zeros(shape=(pred.shape[0], pred.shape[1], 3), dtype=np.uint8)

            
            for i in range(self.num_class):
                mask0 = np.zeros_like(label, dtype=np.uint8)
                mask1 = np.zeros_like(label, dtype=np.uint8)
                mask0[label[:] == i] += 1
                mask0[pred[:] == i] += 1
                mask1[pred[:] == i] += 1
                result[mask0[:] == 1] = self.colorlist[i]
                result[mask1[:] == 1] = (0, 0, 0)

            image_result = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
            # if ori_img_in is not None:
            #     image_result  = cv2.addWeighted(ori_img[i], 0.6, image_result, 0.4, 0)
            
            image_result  = cv2.addWeighted(ori_img[img_id], 0.6, image_result, 0.4, 0)            

            cv2.imwrite(os.path.join(base_dir, '{}_{}.jpg'.format(name, img_id)), image_result)

    def vis_fp(self, preds, targets, ori_img_in=None, name='default', sub_dir='fp'):
        base_dir = os.path.join(PROJECT_DIR, SEG_DIR, sub_dir)
        if not os.path.exists(base_dir):
            Log.error('Dir:{} not exists!'.format(base_dir))
            os.makedirs(base_dir)

        if not isinstance(preds, np.ndarray):
            if len(preds.size()) > 3:
                Log.error('Preds size is not valid.')
                exit(1)

            elif len(preds.size()) == 3:
                preds = preds.clone().data.cpu().numpy()

            elif len(preds.size()) == 2:
                preds = preds.unsqueeze(0).data.cpu().numpy()

        else:
            if len(preds.shape) > 3:
                Log.error('Preds size is not valid.')
                exit(1)

            if len(preds.shape) == 2:
                preds = preds.unsqueeze(0)

        if not isinstance(targets, np.ndarray):

            if len(targets.size()) == 3:
                targets = targets.clone().data.cpu().numpy()

            elif len(targets.size()) == 2:
                targets = targets.unsqueeze(0).data.cpu().numpy()

        else:
            if len(targets.shape) == 2:
                targets = targets.unsqueeze(0)

        if ori_img_in is not None:
            if not isinstance(ori_img_in, np.ndarray):
                if len(ori_img_in.size()) < 3:
                    Log.error('Image size is not valid.')
                    exit(1)

                elif len(ori_img_in.size()) == 4:
                    ori_img_in = ori_img_in.data.cpu()

                elif len(ori_img_in.size()) == 3:
                    ori_img_in = ori_img_in.unsqueeze(0).data.cpu()

                ori_img = ori_img_in.clone()
                # print(ori_img.shape)
                for i in range(ori_img_in.size(0)):
                    ori_img[i] = DeNormalize(div_value=255.0,
                                             mean=[0.485, 0.456, 0.406],
                                             std=[0.229, 0.224, 0.225])(ori_img_in[i].clone())
                # print(ori_img.shape)              

                ori_img = ori_img.numpy().transpose(0, 2, 3, 1).astype(np.uint8)
  
                # print(ori_img.shape)

            else:
                if len(ori_img_in.shape) == 3:
                    ori_img_in = ori_img_in.unsqueeze(0)

                ori_img = ori_img_in.copy()


        for img_id in range(preds.shape[0]):
            label = targets[img_id]
            pred = preds[img_id]
            # print('-------', pred.max(), pred.min())
            # pred = (pred-pred.min())/(pred.max()-pred.min())
            # pred[pred>0.7] = 1
            # pred[pred<=0.7] = 0
            pred[pred>0] = 1
            pred[pred<=0] = 0
            pred = pred.astype(np.uint8)
            # print('-------', pred.max(), pred.min())
            result = np.zeros(shape=(pred.shape[0], pred.shape[1], 3), dtype=np.uint8)

            for i in range(self.num_class):
                mask0 = np.zeros_like(label, dtype=np.uint8)
                mask1 = np.zeros_like(label, dtype=np.uint8)
                mask0[label[:] == i] += 1
                mask0[pred[:] == i] += 1
                mask1[label[:] == i] += 1
                result[mask0[:] == 1] = self.colorlist[i]
                result[mask1[:] == 1] = (0, 0, 0)

            image_result = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
            # if ori_img_in is not None:
            #     # print(ori_img.shape, image_result.shape, type(ori_img), type(image_result), ori_img[i].shape, type(ori_img[i]))
            #     image_result = cv2.addWeighted(ori_img[i], 0.6, image_result, 0.4, 0)
            #     # image_result = cv2.addWeighted(ori_img, 0.6, image_result, 0.4, 0)

            
            image_result  = cv2.addWeighted(ori_img[img_id], 0.2, image_result, 0.8, 0)  # if ori_img_in is not None:

        

            cv2.imwrite(os.path.join(base_dir, '{}_{}.jpg'.format(name, img_id)), image_result)

    def error_map(self, im, pred, gt):
        canvas = im.copy()
        canvas[np.where((gt - pred != [0, 0, 0]).all(axis=2))] = [0, 0, 0]
        pred[np.where((gt - pred == [0, 0, 0]).all(axis=2))] = [0, 0, 0]
        canvas = cv2.addWeighted(canvas, 1.0, pred, 1.0, 0)
        # canvas = cv2.addWeighted(im, 0.3, canvas, 0.7, 0)
        canvas[np.where((gt == [0, 0, 0]).all(axis=2))] = [0, 0, 0]
        return canvas
