##+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
## Implementation of PKLNet
## Created by: Xu Liang
## Harbin Institute of Technology, Shenzhen
## xuliangcs@gmail.com
## Copyright (c) 2022
##+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import os
import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable


from lib.models.backbones.backbone_selector import BackboneSelector
from lib.models.tools.module_helper import ModuleHelper

from lib.models.modules.spatial_ocr_block import SpatialGather_Module, SpatialOCR_Module

from lib.models.backbones.hrt.hrt_backbone_palm import HRTBackbone
from lib.models.backbones.hrt.modules.transformer_block_palm import GeneralTransformerBlock, GeneralTransformerBlock_Palm

import lib.models.nets.dsntnn as dsntnn


class bre_module(nn.Module):
    '''
    The OCR (object context representation) is utilized here.
    '''
    def __init__(self, in_channels, NUM_CLS=3, DIM=-1):
        super(bre_module, self).__init__()
        self.num_classes = NUM_CLS
        self.in_channels = in_channels
        if DIM > 0:
            self.DIM = DIM #128 #64 #256 #512 ##############
        else:
            self.DIM = in_channels 

        self.conv3x3 = nn.Sequential(
            nn.Conv2d(self.in_channels, self.DIM, kernel_size=3, stride=1, padding=1),
            ModuleHelper.BNReLU(self.DIM, bn_type='torchbn'),#'torchsyncbn'
        )
        self.ocr_gather_head = SpatialGather_Module(self.num_classes)
        self.ocr_distri_head = SpatialOCR_Module(
            in_channels=self.DIM, # feat channels
            key_channels=self.DIM//2, # class channels
            out_channels=self.DIM,
            scale=1,
            dropout=0.05,
            bn_type='torchbn',
        )
        self.cls_head = nn.Conv2d(
            self.DIM, self.num_classes, kernel_size=1, stride=1, padding=0, bias=True
        )
        self.aux_head = nn.Sequential(
            nn.Conv2d(in_channels, self.DIM, kernel_size=3, stride=1, padding=1),
            ModuleHelper.BNReLU(self.DIM, bn_type='torchbn'),
            nn.Conv2d(
                self.DIM, self.num_classes, kernel_size=1, stride=1, padding=0, bias=True
            ),
        ) 
    
    def forward(self, xi):
        '''
        BRE cube segmentation based on OCR
        '''
        seg_aux = self.aux_head(xi)
        pix_feats = self.conv3x3(xi)
        context = self.ocr_gather_head(pix_feats, seg_aux) # (pix_reps+region->region reps)=>context
        z_ = self.ocr_distri_head(pix_feats, context) # g(.)
        seg_ocr = self.cls_head(z_) # phi

        return seg_aux, seg_ocr



class kcr_module(nn.Module):
    ''' 
    Implementation of the key point coordinates regression (KCR) head
    INPUT_IMG_SIZE: (H, W)
    W: width of the input image
    H: height of the input image
    KP_NUM: number of keypoints

    '''
    # def __init__(self, NUM_KP=2+4):  # ROI
    def __init__(self, NUM_KP=2+1): # ROI center
        super(kcr_module, self).__init__()
    
        self.INPUT_IMG_SIZE = None
        self.KP_NUM = NUM_KP

        self.BRE_CH = 6

        self.channel_wise_softmax = nn.Softmax(dim=1)

        self.s = nn.Parameter(torch.FloatTensor([0]))


        # self.kp_head_preprocessing = nn.Sequential(
        #     GeneralTransformerBlock(inplanes=6, planes=6, num_heads=3, window_size=7),
        #     GeneralTransformerBlock(inplanes=6, planes=6, num_heads=3, window_size=7),
        #     GeneralTransformerBlock(inplanes=6, planes=6, num_heads=3, window_size=7)
        # )


        # Spatial transformer network: localization
        self.localization = nn.Sequential(     
            nn.AvgPool2d(2, stride=2),

            nn.BatchNorm2d(self.BRE_CH), ############ 

            nn.Conv2d(self.BRE_CH, 16, kernel_size=3), ############       
            nn.MaxPool2d(2, stride=2),
            nn.BatchNorm2d(16),
            nn.ReLU(True),
            nn.Conv2d(16, 64, kernel_size=5),#32
            nn.MaxPool2d(2, stride=2),
            nn.BatchNorm2d(64),
            nn.ReLU(True),
            nn.Conv2d(64, 64, kernel_size=5),
            nn.MaxPool2d(2, stride=2),
            nn.BatchNorm2d(64),
            nn.ReLU(True)
        )     

        self.fc_loc = nn.Sequential(   
            nn.Linear(64*21*15, 128), ###################
            nn.ReLU(True),
            nn.Linear(128, 3 * 2) # Regressor for the 3 * 2 affine matrix
        )     

        # Initialize the weights/bias with identity transformation: IMPORTANT!!!
        # 1,0,0
        # 0,1,0
        self.fc_loc[2].weight.data.zero_()
        self.fc_loc[2].bias.data.copy_(torch.tensor([1, 0, 0, 0, 1, 0], dtype=torch.float))
        self.fixed_theta = torch.tensor([1, 0, 0, 0, 1, 0], dtype=torch.float)###########


        self.v = torch.ones((3,1))

        # FC-based coordinates regression
        self.kp_head = nn.Sequential(
            nn.AvgPool2d(kernel_size=2, stride=2, padding=0),
            ModuleHelper.BNReLU(self.BRE_CH, bn_type='torchbn'),
            # GeneralTransformerBlock_Palm(inplanes=self.BRE_CH, planes=1+self.KP_NUM*2, num_heads=3, window_size=7) # output ##################
            GeneralTransformerBlock_Palm(inplanes=self.BRE_CH, planes=self.KP_NUM*2, num_heads=3, window_size=7) # output ##################

            # GeneralTransformerBlock_Palm(inplanes=self.BRE_CH, planes=self.KP_NUM*2, num_heads=2, window_size=7) # output ##################
            # GeneralTransformerBlock_Palm(inplanes=self.BRE_CH, planes=self.KP_NUM*2, num_heads=2, window_size=7) # output ##################

        )

        # HM-based coordinates regression
        self.PPU = nn.Sequential(
            # GeneralTransformerBlock(inplanes=6, planes=6, num_heads=6, window_size=3), 
            # GeneralTransformerBlock(inplanes=6, planes=6, num_heads=3, window_size=3), 
            # GeneralTransformerBlock(inplanes=6, planes=6, num_heads=2, window_size=3), 
            # GeneralTransformerBlock(inplanes=6, planes=6, num_heads=1, window_size=3), 

            # GeneralTransformerBlock(inplanes=9, planes=9, num_heads=1, window_size=5), 
            # GeneralTransformerBlock(inplanes=9, planes=9, num_heads=1, window_size=5), 

            GeneralTransformerBlock(inplanes=self.BRE_CH, planes=self.BRE_CH, num_heads=3, window_size=7), 
            # GeneralTransformerBlock(inplanes=self.BRE_CH, planes=self.BRE_CH, num_heads=2, window_size=7), 
            # GeneralTransformerBlock(inplanes=self.BRE_CH, planes=self.BRE_CH, num_heads=self.BRE_CH, window_size=7), 
            # GeneralTransformerBlock(inplanes=self.BRE_CH, planes=self.BRE_CH, num_heads=self.BRE_CH, window_size=7), 
            # GeneralTransformerBlock(inplanes=3, planes=3, num_heads=3, window_size=7), 
            # GeneralTransformerBlock(inplanes=6, planes=6, num_heads=3, window_size=7), 
            # GeneralTransformerBlock(inplanes=6, planes=6, num_heads=3, window_size=7), 

            # nn.BatchNorm2d(3),    
            # nn.Conv2d(3, 64, kernel_size=3, stride=1,padding=1), 
            # nn.BatchNorm2d(64),   
            # nn.ReLU(),
            # nn.AvgPool2d(kernel_size=2, stride=2),
            # nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),    
            # nn.BatchNorm2d(128),    
            # nn.ReLU(),            
            # nn.AvgPool2d(kernel_size=2, stride=2),
            # nn.Conv2d(128, self.KP_NUM, kernel_size=3, stride=1, padding=1) 

        ) # postprocessing unit

        # self.hm = nn.Sequential(                 
        #     nn.BatchNorm2d(6),    
        #     nn.Conv2d(6, 36, kernel_size=1, stride=1),    
        #     nn.ReLU(),
        #     nn.Conv2d(36, self.KP_NUM, kernel_size=1, bias=False) ####################
        # )
        self.hm = nn.Sequential(                 
            nn.BatchNorm2d(6),    
            nn.Conv2d(6, 36, kernel_size=1, stride=1),    
            nn.ReLU(),
            nn.Conv2d(36, self.KP_NUM, kernel_size=1, bias=False) ####################
        )

        # self.hm = nn.Sequential(                 
        #     nn.BatchNorm2d(6),    
        #     nn.Conv2d(6, 36, kernel_size=1, stride=1), 
        #     nn.BatchNorm2d(36),   
        #     nn.ReLU(),
        #     nn.Conv2d(36, 36, kernel_size=1, stride=1),    
        #     nn.BatchNorm2d(36),    
        #     nn.ReLU(),
        #     nn.Conv2d(36, self.KP_NUM, kernel_size=1, bias=False) ####################
        # )

        # self.hm = nn.Sequential(                 
        #     # nn.BatchNorm2d(self.BRE_CH),    
        #     # nn.Conv2d(self.BRE_CH, 36, kernel_size=1, stride=1),    
        #     # nn.ReLU(),
        #     nn.Conv2d(self.BRE_CH, self.KP_NUM, kernel_size=1, bias=False) ####################
        # )

    def bre_expend(self, x):
        x_ = self.channel_wise_softmax(x)
        x = torch.cat((x, x_), dim=1)
        return x

    # def bre_prepro(self, x):
    #     x_ = self.channel_wise_softmax(x)
    #     x = x + x_
    #     return x


    def stn(self, x):
        '''
        Spatial transformer network forward function
        '''
        xs = self.localization(x)      

        xs = xs.view(-1, 64*21*15) #(9*5), for the FC layer  ##########################################################

        theta = self.fc_loc(xs)
        # theta = self.fixed_theta.expand([x.size(0), 6]).to(x.device) ##################

        theta = theta.view(-1, 2, 3)

        b,c,h,w = x.size()

        grid = F.affine_grid(theta, (b, c, h//2, w//2)) # size of the output feature image; h//2:small image ##########

        x = F.grid_sample(x, grid) 
        return x, theta

    
 
    def affineCoord(self, x, y, M):
        '''
        affine coordinates (x,y) using the given transformation matrix M
        ''' 
        v = self.v # v = torch.ones((3,1), device=M.device) #.to(M.device)
        v[0, 0] = x
        v[1, 0] = y
        v[2, 0] = 1
        return torch.matmul(M, v)


    def kp_coord(self, kp, M, W, H):
        '''
        invert warpping: 
        coordinate system from STN feature map to the input palm image
        '''
        b,d = kp.size()             # b:batch; d:number_of_keypoints
        x = kp[:, :-1:2].reshape(-1)   # xs    #.view(-1)
        y = kp[:, 1::2].reshape(-1)    # ys
        z = torch.ones_like(x)      # zs

        xyz = torch.stack((x, y, z), dim=0) # [xs;ys;zs], 2D tensor
        xyz = torch.split(xyz, d//2, dim=1) # ([xs_b1;ys_b1;zs_b1], [xs_b2;ys_b2;zs_b2], ... [batch size]), a list of 2D tensors
        xyz = torch.stack(xyz, dim=0)       # 3D tensors (batch sample id, xyz id, keypoint id), new batch structure:
        '''
        sample-1:
        x1, x2, ...;
        y1, y2, ...;
        1,  1,  ...;

        sample-2:
        x1, x2, ...;
        y1, y2, ...;
        1,  1,  ...;
        ...
        '''
        o = torch.matmul(M, xyz) # Here, each image corresponds to one theta matrix; Coordinates range: [-1~0~+1]
        o = torch.transpose(o, dim0=1, dim1=2) # 3D tensors, (batch_id, xyz_id, kp_id) ---> (batch_id, kp_id, xyz_id)

        xys = torch.split(o, 1, dim=1) # a list: (kp1:[batch_id, 0, xyz_id], kp2:[batch_id, 0, xyz_id], ..., kpn:[batch_id, 0, xyz_id]); # print(xys[0].shape)
        kp = torch.cat(xys, dim=2).squeeze(1) # [bid, x1y1z1x2y2z2...xnynzn]

        # t = torch.Tensor([W/2., H/2.0], device=kp.device).repeat((kp.size(0), d//2)) 
        t = torch.Tensor([W/2., H/2.0]).repeat((kp.size()[0], d//2)).to(kp.device)

        pixel_coords = kp * t + t # [0, W], [0, H]

        return pixel_coords


    def forward(self, seg, INPUT_IMG_SIZE):

        (H, W) = INPUT_IMG_SIZE
        self.INPUT_IMG_SIZE = INPUT_IMG_SIZE

        # V = self.bre_prepro(seg) # V=seg
        V = self.bre_expend(seg) # V=seg

        stnmap, M_theta = self.stn(V)

        ## HM-based regression:
        post_feat = self.PPU(stnmap) # print(post_feat.shape)

        unnormalized_heatmaps = self.hm(post_feat)     
        heatmaps = dsntnn.flat_softmax(unnormalized_heatmaps)
        coords = dsntnn.dsnt(heatmaps)

        # normalization: from dsntnn to stn
        coords[:,:,0] = coords[:,:,0]/(1-1./heatmaps.size(2)) # h, y
        coords[:,:,1] = coords[:,:,1]/(1-1./heatmaps.size(3)) # w, x

        kp = coords.reshape(coords.size(0), -1)

        kp_coords_hm = self.kp_coord(kp, M_theta, W, H)

        ## FC-based regression:

        ## dynamic fusion weight scheme:
        # fc_out = self.kp_head(stnmap) #(post_feat)
        # ws = fc_out[:,0].unsqueeze(dim=1)
        # weight = 1.0 / (1 + torch.exp(-self.s*ws))
        # w = weight.repeat((1, self.KP_NUM*2))
        # kp_fc = fc_out[:,1:]

        kp_fc = self.kp_head(stnmap) #(post_feat)

        kp_coords_fc = self.kp_coord(kp_fc, M_theta, W, H)

              
        ## fixed learnable weight scheme:
        w = 1.0 / (1 + torch.exp(-self.s))

        ## fixed weight scheme:   !!!
        w_ = 0.5
        # # w_ = 0.2
        # # w_ = 0.8
        # # w_ = 1
        # # w_ = 0

        kp_coords = (1-w_) * kp_coords_hm + w_ * kp_coords_fc 

        # kp_coords = (1-w) * kp_coords_hm + w * kp_coords_fc 


        return kp_coords, V, stnmap, post_feat, heatmaps, w



class pklnet(nn.Module):
    # def __init__(self, configer=None, NUM_KP=2+4, NUM_CLS=3): # ROI
    def __init__(self, configer=None, NUM_KP=2+1, NUM_CLS=3): # ROI center
        super(pklnet, self).__init__()
        # self.configer = configer
             
        # backbone
        self.backbone = HRTBackbone()()

        # in_channels = 160 # 32+64+64
        # in_channels = 480 # 32+64+128+256
        in_channels = 224 #32+64+64+64##################################################  
        
        self.bre_segment = bre_module(in_channels, NUM_CLS)
        self.kcr = kcr_module(NUM_KP)          

    def forward(self, x_):
        batch, _, H, W = x_.size()
        self.INPUT_IMG_SIZE = (H, W)

        x = self.backbone(x_)

        batch, _, h, w = x[0].size()


        feat1 = x[0] # 
        feat2 = F.interpolate(x[1], size=(h, w), mode="bilinear", align_corners=True)
        feat3 = F.interpolate(x[2], size=(h, w), mode="bilinear", align_corners=True)
        feat4 = F.interpolate(x[3], size=(h, w), mode="bilinear", align_corners=True) 
      

        xi = torch.cat([feat1, feat2, feat3, feat4], 1)
        # xi = torch.cat([feat1, feat2, feat3], 1) # lite version
        
        seg_aux, seg = self.bre_segment(xi)

        seg_aux = F.interpolate(
            seg_aux, size=(H, W), mode="bilinear", align_corners=True
        )
        seg = F.interpolate(
            seg, size=(H, W), mode="bilinear", align_corners=True
        )

        # feats = torch.cat([seg, seg_aux, conv_feat], dim=1)
        # feats = torch.cat([seg, seg_aux, phi], dim=1)
        # stnmap, kp_coords, heatmaps = self.kcrhead(feats)
        # stnmap, kp_coords, heatmaps = self.kcr(seg, W, H)

        phi = seg # BRE segment feature cube
        kp_coords, seg, stnmap, post_feat, heatmaps, weight = self.kcr(phi, self.INPUT_IMG_SIZE)
    
        return kp_coords, seg_aux, seg, stnmap, post_feat, heatmaps, weight




class FocalLoss(nn.Module):
    r"""
        This criterion is a implemenation of Focal Loss, which is proposed in 
        Focal Loss for Dense Object Detection.

            Loss(x, class) = - \alpha (1-softmax(x)[class])^gamma \log(softmax(x)[class])

        The losses are averaged across observations for each minibatch.

        Args:
            alpha(1D Tensor, Variable) : the scalar factor for this criterion
            gamma(float, double) : gamma > 0; reduces the relative loss for well-classiﬁed examples (p > .5), 
                                   putting more focus on hard, misclassiﬁed examples
            size_average(bool): By default, the losses are averaged over observations for each minibatch.
                                However, if the field size_average is set to False, the losses are
                                instead summed for each minibatch.


    """
    def __init__(self, class_num, alpha=None, gamma=2, size_average=True):
        super(FocalLoss, self).__init__()
        if alpha is None:
            self.alpha = Variable(torch.ones(class_num, 1))
        else:
            if isinstance(alpha, Variable):
                self.alpha = alpha
            else:
                self.alpha = Variable(alpha)
        self.gamma = gamma
        self.class_num = class_num
        self.size_average = size_average

    def forward(self, inputs, targets):
        N = inputs.size(0)
        C = inputs.size(1)
        P = F.softmax(inputs, dim=1)

        H = inputs.size(2)
        W = inputs.size(3)
        # print(inputs.shape)

        P = P.permute(0,2,3,1).reshape(-1, C)
   

        class_mask = inputs.data.new(N*W*H, C).fill_(0)
        class_mask = Variable(class_mask)

        target = self._scale_target(targets, (inputs.size(2), inputs.size(3)))
        # print(target.shape)
        ids = target.view(-1, 1)

        # ignore class: -1
        ids[ids<0]=0
        
        class_mask.scatter_(1, ids.data, 1.)


        if inputs.is_cuda and not self.alpha.is_cuda:
            self.alpha = self.alpha.cuda()

        alpha = self.alpha[ids.data.view(-1)]


        probs = (P*class_mask).sum(1).view(-1,1)


        log_p = probs.log()
        # print('probs size= {}'.format(probs.size()))
        # print(probs)
     
        batch_loss = -alpha*(torch.pow((1-probs), self.gamma))*log_p 
        # print('-----bacth_loss------')
        # print(batch_loss)

        if self.size_average:
            loss = batch_loss.mean()
        else:
            loss = batch_loss.sum()
        return loss

    @staticmethod
    def _scale_target(targets_, scaled_size):
        targets = targets_.clone().unsqueeze(1).float()
        targets = F.interpolate(targets, size=scaled_size, mode='nearest')
        return targets.squeeze(1).long()


class SegFocalLoss(nn.Module):
    def __init__(self, class_num, alpha=None, gamma=2, size_average=True):
        super(SegFocalLoss, self).__init__()
        self.focal_loss = FocalLoss(class_num=class_num, alpha=alpha, gamma=gamma, size_average=size_average)

    def forward(self, inputs, targets, **kwargs):
        aux_out, seg_out = inputs
        # print(aux_out.shape, seg_out.shape)
        seg_loss = self.focal_loss(seg_out, targets)
        # print('seg_loss: ', seg_loss)
        aux_loss = self.focal_loss(aux_out, targets)
        # print('axu_loss: ', aux_loss)
        # loss = 1.0 * seg_loss + 1.0 * aux_loss ##############################
        loss = 1.0 * seg_loss + 0.5 * aux_loss
        return loss



# Cross-entropy Loss
class FSCELoss(nn.Module):
    def __init__(self, weights = None):
        super(FSCELoss, self).__init__()

        weight = None 
        reduction = 'mean'#'elementwise_mean'       
        ignore_index = -1    

        self.ce_loss = nn.CrossEntropyLoss(weight=weight, ignore_index=ignore_index, reduction=reduction)

    def forward(self, inputs, *targets, weights=None, **kwargs):
        loss = 0.0
        if isinstance(inputs, tuple) or isinstance(inputs, list):
            if weights is None:
                weights = [1.0] * len(inputs)
                
            for i in range(len(inputs)):
                if len(targets) > 1:
                    target = self._scale_target(targets[i], (inputs[i].size(2), inputs[i].size(3)))
                    loss += weights[i] * self.ce_loss(inputs[i], target)
                else:
                    target = self._scale_target(targets[0], (inputs[i].size(2), inputs[i].size(3)))
                    loss += weights[i] * self.ce_loss(inputs[i], target)

        else: # this branch
            target = self._scale_target(targets[0], (inputs.size(2), inputs.size(3)))
            
            loss = self.ce_loss(inputs, target)

            # print(target.shape, inputs.shape, target.max(), loss.item())

        return loss

    @staticmethod
    def _scale_target(targets_, scaled_size):
        targets = targets_.clone().unsqueeze(1).float()
        targets = F.interpolate(targets, size=scaled_size, mode='nearest')
        return targets.squeeze(1).long()



class FSAuxCELoss(nn.Module):
    def __init__(self, weights=None):
        super(FSAuxCELoss, self).__init__()
        self.weights = weights
        self.ce_loss = FSCELoss(weights=self.weights)

    def forward(self, inputs, targets, **kwargs):
        aux_out, seg_out = inputs
        # print(aux_out.shape, seg_out.shape)
        seg_loss = self.ce_loss(seg_out, targets)
        # print('seg_loss: ', seg_loss)
        aux_loss = self.ce_loss(aux_out, targets)
        # print('axu_loss: ', aux_loss)

        # loss = 1.0 * seg_loss + 0.4 * aux_loss
        # loss = 0.4 * seg_loss + 1.0 * aux_loss
        # loss = 0.0 * seg_loss + 1.0 * aux_loss
        # loss = 1.0 * seg_loss + 0.2 * aux_loss # bad
        # loss = 1.0 * seg_loss + 1.0 * aux_loss
        # loss = 1.0 * seg_loss + 0.5 * aux_loss
        # loss = 1.0 * seg_loss + 0.8 * aux_loss

        loss = 1.0 * seg_loss + 0.5 * aux_loss

        return loss


class EdgeAwareLoss(nn.Module):
    r"""Implement of edge aware loss::
        Args:
            kpNum: edge keypoints around one finger valley keypoint (20+20+1=41)
      
        """
    def __init__(self, kpNum):
        super(EdgeAwareLoss, self).__init__()
        # self.in_features = in_features
        # self.out_features = out_features
        # self.s = s
        self.kpNum = kpNum

        # self.weight = Parameter(torch.ones(1, self.kpNum))
        # self.maxpool = nn.MaxPool1d(self.kpNum, padding = 0)
       

    def forward(self, input, target):              
        # w = torch.ones(1, self.kpNum)
        # print(target.shape)
        # edge1 = target[:, :self.kpNum*2]
        # edge2 = target[:, self.kpNum*2:]
        # print(edge1.shape, edge2.shape)
        # e1x = edge1[:, :-1:2]
        # e1y = edge1[:, 1::2]
        # e2x = edge2[:, :-1:2]
        # e2y = edge2[:, 1::2]
        # print(e1x.shape)
        # edgea = torch.cat((e1x, e1y), axis=1)
        # edgeb = torch.cat((e2x, e2y), axis=1)
        # print(edgea.shape, edgeb.shape)
        # xy = torch.split(input, 1, dim=1) 
        # edge = edge.repeat((b, 1))
        a = input[:, :2].repeat((1, self.kpNum))
        # print(a.shape)
        b = input[:, 2:4].repeat((1, self.kpNum))
        # print(b.shape)
        # print(input[:, 0].view(-1, 1).repeat((1, self.kpNum)).shape)
        c = torch.cat((a,b), dim=1)
        # print(c.shape, target.shape)
        edge = target        
        dis = c - edge
        # print(dis)
        dis2 = torch.pow(dis, 2)
        # print(dis2)
        dx = dis2[:, :-1:2]
        dy = dis2[:, 1::2]
        # print(d)
        # d = torch.sqrt(dx + dy)
        d = dx+dy
        # print(d.shape, d)
        
        dmin1, idx1 = torch.min(d[:,:self.kpNum], dim=1)
        dmin2, idx2 = torch.min(d[:,self.kpNum:], dim=1)

        # dmin1 = torch.sqrt(dmin1)
        # dmin2 = torch.sqrt(dmin2)

        # print(dmin1)
        # print('dmin1.size(): ',dmin1.size())
        # dmin = -self.maxpool(-d.view(-1, 2, self.kpNum)).view(-1, 2)
        # print(dmin.shape, dmin)

        # loss = torch.sum(dmin)/input.size()[0]/2.0
        # loss = torch.sum((dmin[:, 1]))/input.size()[0]/2.
        loss = (torch.sum(dmin1)+torch.sum(dmin2))/input.size(0)/2. # 4.

        # print(dmin.shape, loss.shape)

        return loss, idx1, idx2

        
class LocScaleLoss(nn.Module):
    r"""Implement of location-scale loss::
        Args:
            imgSize: W, H

        (not used)
        """
    def __init__(self, imgSize=(150, 200), centerTH=20, lenTH1=100, lenTH2 = 110):
    # def __init__(self, imgSize=(150, 200), centerTH=50, lenTH1=100, lenTH2 = 130):
        super(LocScaleLoss, self).__init__()
        self.imgSize = imgSize  
        self.centerTH = centerTH
        self.lenTH1 = lenTH1
        self.lenTH2 = lenTH2      

    def forward(self, input):        
        # dis = torch.sqrt(torch.norm((input[:, :2]-input[:, 2:]), p=2, keepdim=False))
        dis = (torch.norm((input[:, :2]-input[:, 2:]), p=2, keepdim=False))

        center = (input[:,:2]+input[:,2:])/2.0
        anchor = torch.tensor([self.imgSize[0]/2.0, self.imgSize[1]/2]).repeat((input.size()[0], 1)).to(input.device)        
        # center_dis = torch.sqrt(torch.norm((center-anchor), p=2, keepdim=False))
        center_dis = (torch.norm((center-anchor), p=2, keepdim=False))
        
        disloss1 = torch.mean(torch.clamp(self.lenTH1 - dis, min=0.0))
        disloss2 = torch.mean(torch.clamp(dis - self.lenTH2, min=0.0))
        disloss = disloss1 + disloss2

        cenloss = torch.mean(torch.clamp(center_dis - self.centerTH, min=0.0))

        # return (disloss)
        # return (cenloss)
        return (disloss+cenloss)/2.0